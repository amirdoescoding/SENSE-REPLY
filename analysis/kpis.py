"""KPIs for Sense Reply configs A (Orch+Cost), B and C (Orch+Cost+Sust; C = same panel dirt as A). Stdlib only.

Run: python3 analysis/kpis.py   -> markdown table on stdout + self-check asserts.
Formulas are documented in docs/KPIS.md.
"""
import json
from pathlib import Path

from carbon import ci_lookup

ROOT = Path(__file__).resolve().parent.parent
DT = 0.25  # h per sample
P_MAX = 5.0  # kW inverter limit (max of maximumCharge/DischargePower in data)
# €/kWh discharged. data/DatasetV4/Assets/BSS.json: replacementCostPerEnergy 100 €/kWh x
# cycleDegradationPerEquivalentCycle 0.005 % (telemetry: dSoH/EFC = 5.0e-5 in all runs).
# 1 EFC costs 5e-5 x 100 x Cap and discharges ~Cap kWh -> 100 x 5e-5 per kWh.
C_DEG = 100 * 0.005 / 100
USD_EUR = 0.86  # assumed FX for LLM cost
P_IN, P_OUT = 0.40, 2.00  # $/M tokens Devstral 2 (aggregator figure, docs/research/04 §2)
# From DataIndex.xlsx (see .claude/MEMORY.md): requests, input tok, output tok, mean LLM ms
LLM = {"A": (2948, 11_690_688, 418_362, 2355), "B": (5472, 20_049_658, 770_858, 2486),
       "C": (5118, 18_792_541, 723_233, 2384)}
FILES = {"A": "dataset-001.json", "B": "dataset-002.json", "C": "dataset-003.json"}
TARGET_SOC = 0.80  # BSS.json targetStateOfCharge


def load(path):
    """One flat dict per 15-min sample, sorted by time. Assets found by their fields."""
    rows = []
    for s in json.loads(path.read_text()):
        r = {"dt": s["datetime"], "pv": 0.0}
        for a in s["state"]["assets"]:
            if "pv_energy_interval" in a:
                r["pv"] += a["pv_energy_interval"]
            elif "soc" in a:
                r["bess"] = a
            elif "load" in a:
                r["load"] = a["load"] * DT  # kW -> kWh
            elif "buyPrice" in a:
                r["grid"] = a
        rows.append(r)
    return sorted(rows, key=lambda r: r["dt"])


def bill(imp, exp, rows):
    return sum(i * r["grid"]["buyPrice"] - e * r["grid"]["sellPrice"] for i, e, r in zip(imp, exp, rows))


def soc_value(d_soc, b, mean_buy):
    """€ value of stored energy change: what it would cost to buy back from the grid."""
    return d_soc * b["capacityKwh"] * b["dischargeEfficiency"] * mean_buy


def rule_baseline(rows, soc0, floor=None, socs=None):
    """Self-consumption rule: charge on PV surplus, discharge to cover deficit.
    Power limits come from the rule's OWN SoC, using the formula the data follows
    (maxCharge = min(5, (SoCmax - SoC)*Cap per h), fits within 0.08 kW). floor = optional reserve SoC."""
    soc, imp, exp, dis_tot = soc0, [], [], 0.0
    for r in rows:
        b, net = r["bess"], r["pv"] - r["load"]
        cap, ec, ed = b["capacityKwh"], b["chargeEfficiency"], b["dischargeEfficiency"]
        lo = max(b["minimumStateOfCharge"], floor or 0)
        if net > 0:
            p_max = min(P_MAX, (b["maximumStateOfCharge"] - soc) * cap)
            c = max(min(net, p_max * DT, (b["maximumStateOfCharge"] - soc) * cap / ec), 0)
            soc += c * ec / cap
            imp.append(0.0)
            exp.append(net - c)
        else:
            p_max = min(P_MAX, (soc - b["minimumStateOfCharge"]) * cap)
            d = max(min(-net, p_max * DT, (soc - lo) * cap * ed), 0)
            soc -= d / ed / cap
            dis_tot += d
            imp.append(-net - d)
            exp.append(0.0)
        if socs is not None:  # optional SoC trace, used by timeseries.py
            socs.append(soc)
    return imp, exp, soc, dis_tot


