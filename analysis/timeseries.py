"""Time-series view of runs A, B, C: per-day KPIs, day types, hourly profiles, anomalies. Stdlib only.

Run: python3 analysis/timeseries.py  -> markdown on stdout + self-check asserts.
Per-day "excess vs rule" = agent minus rule baseline on the same day's sun and load, € corrected for the
change in the SoC gap between agent and rule over that day (same method as kpis.py, per day).
"""
from collections import defaultdict

from carbon import ci_lookup
from kpis import FILES, ROOT, load, rule_baseline


def soc0_of(rows):
    b = rows[0]["bess"]
    return b["soc"] - (b["energyChargedInterval"] * b["chargeEfficiency"]
                       - b["energyDischargedInterval"] / b["dischargeEfficiency"]) / b["capacityKwh"]


def per_day(rows, ci):
    """One dict per calendar day: agent and rule energy, €, CO2, plus SoC-gap-corrected excess vs rule."""
    soc0 = soc0_of(rows)
    rule_socs = []
    r_imp, r_exp, _, _ = rule_baseline(rows, soc0, socs=rule_socs)
    b0 = rows[0]["bess"]
    mean_buy = sum(r["grid"]["buyPrice"] for r in rows) / len(rows)
    val = b0["capacityKwh"] * b0["dischargeEfficiency"] * mean_buy  # € per unit SoC, as kpis.soc_value
    days = defaultdict(lambda: defaultdict(float))
    gap_prev = 0.0  # agent SoC - rule SoC at end of previous day (both start at soc0)
    for i, r in enumerate(rows):
        d, g = days[r["dt"][:10]], r["grid"]
        imp, exp, ci_t = g["energyImportInterval"], g["energyExportInterval"], ci(r["dt"])
        d["n"] += 1
        d["pv"] += r["pv"]
        d["load"] += r["load"]
        d["imp"] += imp
        d["exp"] += exp
        d["bill"] += imp * g["buyPrice"] - exp * g["sellPrice"]
        d["co2"] += imp * ci_t / 1000
        d["r_imp"] += r_imp[i]
        d["r_bill"] += r_imp[i] * g["buyPrice"] - r_exp[i] * g["sellPrice"]
        d["r_co2"] += r_imp[i] * ci_t / 1000
        d["soc_end"] = r["bess"]["soc"]
        d["gap_end"] = r["bess"]["soc"] - rule_socs[i]
    for d in days.values():
        d["x_eur"] = d["bill"] - d["r_bill"] - (d["gap_end"] - gap_prev) * val
        d["x_co2"] = d["co2"] - d["r_co2"]
        gap_prev = d["gap_end"]
    return dict(days)


def hourly(rows, ci):
    h = defaultdict(lambda: defaultdict(float))
    for r in rows:
        x = h[int(r["dt"][11:13])]
        x["n"] += 1
        x["soc"] += r["bess"]["soc"]
        x["p"] += r["bess"]["power"]
        x["imp"] += r["grid"]["energyImportInterval"]
        x["exp"] += r["grid"]["energyExportInterval"]
        x["net"] += r["pv"] - r["load"]
        x["buy"] += r["grid"]["buyPrice"]
        x["ci"] += ci(r["dt"])
    return h


