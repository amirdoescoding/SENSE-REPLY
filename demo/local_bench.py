"""Replay the demo's daily agent with another LOCAL open-weight model (llama.cpp llama-server, same `agent.ask`).

Same prompts, validator, replay gate and MPC as demo/sim.py: only agent.ask is swapped. Also runs the no-LLM
baseline ("copy the most similar good day", agent.ask -> None) so the model has to beat memory to earn its place.

  llama-server -m ~/models/<model>.gguf -c 8192 --port 8080   # one model at a time
  .venv/bin/python demo/local_bench.py --name ministral-3-8b  # appends to demo/out/local_bench.json
  .venv/bin/python demo/local_bench.py --name memory --memory  # baseline, no server needed
"""
import argparse
import json

import agent
import sim

MODES = sim.MODES
LAM = 0.10
OUT = agent.OUT / "local_bench.json"


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
        agent.LLAMA_URL, agent.MODEL = a.url, a.name  # cache keyed by name: each bench model asks for real
        agent.CACHE = agent.OUT / "bench_cache.json"  # keep the demo's committed replay cache clean
        inner = agent.ask

        def ask(text):
            r = inner(text)
            calls.append({k: r[k] for k in ("tok_in", "tok_out", "ms", "json_ok", "prefill_tps", "decode_tps")})
            return r
        agent.ask = ask
    res = {}
    for mode in MODES:
        n0 = len(calls)
        f, days = sim.run_ours(rows, mode, LAM, ci, mem)  # fixed A+C memory, like the demo replay
        k, tok = sim.ours_kpis(rows, f, days, rule, ci if hours else None)
        rep = json.loads((agent.OUT / f"run_{LAM}.json").read_text())
        c = calls[n0:]
        res[mode] = dict(
            S_net=round(k["S_net"], 4), VORB=round(k["VORB"], 4), S1_kg=round(k["S1"], 2),
            replay_S_net=rep["kpis"]["S_net"], replay_VORB=rep["kpis"]["VORB"],
            json_ok=sum(x["json_ok"] for x in c), calls=len(c),
            clamped_or_invalid=sum(bool(d["validator_notes"]) for d in days),
            gate_passed=sum(d["gate"]["passed"] for d in days), used=[d["used"] for d in days],
            knobs=[d["knobs"] for d in days], replay_knobs=rep["knobs"],
            tok_in=tok["tok_in"], tok_out=tok["tok_out"],
            ms_mean=round(sum(x["ms"] for x in c) / len(c)) if c else 0,
            prefill_tps=round(sum(x["prefill_tps"] or 0 for x in c) / len(c), 1) if c else None,
            decode_tps=round(sum(x["decode_tps"] or 0 for x in c) / len(c), 1) if c else None,
            explanation_day1=days[0]["explanation"])
        r = res[mode]
        print(f"{a.name} {mode}: S_net {r['S_net']} (replay {r['replay_S_net']}) VORB {r['VORB']} "
              f"json {r['json_ok']}/{r['calls']} clamped {r['clamped_or_invalid']} gate {r['gate_passed']}/7 "
              f"tok {r['tok_in']}/{r['tok_out']} {r['ms_mean']} ms/call", flush=True)
    assert all(len(r["knobs"]) == 7 for r in res.values()), "a week is 7 plan windows"
    allres = json.loads(OUT.read_text()) if OUT.exists() else {}
    allres[a.name] = res
    OUT.write_text(json.dumps(allres, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
