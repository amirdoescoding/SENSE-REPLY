"""Daily agent: memory of good days (k-NN, no training) + one Gemini call per day that sets the knobs.

Gemini is a capability stand-in for Devstral 2, not a proposal. REST via urllib, key from .env GEMINI_API_KEY.
Answers are cached in demo/out/gemini_cache.json (committed) so the hosted demo replays them without a key.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from itertools import product
from pathlib import Path

from sim import ROOT, day_score, default_knobs, load_run, rule_flows, run_day
from timeseries import soc0_of  # on sys.path via sim

# 3.8/3.6 Flash free tier = 20 requests/day; a full run needs 42 calls. Flash-Lite allows 500/day (2026-11-18).
MODEL = "gemini-3.5-flash-lite"
OUT = Path(__file__).resolve().parent / "out"
CACHE = OUT / "gemini_cache.json"
MEMORY = OUT / "memory.json"
RANGES = {"soc_floor": (0.10, 0.50), "evening_reserve_kwh": (0.0, 8.0), "export_hold_eur": (0.0, 0.20)}
# Small grid for the hindsight seed (each set costs one 96-step rolling MPC per day)
GRID = {"soc_floor": (0.10, 0.20), "evening_reserve_kwh": (0.0, 3.0, 6.0), "export_hold_eur": (None, 0.12)}
GRID_GC = (None, {"from": 0, "to": 6})
QUOTA_HIT = False


def _key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    env = ROOT / ".env"
    for line in env.read_text().splitlines() if env.exists() else []:
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    return None


def context(rows, start, soc0, ci):
    """What the agent and the k-NN see about a day (only data known at its start, prices day-ahead)."""
    prev = rows[start - 96:start] if start >= 96 else rows[start + 96:start + 192]
    day = rows[start:start + 96]
    buy = [r["grid"]["buyPrice"] for r in day]
    cis = [ci(r["dt"]) for r in prev]
    return dict(pv_yday=round(sum(r["pv"] for r in prev), 2), load_yday=round(sum(r["load"] for r in prev), 2),
                price_spread=round(max(buy) - min(buy), 4), co2_spread=round(max(cis) - min(cis), 1),
                soc0=round(soc0, 3))


def validate(raw, mode, mean_buy):
    """Schema check + clamp. Returns (knobs, notes). Missing or non-numeric fields fall back to defaults."""
    knobs, notes = default_knobs(mode, mean_buy), []
    for k, (lo, hi) in RANGES.items():
        v = raw.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            notes.append(f"{k} missing/invalid -> default")
            continue
        if not lo <= v <= hi:
            notes.append(f"{k} {v} clamped to [{lo}, {hi}]")
        knobs[k] = round(min(max(float(v), lo), hi), 4)
    gc = raw.get("grid_charge")
    if mode == "conservative":
        if gc:
            notes.append("grid_charge removed (conservative mode)")
        knobs["grid_charge"] = None
    elif gc is None:
        knobs["grid_charge"] = None
    elif isinstance(gc, dict) and all(isinstance(gc.get(x), int) and 0 <= gc[x] <= 24 for x in ("from", "to")):
        knobs["grid_charge"] = {"from": gc["from"], "to": gc["to"]}
    else:
        notes.append("grid_charge invalid -> default")
    return knobs, notes


def seed_memory(ci, modes=("conservative", "upside"), lam=0.10):
    """Hindsight grid search on the 14 logged days of A and C: per day and mode, the knob set with the lowest
    € + λ·kg under the rolling MPC (persistence forecast), and its regret vs the static rule.
    Same week as the test: this leaks, and is flagged. Cached in demo/out/memory.json."""
    if MEMORY.exists():
        return json.loads(MEMORY.read_text())
    mem = []
    for run in ("A", "C"):
        rows = load_run(run)
        mean_buy = sum(r["grid"]["buyPrice"] for r in rows) / len(rows)
        for day in range(len(rows) // 96):
            start = day * 96
            soc0 = rows[start - 1]["bess"]["soc"] if start else soc0_of(rows)
            ctx = context(rows, start, soc0, ci)
            day_rows = rows[start:start + 96]
            r_score = day_score(day_rows, rule_flows(day_rows, soc0), lam)[0]
            for mode in modes:
                best = None
                for fl, res, hold, gc in product(*GRID.values(), GRID_GC if mode == "upside" else (None,)):
                    k = dict(soc_floor=fl, evening_reserve_kwh=res, grid_charge=gc,
                             export_hold_eur=round(mean_buy, 4) if hold is None else hold)
                    sc = day_score(day_rows, run_day(rows, start, soc0, k, mode, lam, ci), lam)[0]
                    if best is None or sc < best[0]:
                        best = (sc, k)
                mem.append(dict(run=run, day=day, mode=mode, context=ctx, knobs=best[1],
                                score=round(best[0], 4), regret_vs_rule=round(best[0] - r_score, 4)))
                print(f"memory {run} day {day} {mode}: {best[1]} regret {best[0] - r_score:+.3f}")
    OUT.mkdir(exist_ok=True)
    MEMORY.write_text(json.dumps(mem, indent=1))
    return mem


def nearest(mem, ctx, mode, k=3, exclude=None):
    """k most similar memory days (z-scored context, Euclidean). exclude=(run, day) to skip."""
    pool = [m for m in mem if m["mode"] == mode and (m["run"], m["day"]) != exclude]
    keys = list(ctx)
    sd = {x: (sum((m["context"][x] - sum(p["context"][x] for p in pool) / len(pool)) ** 2 for m in pool)
              / len(pool)) ** 0.5 or 1 for x in keys}
    dist = lambda m: sum(((m["context"][x] - ctx[x]) / sd[x]) ** 2 for x in keys) ** 0.5
    return sorted(pool, key=dist)[:k]


def prompt(ctx, prices, co2_fc, mode, lam, neighbours):
    return f"""You plan tomorrow for a home battery (10 kWh, SoC 0.10-0.90, 5 kW, 95% efficiency each way) with
