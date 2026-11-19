"""Replay the demo's daily agent with a LOCAL open-weight model (llama.cpp llama-server) instead of Gemini.

Same prompts, validator, replay gate and MPC as demo/sim.py: only agent.ask is swapped. Also runs the no-LLM
baseline ("copy the most similar good day", agent.ask -> None) so the model has to beat memory to earn its place.

  llama-server -m ~/models/<model>.gguf -c 8192 --port 8080   # one model at a time
  .venv/bin/python demo/local_bench.py --name ministral-3-8b  # appends to demo/out/local_bench.json
  .venv/bin/python demo/local_bench.py --name memory --memory  # baseline, no server needed
"""
import argparse
import json
import time
import urllib.request

import agent
import sim

MODES = ("conservative", "upside")
LAM = 0.10
OUT = agent.OUT / "local_bench.json"


def local_ask(url):
    def ask(text, live=False, on_wait=None):
        body = {"messages": [{"role": "user", "content": text}], "temperature": 0.2,
                "response_format": {"type": "json_object"},  # any JSON; field checks are the validator's job
                "chat_template_kwargs": {"enable_thinking": False}}
        req = urllib.request.Request(f"{url}/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=900) as r:
            d = json.load(r)
        ms = round((time.monotonic() - t0) * 1000)
        text_out = d["choices"][0]["message"]["content"]
        try:
            raw, ok = json.loads(text_out), True
        except json.JSONDecodeError:
            raw, ok = {}, False
        raw = raw if isinstance(raw, dict) else {}
        u, t = d.get("usage", {}), d.get("timings", {})
        return dict(raw=raw, explanation=str(raw.get("explanation", "")), thoughts="", source="gemini",  # counted as an LLM call
                    tok_in=u.get("prompt_tokens", 0), tok_out=u.get("completion_tokens", 0), ms=ms, json_ok=ok,
                    prefill_tps=t.get("prompt_per_second"), decode_tps=t.get("predicted_per_second"))
    return ask


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--url", default="http://127.0.0.1:8080")
    p.add_argument("--memory", action="store_true", help="no LLM: memory fallback only")
    a = p.parse_args()
    from carbon import ci_lookup
    ci, _, hours = ci_lookup()
    rows = sim.load_run("C")
    rule = sim.rule_flows(rows, 0.80)
    mem = agent.seed_memory(ci)
    calls = []
    if a.memory:
        agent.ask = lambda *_a, **_k: None
    else:
        inner = local_ask(a.url)

        def ask(text, live=False, on_wait=None):
            r = inner(text)
            calls.append({k: r[k] for k in ("tok_in", "tok_out", "ms", "json_ok", "prefill_tps", "decode_tps")})
            return r
        agent.ask = ask
    res = {}
    for mode in MODES:
        n0 = len(calls)
        f, days = sim.run_ours(rows, mode, LAM, ci, mem)  # not live: fixed A+C memory, like the precomputed Gemini run
        k, tok = sim.ours_kpis(rows, f, days, rule, ci if hours else None)
        gem = json.loads((agent.OUT / f"run_{mode}_{LAM}.json").read_text())
        c = calls[n0:]
        res[mode] = dict(
            S_net=round(k["S_net"], 4), VORB=round(k["VORB"], 4), S1_kg=round(k["S1"], 2),
            gemini_S_net=gem["kpis"]["S_net"], gemini_VORB=gem["kpis"]["VORB"],
            json_ok=sum(x["json_ok"] for x in c), calls=len(c),
            clamped_or_invalid=sum(bool(d["validator_notes"]) for d in days),
            gate_passed=sum(d["gate"]["passed"] for d in days), used=[d["used"] for d in days],
            knobs=[d["knobs"] for d in days], gemini_knobs=gem["knobs"],
            tok_in=tok["tok_in"], tok_out=tok["tok_out"],
            ms_mean=round(sum(x["ms"] for x in c) / len(c)) if c else 0,
            prefill_tps=round(sum(x["prefill_tps"] or 0 for x in c) / len(c), 1) if c else None,
            decode_tps=round(sum(x["decode_tps"] or 0 for x in c) / len(c), 1) if c else None,
            explanation_day1=days[0]["explanation"])
        r = res[mode]
        print(f"{a.name} {mode}: S_net {r['S_net']} (gemini {r['gemini_S_net']}) VORB {r['VORB']} "
              f"json {r['json_ok']}/{r['calls']} clamped {r['clamped_or_invalid']} gate {r['gate_passed']}/7 "
              f"tok {r['tok_in']}/{r['tok_out']} {r['ms_mean']} ms/call", flush=True)
    assert all(len(r["knobs"]) == 7 for r in res.values()), "a week is 7 plan windows"
    allres = json.loads(OUT.read_text()) if OUT.exists() else {}
    allres[a.name] = res
    OUT.write_text(json.dumps(allres, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