def kpis(name, rows, ci):
    n = len(rows)
    g = [r["grid"] for r in rows]
    b = [r["bess"] for r in rows]
    imp = [x["energyImportInterval"] for x in g]
    exp = [x["energyExportInterval"] for x in g]
    chg = [x["energyChargedInterval"] for x in b]
    dis = [x["energyDischargedInterval"] for x in b]
    pv = sum(r["pv"] for r in rows)
    ld = sum(r["load"] for r in rows)
    buy = [x["buyPrice"] for x in g]
    mean_buy = sum(buy) / n
    b0 = b[0]
    # SoC before first interval: undo first interval's charge/discharge
    soc0 = b0["soc"] - (chg[0] * b0["chargeEfficiency"] - dis[0] / b0["dischargeEfficiency"]) / b0["capacityKwh"]
    soc_end = b[-1]["soc"]

    k = {}
    # --- economic (cost agent) ---
    k["E1 net energy bill €"] = e1 = bill(imp, exp, rows)
    k["E2 SoC-adjusted bill €"] = e2 = e1 - soc_value(soc_end - soc0, b0, mean_buy)
    k["E3 cost per kWh load €/kWh"] = e2 / ld
    nb_imp = [max(r["load"] - r["pv"], 0) for r in rows]
    nb_exp = [max(r["pv"] - r["load"], 0) for r in rows]
    c_nb = bill(nb_imp, nb_exp, rows)
    r_imp, r_exp, r_soc, r_dis = rule_baseline(rows, soc0)
    c_rule = bill(r_imp, r_exp, rows) - soc_value(r_soc - soc0, b0, mean_buy)
    f_imp, f_exp, f_soc, f_dis = rule_baseline(rows, soc0, floor=0.3)
    c_rule30 = bill(f_imp, f_exp, rows) - soc_value(f_soc - soc0, b0, mean_buy)
    k["  baseline no-battery bill €"] = c_nb
    k["  baseline rule-based bill € (SoC-adj)"] = c_rule
    k["  baseline rule + 30% reserve bill €"] = c_rule30
    k["E4a savings vs no-battery %"] = 100 * (c_nb - e2) / c_nb
    k["E4a savings vs no-battery €"] = c_nb - e2
    k["E4b savings vs rule-based %"] = 100 * (c_rule - e2) / c_rule
    k["E4b savings vs rule-based €"] = c_rule - e2
    k["E4c savings vs rule+30% reserve €"] = c_rule30 - e2
    # wear-inclusive: add c_deg * discharged energy to agent and rule
    k["  discharged kWh agent / rule"] = f"{sum(dis):.1f} / {r_dis:.1f}"
    k["E4d savings vs rule incl. wear €"] = (c_rule + C_DEG * r_dis) - (e2 + C_DEG * sum(dis))
    k["E7 break-even c_deg agent=rule €/kWh"] = (e2 - c_rule) / (r_dis - sum(dis)) if r_dis > sum(dis) else float("nan")
    k["E8 break-even c_deg battery pays off €/kWh"] = (c_nb - e2) / sum(dis)
    k["E5 price-timing spread €/kWh"] = (
        sum(d * p for d, p in zip(dis, buy)) / sum(dis) - sum(c * p for c, p in zip(chg, buy)) / sum(chg)
    )
    k["E6 import at high price % (buy > median)"] = (
        100 * sum(i for i, p in zip(imp, buy) if p > sorted(buy)[n // 2]) / sum(imp)
    )
    # --- energy / sustainability proxies ---
    k["  PV energy kWh"] = pv
    k["  load kWh"] = ld
    k["  grid import kWh"] = sum(imp)
    k["  grid export kWh"] = sum(exp)
    k["G1 self-consumption %"] = 100 * (pv - sum(exp)) / pv
    k["G2 self-sufficiency %"] = 100 * (1 - sum(imp) / ld)
    pv_to_bat = sum(min(c, max(r["pv"] - r["load"], 0)) for c, r in zip(chg, rows))
    k["G3 green charging share %"] = 100 * pv_to_bat / sum(chg)
    k["G4 peak import kW"] = max(x["power"] for x in g)
    k["G5 violations / penalty €"] = f'{sum(x["violation"] for x in g)} / {sum(x["penalty"] for x in g):.2f}'
    k["  rule-based import kWh"] = sum(r_imp)
    # --- sustainability (needs carbon intensity CI_t, g/kWh) ---
    cis = [ci(r["dt"]) for r in rows]
    co2 = lambda imps: sum(i * c for i, c in zip(imps, cis)) / 1000  # kg
    k["S1 grid CO2 kg"] = s1 = co2(imp)
    k["S2a CO2 avoided vs no-battery kg"] = co2(nb_imp) - s1
    k["S2b CO2 avoided vs rule-based kg"] = co2(r_imp) - s1
    k["S3 CO2 intensity of imports g/kWh"] = 1000 * s1 / sum(imp)
    k["  mean grid CI g/kWh"] = sum(cis) / n
    k["_excess_cost"] = e2 - c_rule  # used for T1/T2, hidden
    # same end-SoC correction as €: energy the agent holds above the rule at the end replaces future imports
    d_store = (soc_end - r_soc) * b0["capacityKwh"] * b0["dischargeEfficiency"]  # kWh
    k["_excess_co2"] = s1 - co2(r_imp) - d_store * sum(cis) / n / 1000
    k["  excess import vs rule kWh (SoC-adj)"] = sum(imp) - sum(r_imp) - d_store
    k["G6 P99 import kW"] = sorted(x["power"] for x in g)[int(0.99 * n)]
    # --- battery ---
    k["B1 apparent storage efficiency (device 0.95²=0.90)"] = (sum(dis) + (soc_end - soc0) * b0["capacityKwh"] * b0["dischargeEfficiency"]) / sum(chg)
    k["B2 equivalent full cycles"] = (sum(chg) + sum(dis)) / (2 * b0["capacityKwh"])
    k["B3 degradation cost € (BSS.json wear)"] = C_DEG * sum(dis)
    k["B4 time at SoC limit %"] = 100 * sum(
        x["soc"] <= x["minimumStateOfCharge"] + 0.01 or x["soc"] >= x["maximumStateOfCharge"] - 0.01 for x in b
    ) / n
    k["B6 time near target SoC 0.8 %"] = 100 * sum(abs(x["soc"] - TARGET_SOC) < 0.03 for x in b) / n
    k["  SoC start -> end"] = f"{soc0:.2f} -> {soc_end:.2f}"
    k["  mean SoC"] = sum(x["soc"] for x in b) / n
    k["B5 SoH loss % / max temp °C"] = f'{100 * (b0["soh"] - b[-1]["soh"]):.3f} / {max(x["temperature"] for x in b):.1f}'
    # --- orchestrator / agent ops ---
    req, tin, tout, ms = LLM[name]
    llm_eur = (tin * P_IN + tout * P_OUT) / 1e6 * USD_EUR
    k["O1 LLM calls per decision"] = req / n
    k["O2 input tokens per decision"] = tin / n
    k["O3 decision latency s (upper bound)"] = ms * req / n / 1000
    k["O4 LLM cost per decision €"] = llm_eur / n
    k["O5 LLM cost per week €"] = llm_eur
    k["F1 net value vs rule-based €/week"] = c_rule - e2 - llm_eur
    k["F1w net value vs rule incl. wear €/week"] = k["E4d savings vs rule incl. wear €"] - llm_eur
    k["F2 LLM cost / energy savings vs no-battery"] = llm_eur / (c_nb - e2)
    p = [x["power"] for x in b]
    modes = [x > 0 for x in p if x != 0]  # charge/discharge sequence, idle skipped
    k["F3 mode switches per day"] = sum(a != c for a, c in zip(modes, modes[1:])) / (n * DT / 24)
    k["F4 mean |ΔP| kW"] = sum(abs(c - a) for a, c in zip(p, p[1:])) / (n - 1)
    k["  samples"] = n
    k["  energy balance residual kWh"] = sum(
        i - e - (r["load"] - r["pv"] + c - d) for i, e, r, c, d in zip(imp, exp, rows, chg, dis)
    )
    return k


def fmt(v):
    return v if isinstance(v, str) else f"{v:,.4f}" if abs(v) < 1 else f"{v:,.2f}"


def main():
    ci, src, hours = ci_lookup()
    data = {n: load(ROOT / "data/DatasetV4" / f) for n, f in FILES.items()}
    if hours is not None:  # hourly CSV: make sure timestamps actually line up, else misses silently use STATIC
        rows = [r for d in data.values() for r in d]
        cov = sum(r["dt"][:13] in hours for r in rows) / len(rows)
        src += f", coverage {100 * cov:.0f}%"
        assert cov > 0.9, f"ENTSO-E CSV covers only {100 * cov:.0f}% of samples: check dates and time zone"
    res = {n: kpis(n, rows, ci) for n, rows in data.items()}
    a, b = res["A"], res["B"]
    # self-check: must reproduce docs/research/00-synthesis.md §1
    for key, va, vb in [
        ("E1 net energy bill €", 3.23, 5.15),
        ("  PV energy kWh", 93.13, 69.12),
        ("  grid import kWh", 63.82, 60.49),
        ("  grid export kWh", 45.09, 17.57),
    ]:
        assert abs(a[key] - va) < 0.01 and abs(b[key] - vb) < 0.01, (key, a[key], b[key])
    c = res["C"]
    for key, v in [("E1 net energy bill €", 2.89), ("  PV energy kWh", 93.06),
                   ("  grid import kWh", 58.73), ("  grid export kWh", 42.87)]:
        assert abs(c[key] - v) < 0.01, (key, c[key])
    print(f"carbon source: {src}\n")
    print("| KPI | A (Orch+Cost) | B (Orch+Cost+Sust) | C (Orch+Cost+Sust, same dirt as A) |\n|---|---|---|---|")
    for key in a:
        if not key.startswith("_"):
            print(f"| {key} | {fmt(a[key])} | {fmt(b[key])} | {fmt(c[key])} |")
    # trade-off vs A, each run measured against its own rule baseline (removes PV/SoC differences)
    for name, x in [("C", c), ("B", b)]:
        d_cost = x["_excess_cost"] - a["_excess_cost"]
        d_co2 = a["_excess_co2"] - x["_excess_co2"]  # kg CO2 saved vs A
        d_imp = a["  excess import vs rule kWh (SoC-adj)"] - x["  excess import vs rule kWh (SoC-adj)"]
        print(f"\nT1 {name}-vs-A import saved kWh (baseline-relative, SoC-adj): {d_imp:.2f}")
        d_llm = x["O5 LLM cost per week €"] - a["O5 LLM cost per week €"]
        d_deg = x["B3 degradation cost € (BSS.json wear)"] - a["B3 degradation cost € (BSS.json wear)"]
        print(f"T1 {name}-vs-A extra energy cost € (baseline-relative): {d_cost:.2f}")
        print(f"T1 {name}-vs-A CO2 saved kg (baseline-relative): {d_co2:.2f}")
        print(f"T1 marginal abatement cost €/kg: {d_cost / d_co2:.2f}" if d_co2 > 0 and d_cost > 0
              else "T1 marginal abatement cost: n/a (dominates or is dominated)")
        print(f"T2 {name}-vs-A total cost of sustainability € (energy+wear+LLM): {d_cost + d_deg + d_llm:.2f}")
        if d_co2 > 0:
            print(f"T3 {name}-vs-A abatement cost incl. LLM €/t CO2: {1000 * (d_cost + d_deg + d_llm) / d_co2:,.0f}")

if __name__ == "__main__":
    main()