9 PV panels, in Italy (assumed). You do NOT set kW: a rolling optimiser does that every 15 minutes, minimising
€ + λ·kg CO2 with a 24 h "same as yesterday" forecast. You set 3-4 daily knobs that protect it from forecast error.

Knobs:
- soc_floor (0.10-0.50): lowest SoC the optimiser may plan.
- evening_reserve_kwh (0-8): energy that must be in the battery at 17:00 for the expensive evening.
- export_hold_eur (0-0.20 €/kWh): value of a stored kWh; midday solar is sold only if the price beats it.
- grid_charge: null, or {{"from": h, "to": h}} hours when charging from the grid is allowed. Mode "{mode}"
  {"forbids grid charging: use null." if mode == "conservative" else "allows it (shadow mode)."}

Today: mode={mode}, λ={lam} €/kg CO2.
Context: {json.dumps(ctx)}
Hourly buy prices tomorrow (€/kWh, day-ahead, 24 values from 11:00): {prices}
Hourly grid CO2 forecast (g/kWh, persistence): {co2_fc}
Most similar past days, with the knobs that worked best in hindsight and their regret vs a plain rule
(negative = beat the rule): {json.dumps([dict(context=n["context"], knobs=n["knobs"], regret=n["regret_vs_rule"]) for n in neighbours])}

Answer JSON only: {{"soc_floor": x, "evening_reserve_kwh": x, "export_hold_eur": x, "grid_charge": null or
{{"from": h, "to": h}}, "explanation": "2-3 plain sentences for the home owner: what you chose and why"}}"""


def ask(text, live=False, on_wait=None):
    """One Gemini call (cached by prompt hash). Returns dict(raw, explanation, thoughts, tok_in, tok_out, source)
    or None when no key / API error (caller falls back to memory).
    live=True: no cache read or write (the prompts are deterministic, so the cache would replay every answer);
    on_wait(msg) hears about 503 back-offs."""
    global QUOTA_HIT
    cache = {} if live else json.loads(CACHE.read_text()) if CACHE.exists() else {}
    h = hashlib.sha256((MODEL + text).encode()).hexdigest()[:16]
    if h in cache:
        return cache[h]
    key = _key()
    if not key or QUOTA_HIT:
        return None
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseMimeType": "application/json", "thinkingConfig": {"includeThoughts": True, "thinkingBudget": 2048}}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    t0 = time.monotonic()
    for wait in (10, 30, 60, None):  # 503 "high demand" / 429 are common on the free tier: back off, then give up
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            break
        except (urllib.error.URLError, TimeoutError) as e:  # key never in the message: it is a header
            code = getattr(e, "code", None)
            print(f"gemini error: {code} {getattr(e, 'reason', e)}", flush=True)
            if code == 429:  # daily quota gone: no point retrying today; the rest of the run uses memory
                QUOTA_HIT = True
                return None
            if wait is None or code not in (500, 503):
                return None
            if on_wait:
                on_wait(f"{code} · retry in {wait} s")
            time.sleep(wait)
    parts = d["candidates"][0]["content"]["parts"]
    answer = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    try:
        raw = json.loads(answer)
    except json.JSONDecodeError:
        raw = {}
    u = d.get("usageMetadata", {})
    out = dict(raw=raw, explanation=str(raw.get("explanation", "")),
               thoughts="".join(p.get("text", "") for p in parts if p.get("thought")),
               tok_in=u.get("promptTokenCount", 0), tok_out=u.get("candidatesTokenCount", 0)
               + u.get("thoughtsTokenCount", 0), source="gemini", model=MODEL)
    if live:
        return out | dict(ms=round((time.monotonic() - t0) * 1000))
    cache[h] = out
    OUT.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1))
    return out


def propose(rows, start, soc0, ci, mode, lam, mem, live=False, on_wait=None):
    """Gemini's knobs for the day at `start`, else 'copy the most similar good day' (memory fallback)."""
    ctx = context(rows, start, soc0, ci)
    nb = nearest(mem, ctx, mode, exclude=("C", start // 96))
    day = rows[start:start + 96]
    prev = rows[start - 96:start] if start >= 96 else rows[start + 96:start + 192]
    prices = [round(day[i]["grid"]["buyPrice"], 4) for i in range(0, len(day), 4)]
    co2 = [round(ci(prev[i]["dt"])) for i in range(0, len(prev), 4)]
    ans = ask(prompt(ctx, prices, co2, mode, lam, nb), live, on_wait)
    if ans is None:
        good = min(nb, key=lambda m: m["regret_vs_rule"])
        return dict(raw=dict(good["knobs"]), explanation=f"No model answer: copied the knobs of the most similar "
                    f"logged day ({good['run']} day {good['day'] + 1}).", thoughts="", tok_in=0, tok_out=0,
                    source="memory"), ctx, nb
    return ans, ctx, nb


if __name__ == "__main__":
    from carbon import ci_lookup
    ci = ci_lookup()[0]
    k, notes = validate({"soc_floor": 0.9, "evening_reserve_kwh": "lots", "grid_charge": {"from": 1, "to": 5}},
                        "conservative", 0.1)
    assert k["soc_floor"] == 0.5 and k["evening_reserve_kwh"] == 0 and k["grid_charge"] is None and len(notes) == 4
    print("validator ok")
    seed_memory(ci)
