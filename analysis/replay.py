"""Replay the proposal's knobs as rule variants on the real sun/load/prices of runs A and C. Stdlib only.

Run: python3 analysis/replay.py
Knobs (what the daily LLM would set): reserve floor SoC, and a night grid-charge window up to a target SoC.
Each variant is scored like kpis.py: SoC-adjusted bill, SoC-adjusted grid CO2 (hourly ENTSO-E CI).
"""
from carbon import ci_lookup
from kpis import DT, FILES, P_MAX, ROOT, load, rule_baseline, soc_value
from timeseries import soc0_of


def knob_rule(rows, soc0, floor=None, gc_hours=(), gc_target=0.0):
    """Self-consumption rule + optional grid charge in gc_hours up to gc_target. Returns imports, exports, end SoC."""
    soc, imp, exp = soc0, [], []
    for r in rows:
        b, net = r["bess"], r["pv"] - r["load"]
        cap, ec = b["capacityKwh"], b["chargeEfficiency"]
        if net <= 0 and int(r["dt"][11:13]) in gc_hours and soc < gc_target:
            c = min(P_MAX * DT, (gc_target - soc) * cap / ec)  # kWh drawn from grid into the battery
            soc += c * ec / cap
            imp.append(-net + c)
            exp.append(0.0)
        else:  # one step of the plain rule from the current SoC
            i, e, soc, _ = rule_baseline([r], soc, floor)
            imp += i
            exp += e
    return imp, exp, soc


def score(rows, soc0, imp, exp, soc_end, cis):
    b0, n = rows[0]["bess"], len(rows)
    mean_buy = sum(r["grid"]["buyPrice"] for r in rows) / n
    bill = sum(i * r["grid"]["buyPrice"] - e * r["grid"]["sellPrice"] for i, e, r in zip(imp, exp, rows))
    d_store = (soc_end - soc0) * b0["capacityKwh"] * b0["dischargeEfficiency"]
    co2 = sum(i * c for i, c in zip(imp, cis)) / 1000 - d_store * sum(cis) / n / 1000
    return bill - soc_value(soc_end - soc0, b0, mean_buy), co2, sum(imp) - d_store


def main():
    ci, src, _ = ci_lookup()
    night = tuple(range(0, 5))
    variants = {
        "rule (floor 10%)": {},
        "rule, reserve floor 20%": {"floor": 0.2},
        "rule, reserve floor 30%": {"floor": 0.3},
        "rule + night grid charge to 30%": {"gc_hours": night, "gc_target": 0.3},
        "rule + night grid charge to 50%": {"gc_hours": night, "gc_target": 0.5},
    }
    print(f"carbon source: {src}\n")
    for name in ("A", "C"):
        rows = load(ROOT / "data/DatasetV4" / FILES[name])
        soc0, cis = soc0_of(rows), [ci(r["dt"]) for r in rows]
        # self-check: the knob rule with no knobs equals kpis.rule_baseline
        i0, e0, s0, _ = rule_baseline(rows, soc0)
        i1, e1, s1 = knob_rule(rows, soc0)
        assert abs(sum(i0) - sum(i1)) < 1e-9 and abs(s0 - s1) < 1e-9
        agent = score(rows, soc0, [r["grid"]["energyImportInterval"] for r in rows],
                      [r["grid"]["energyExportInterval"] for r in rows], rows[-1]["bess"]["soc"], cis)
        print(f"### Sun/load/prices of run {name}\n")
        print("| variant | bill € (SoC-adj) | grid CO2 kg (SoC-adj) | import kWh (SoC-adj) |\n|---|---|---|---|")
        print(f"| agent run {name} (measured) | {agent[0]:.2f} | {agent[1]:.1f} | {agent[2]:.1f} |")
        for v, kw in variants.items():
            imp, exp, s = knob_rule(rows, soc0, **kw)
            c, g, m = score(rows, soc0, imp, exp, s, cis)
            print(f"| {v} | {c:.2f} | {g:.1f} | {m:.1f} |")
        print()


if __name__ == "__main__":
    main()
