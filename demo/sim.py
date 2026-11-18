"""Demo simulation engine: daily agent knobs -> guardrails -> rolling LP optimiser -> Excel KPIs.

Run: .venv/bin/python demo/sim.py --check   (self-checks against data/Sense_Reply_B2_KPI_Conformity.xlsx)
     .venv/bin/python demo/sim.py           (writes demo/out/*.json)
KPI formulas follow the KPI Conformity workbook and report §4. Basis: run C inputs, start SoC 0.80.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from kpis import C_DEG, DT, FILES, LLM, P_IN, P_OUT, ROOT, USD_EUR, bill, load, rule_baseline  # noqa: E402
from timeseries import soc0_of  # noqa: E402

CAP, ETA = 10.0, 0.95
CO2_K = 0.356  # kg/kWh, workbook constant
S_STAR = 2.184  # €/wk perfect-foresight saving implied by the workbook (S / VCR, same in every column)

# Workbook "KPI Verdicts" sheet: id -> (direction, threshold). Direction: +1 higher is better, -1 lower, 0 context.
THRESH = {
    "S_net": (1, 1.03), "VCR": (1, 0.6), "VORB": (1, 0), "N1": (1, 0), "N2": (-1, 0.2), "F1": (1, 0),
    "O5": (-1, 0.5), "S2b": (1, 0), "S3": (-1, 356), "MAC": (-1, 0.09), "S1": (0, None),
    "SCR": (1, 0.7), "SSR": (1, 0.6), "PSR": (1, 0.25), "G2": (-1, 0), "G1": (0, None),
    "B1": (1, 0.88), "B2": (-1, 7), "B4": (-1, 0.25), "B3": (0, None), "B6": (0, None),
    "C5": (-1, 0.5), "C4": (0, None), "O1": (-1, 0.3), "O3": (-1, 0.1),
    "C1": (0, None), "S": (0, None), "IMP": (0, None), "EXP": (0, None), "PV": (0, None),
}
# Workbook columns I, K-N (hardcoded "blue" values). None = blank cell in the workbook.
EXCEL = {
    "A": dict(S_net=0.4071, VCR=0.2769, VORB=-0.7261, N1=-4.3341, N2=7.8375, F1=-5.4673, O5=4.7412, S2b=-10.0493,
              S3=372.5, MAC=None, S1=21.9475, SCR=0.5158, SSR=0.3931, PSR=0.0002, G2=0, G1=4.8053, B1=0.902,
              B2=4.2919, B4=0, B3=0.1979, B6=0.3155, C5=0.8143, C4=0.0124, O1=4.387, O3=0.0115, C1=3.0128,
              S=0.6049, IMP=63.8152, EXP=45.093, PV=93.13),
    "C": dict(S_net=0.4026, VCR=0.2883, VORB=-0.67, N1=-7.306, N2=12.2416, F1=-8.3786, O5=7.7086, S2b=-9.357,
              S3=372, MAC=4.293, S1=21.2553, SCR=0.5393, SSR=0.441, PSR=0.3892, G2=0, G1=2.9312, B1=0.9021,
              B2=4.7343, B4=0, B3=0.2271, B6=0.3065, C5=0.8019, C4=0.0104, O1=7.616, O3=0.0202, C1=2.9828,
              S=0.6297, IMP=58.7329, EXP=42.8702, PV=93.06),
    "Static rule": dict(S_net=1.034, VCR=0.595, VORB=0, N1=1.034, N2=0, F1=0, O5=0, S2b=0, S3=None, MAC=None,
                        S1=11.8983, SCR=0.8291, SSR=0.7028, PSR=0.5325, G2=0, G1=2.2434, B1=0.9025, B2=5.4793,
                        B4=0.4048, B3=0.2657, B6=0.0461, C5=0.7756, C4=0.0105, O1=0, O3=0, C1=2.3128, S=1.2997,
                        IMP=31.2315, EXP=15.9067, PV=93.06),
    "S5 conservative": dict(S_net=1.1156, VCR=0.6303, VORB=0.0772, N1=1.1043, N2=0.0082, F1=0.0659, O5=0.0113,
                            S2b=-1.6223, S3=None, MAC=0.0317, S1=13.5205, SCR=0.7774, SSR=0.673, PSR=0.5325, G2=0,
                            G1=2.2434, B1=0.9025, B2=5.3057, B4=0.2946, B3=0.2612, B6=0.0506, C5=0.7467,
                            C4=0.0144, O1=0.0104, O3=0, C1=2.2357, S=1.3768, IMP=34.3586, EXP=20.7148, PV=93.06),
    "S5 upside": dict(S_net=1.7957, VCR=0.958, VORB=0.793, N1=1.7844, N2=0.0054, F1=0.7817, O5=0.0113,
                      S2b=-10.3422, S3=None, MAC=0.0317, S1=22.2405, SCR=0.5278, SSR=0.3967, PSR=-0.0651, G2=0,
                      G1=5.1114, B1=0.9025, B2=6.3122, B4=0.3378, B3=0.297, B6=0.0759, C5=0.3914, C4=0.0339,
                      O1=0.0104, O3=0, C1=1.5198, S=2.0927, IMP=63.3894, EXP=43.9449, PV=93.06),
}


def load_run(name):
    """kpis.load + load rebuilt from the energy balance (report §4 step 2; reproduces the workbook exactly)."""
    rows = load(ROOT / "data/DatasetV4" / FILES[name])
    for r in rows:
        g, b = r["grid"], r["bess"]
        r["load"] = r["pv"] + g["energyImportInterval"] - g["energyExportInterval"] \
            + b["energyDischargedInterval"] - b["energyChargedInterval"]
    return rows


def observed(rows):
    """Flows of a pilot run as logged."""
    g, b = [r["grid"] for r in rows], [r["bess"] for r in rows]
    return dict(imp=[x["energyImportInterval"] for x in g], exp=[x["energyExportInterval"] for x in g],
                chg=[x["energyChargedInterval"] for x in b], dis=[x["energyDischargedInterval"] for x in b],
                soc=[x["soc"] for x in b], soc0=soc0_of(rows), viol=sum(x["violation"] for x in g))


def rule_flows(rows, soc0):
    """Static rule twin (kpis.rule_baseline); per-step charge/discharge recovered from its SoC trace."""
    socs = []
    imp, exp, _, _ = rule_baseline(rows, soc0, socs=socs)
    prev, chg, dis = [soc0] + socs[:-1], [], []
    for a, s in zip(prev, socs):
        chg.append(max(s - a, 0) * CAP / ETA)
        dis.append(max(a - s, 0) * CAP * ETA)
    return dict(imp=imp, exp=exp, chg=chg, dis=dis, soc=socs, soc0=soc0, viol=0)


def ai_cost(req, tin, tout, ms, n):
    """O5 (€/wk at Devstral 2 list price), O1, O3 for a run of n 15-min decisions."""
    return dict(O5=(tin * P_IN + tout * P_OUT) / 1e6 * USD_EUR, O1=req / n, O3=ms * req / n / 900_000)


def _base(rows, f):
    """C_adj, gross saving S, SoC-adjusted CO2 (constant factor)."""
    n = len(rows)
    mean_buy = sum(r["grid"]["buyPrice"] for r in rows) / n
    d_soc = f["soc"][-1] - f["soc0"]
    c_adj = bill(f["imp"], f["exp"], rows) - d_soc * CAP * ETA * mean_buy
    c_nb = bill([max(r["load"] - r["pv"], 0) for r in rows], [max(r["pv"] - r["load"], 0) for r in rows], rows)
    co2 = sum(f["imp"]) * CO2_K - d_soc * CAP * ETA * CO2_K
    return c_adj, c_nb - c_adj, co2


def kpis_excel(rows, f, rule, ai, ci=None, co2_rule=None):
    """Every workbook KPI for flows f, vs its own static-rule twin `rule` (flows). ci: hourly g/kWh fn for S3.
    co2_rule: S2b reference. The workbook uses the run-C rule CO2 for every column (even A, whose VORB uses
    A's own rule), so callers pass it; defaults to the twin's CO2."""
    n = len(rows)
    buy = [r["grid"]["buyPrice"] for r in rows]
    pv, ld = sum(r["pv"] for r in rows), sum(r["load"] for r in rows)
    imp, exp, chg, dis, soc = f["imp"], f["exp"], f["chg"], f["dis"], f["soc"]
    c_adj, s, co2 = _base(rows, f)
    _, s_rule, co2_twin = _base(rows, rule)
    co2_rule = co2_twin if co2_rule is None else co2_rule
    k = dict(C1=c_adj, S=s, S_net=s - C_DEG * sum(dis), VCR=s / S_STAR, VORB=s - s_rule, S1=co2, S2b=co2_rule - co2)
    k.update(ai)
    k["N1"] = k["S_net"] - k["O5"]
    k["N2"] = k["O5"] / s
    k["F1"] = k["VORB"] - k["O5"]
    k["S3"] = 1000 * sum(i * ci(r["dt"]) / 1000 for i, r in zip(imp, rows)) / sum(imp) if ci else None
    nb_peak = max(max(r["load"] - r["pv"], 0) for r in rows)
    k.update(SCR=1 - sum(exp) / pv, SSR=1 - sum(imp) / ld, PSR=1 - max(imp) / nb_peak, G2=f["viol"],
             G1=max(imp) / DT, B1=(sum(dis) + (soc[-1] - f["soc0"]) * CAP * ETA) / sum(chg),
             B2=(sum(chg) + sum(dis)) / (2 * CAP), B4=sum(x <= 0.11 or x >= 0.89 for x in soc) / n,
             B3=C_DEG * sum(dis), B6=sum(abs(x - 0.8) < 0.03 for x in soc) / n,
             IMP=sum(imp), EXP=sum(exp), PV=pv)
    med = sorted(buy)[n // 2]
    k["C5"] = sum(i for i, p in zip(imp, buy) if p > med) / sum(imp)
    k["C4"] = sum(d * p for d, p in zip(dis, buy)) / sum(dis) - sum(c * p for c, p in zip(chg, buy)) / sum(chg)
    return k


def verdict(kid, v):
    d, t = THRESH[kid]
    if d == 0:
        return "Context"
    if v is None:
        return "n/a"
    return "Good" if (v >= t if d > 0 else v <= t) else "Improvable"


def check_excel():
    """Acceptance 1a/1b: our KPI code reproduces the workbook's A, C and Static-rule columns."""
    c = load_run("C")
    rule_c = rule_flows(c, 0.80)
    zero = dict(O5=0, O1=0, O3=0)
    got = {"Static rule": kpis_excel(c, rule_c, rule_c, zero)}
    co2_c = got["Static rule"]["S1"]
    for name in ("A", "C"):
        rows = load_run(name)
        f = observed(rows)
        req, tin, tout, ms = LLM[name]
        got[name] = kpis_excel(rows, f, rule_flows(rows, f["soc0"]), ai_cost(req, tin, tout, ms, len(rows)),
                               co2_rule=co2_c)
    bad = []
    for col, k in got.items():
        for kid, want in EXCEL[col].items():
            if want is None or kid in ("S3", "MAC"):
                continue
            tol = 0.002 * max(1, abs(want))
            if abs(k[kid] - want) > tol:
                bad.append(f"{col} {kid}: got {k[kid]:.4f}, Excel {want}")
    assert not bad, "workbook mismatch:\n" + "\n".join(bad)
    print(f"check 1a/1b ok: A, C, Static rule reproduce the workbook")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_excel()