def main():
    ci, src, _ = ci_lookup()
    data = {n: load(ROOT / "data/DatasetV4" / f) for n, f in FILES.items()}
    days = {n: per_day(rows, ci) for n, rows in data.items()}
    # self-check: per-day sums equal weekly totals (kpis.py asserts the weekly values)
    for n, rows in data.items():
        for key, tot in [("imp", sum(r["grid"]["energyImportInterval"] for r in rows)), ("pv", sum(r["pv"] for r in rows))]:
            assert abs(sum(d[key] for d in days[n].values()) - tot) < 1e-6, (n, key)
    assert abs(sum(d["imp"] for d in days["C"].values()) - 58.73) < 0.01
    print(f"carbon source: {src}\n")

    # day type from A's daily PV (A and C share weather and dirt); partial days excluded from typing
    full = [d for d, x in days["A"].items() if x["n"] == 96]
    pv_sorted = sorted(days["A"][d]["pv"] for d in full)
    cut = pv_sorted[len(pv_sorted) // 2]
    dtype = {d: ("partial" if d not in full else "sunny" if days["A"][d]["pv"] >= cut else "dull") for d in days["A"]}

    print("## Per day (raw, not SoC-adjusted; excess = agent − rule, € SoC-gap-corrected)\n")
    print("| day | type | run | PV kWh | load kWh | import kWh | export kWh | self-cons % | bill € | CO2 kg | SoC end | excess € vs rule | excess CO2 kg vs rule |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for day in sorted(days["A"]):
        for n in data:
            x = days[n].get(day)
            if not x:
                continue
            sc = 100 * (x["pv"] - x["exp"]) / x["pv"] if x["pv"] else float("nan")
            print(f"| {day} | {dtype[day]} | {n} | {x['pv']:.1f} | {x['load']:.1f} | {x['imp']:.1f} | {x['exp']:.1f} | "
                  f"{sc:.0f} | {x['bill']:.2f} | {x['co2']:.2f} | {x['soc_end']:.2f} | {x['x_eur']:+.2f} | {x['x_co2']:+.2f} |")

    print("\n## Trade-off by day type (sum over days of agent − own rule baseline)\n")
    print("| day type | days | run | excess € | excess CO2 kg | excess import kWh |\n|---|---|---|---|---|---|")
    for t in ("sunny", "dull"):
        ds = [d for d in dtype if dtype[d] == t]
        for n in data:
            xs = [days[n][d] for d in ds]
            print(f"| {t} | {len(ds)} | {n} | {sum(x['x_eur'] for x in xs):+.2f} | {sum(x['x_co2'] for x in xs):+.2f} | "
                  f"{sum(x['imp'] - x['r_imp'] for x in xs):+.1f} |")
    print(f"\n(sunny = full day with A's PV ≥ median {cut:.1f} kWh)")

    print("\n## Hourly profile (mean over the week)\n")
    hs = {n: hourly(rows, ci) for n, rows in data.items()}
    print("| hour | PV−load kWh/slot | buy €/kWh | CI g/kWh | SoC A | SoC B | SoC C | BESS kW A | BESS kW C | import kWh A | import kWh C | export kWh A | export kWh C |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for hr in range(24):
        a, b, c = hs["A"][hr], hs["B"][hr], hs["C"][hr]
        m = lambda x, k: x[k] / x["n"]
        print(f"| {hr:02d} | {m(a, 'net'):+.2f} | {m(a, 'buy'):.3f} | {m(a, 'ci'):.0f} | {m(a, 'soc'):.2f} | {m(b, 'soc'):.2f} | "
              f"{m(c, 'soc'):.2f} | {m(a, 'p'):+.2f} | {m(c, 'p'):+.2f} | {m(a, 'imp'):.3f} | {m(c, 'imp'):.3f} | "
              f"{m(a, 'exp'):.3f} | {m(c, 'exp'):.3f} |")

    print("\n## Anomalies\n")
    stamps = {n: [r["dt"] for r in rows] for n, rows in data.items()}
    missing = sorted(set(stamps["A"]) - set(stamps["B"]))
    print(f"- B missing samples: {missing}")
    for n, rows in data.items():
        g = [r["grid"] for r in rows]
        print(f"- {n}: violations {sum(x['violation'] for x in g)}, throttling {sum(r['bess']['throttling'] for r in rows)}, "
              f"faults {sum(r['bess']['fault'] for r in rows)}, grid unavailable {sum(1 - x['available'] for x in g)}, "
              f"export while BESS discharging (kWh) "
              f"{sum(x['energyExportInterval'] for x, r in zip(g, rows) if r['bess']['power'] < 0):.2f}")


if __name__ == "__main__":
    main()
