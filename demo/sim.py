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


# ---------------------------------------------------------------- optimiser
RESERVE_HOUR = 17  # evening_reserve_kwh must be in the battery at 17:00
SLACK_EUR = 1.0  # €/kWh penalty for missing the evening reserve (soft: it can be unreachable without sun)


def default_knobs(mode, mean_buy):
    """Plain S5: no extra floor or reserve, stored energy valued like C_adj, grid charging only in upside."""
    return dict(soc_floor=0.10, evening_reserve_kwh=0.0, export_hold_eur=round(mean_buy, 4),
                grid_charge=None if mode == "conservative" else {"from": 0, "to": 24})


def _grid_ok(knobs, hour):
    gc = knobs.get("grid_charge")
    if not gc:
        return False
    a, b = gc["from"], gc["to"]
    return a <= hour < b if a <= b else hour >= a or hour < b


def plan_lp(pv, ld, buy, sell, ci, hours, soc0, knobs, lam):
    """LP over len(pv) steps (forecast inputs). Returns per-step (chg, dis, soc) lists.
    Vars per step: I, X, c, d, s (SoC after step), r (reserve slack). Live limits are linear in SoC:
    c <= min(5, 10(0.9 - s_prev))*DT, d <= min(5, 10(s_prev - 0.1))*DT (fits telemetry within 0.08 kW)."""
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix

    H = len(pv)
    I, X, C, D, S, R = (k * H for k in range(6))
    nv = 6 * H
    ci_mean = sum(ci) / H
    cost = np.zeros(nv)
    for t in range(H):
        cost[I + t] = buy[t] + lam * ci[t] / 1000
        cost[X + t] = -sell[t]
        cost[D + t] = C_DEG
        cost[R + t] = SLACK_EUR
    # stored energy at the horizon end replaces future imports: € (export_hold) + CO2 (λ x mean CI)
    cost[S + H - 1] -= (knobs["export_hold_eur"] + lam * ci_mean / 1000) * ETA * CAP

    floor = min(knobs["soc_floor"], soc0)  # never infeasible: idling keeps SoC at soc0
    reserve = min(0.9, knobs["soc_floor"] + knobs["evening_reserve_kwh"] / CAP)
    bounds = []
    for blk in range(6):
        for t in range(H):
            if blk == 2:  # charge: grid charging only where allowed
                surplus = max(pv[t] - ld[t], 0)
                hi = 5 * DT if _grid_ok(knobs, hours[t]) else min(5 * DT, surplus)
                bounds.append((0, hi))
            elif blk == 3:
                bounds.append((0, 5 * DT))
            elif blk == 4:
                bounds.append((floor, 0.9))
            else:
                bounds.append((0, None))

    A_eq, b_eq = lil_matrix((2 * H, nv)), np.zeros(2 * H)
    A_ub, b_ub = lil_matrix((3 * H, nv)), np.zeros(3 * H)
    for t in range(H):
        A_eq[t, I + t], A_eq[t, X + t], A_eq[t, C + t], A_eq[t, D + t] = 1, -1, -1, 1
        b_eq[t] = ld[t] - pv[t]
        row = H + t
        A_eq[row, S + t], A_eq[row, C + t], A_eq[row, D + t] = 1, -ETA / CAP, 1 / (ETA * CAP)
        if t:
            A_eq[row, S + t - 1] = -1
        else:
            b_eq[row] = soc0
        # live limits from previous SoC
        A_ub[t, C + t] = 1
        A_ub[H + t, D + t] = 1
        if t:
            A_ub[t, S + t - 1] = 10 * DT
            A_ub[H + t, S + t - 1] = -10 * DT
            b_ub[t], b_ub[H + t] = 9 * DT, -DT
        else:
            b_ub[t], b_ub[H + t] = max(9 - 10 * soc0, 0) * DT, max(10 * soc0 - 1, 0) * DT
        # evening reserve (soft): s_t + r_t >= reserve at 17:00
        if hours[t] == RESERVE_HOUR and reserve > floor:
            A_ub[2 * H + t, S + t], A_ub[2 * H + t, R + t] = -1, -1
            b_ub[2 * H + t] = -reserve
    res = linprog(cost, A_ub=A_ub.tocsr(), b_ub=b_ub, A_eq=A_eq.tocsr(), b_eq=b_eq, bounds=bounds, method="highs")
    assert res.status == 0, res.message
    x = res.x
    return list(x[C:C + H]), list(x[D:D + H]), list(x[S:S + H])


def _hour(r):
    return int(r["dt"][11:13])


def _inputs(rows, ci):
    return ([r["grid"]["buyPrice"] for r in rows], [r["grid"]["sellPrice"] for r in rows],
            [ci(r["dt"]) for r in rows], [_hour(r) for r in rows])


def apply_step(r, soc, c, d, knobs):
    """Clamp a planned (charge, discharge) to the ACTUAL step and battery limits. The grid takes the rest."""
    net = r["pv"] - r["load"]
    c_max = min(5, max(10 * (0.9 - soc), 0)) * DT
    d_max = min(5, max(10 * (soc - 0.1), 0)) * DT
    if not _grid_ok(knobs, _hour(r)):
        c = min(c, max(net, 0))
    c = max(min(c, c_max, (0.9 - soc) * CAP / ETA), 0)
    d = max(min(d, d_max, (soc - 0.1) * CAP * ETA, max(-net, 0)), 0)  # never discharge into export
    if c > 0:  # never charge and discharge in the same step
        d = 0.0
    soc += c * ETA / CAP - d / (ETA * CAP)
    g = r["load"] - r["pv"] + c - d
    return soc, c, d, max(g, 0), max(-g, 0)


def run_mpc(rows, soc0, knobs_for_day, mode, lam, ci, prior, horizon=96, t0=0, t1=None):
    """Rolling optimiser: every 15 min, plan `horizon` steps on a 24 h persistence forecast (PV and load of
    the same slot yesterday; `prior` = 96 (pv, load) pairs standing in for 'yesterday' on day 1), prices known,
    then apply step 1 to the actual data. knobs_for_day(day_index) -> knobs. Returns flows."""
    buy, sell, cis, hours = _inputs(rows, ci)
    n, soc = len(rows), soc0
    f = dict(imp=[], exp=[], chg=[], dis=[], soc=[], soc0=soc0, viol=0)
    for t in range(t0, n if t1 is None else t1):
        knobs = knobs_for_day(t // 96)
        end = min(n, t + horizon)
        fc = [prior[k] if k < 96 else (rows[k - 96]["pv"], rows[k - 96]["load"]) for k in range(t, end)]
        c, d, _ = plan_lp([v[0] for v in fc], [v[1] for v in fc], buy[t:end], sell[t:end], cis[t:end],
                          hours[t:end], soc, knobs, lam)
        soc, c, d, i, e = apply_step(rows[t], soc, c[0], d[0], knobs)
        for key, v in zip(("chg", "dis", "imp", "exp", "soc"), (c, d, i, e, soc)):
            f[key].append(v)
    return f


def run_perfect(rows, soc0, knobs, lam, ci):
    """One LP over the whole of `rows` with perfect foresight (S* check, memory seed, replay gate)."""
    buy, sell, cis, hours = _inputs(rows, ci)
    pv, ld = [r["pv"] for r in rows], [r["load"] for r in rows]
    c, d, s = plan_lp(pv, ld, buy, sell, cis, hours, soc0, knobs, lam)
    g = [l - p + a - b for l, p, a, b in zip(ld, pv, c, d)]
    return dict(imp=[max(x, 0) for x in g], exp=[max(-x, 0) for x in g], chg=c, dis=d, soc=s, soc0=soc0, viol=0)


def day_prior(rows, start):
    """Persistence 'yesterday' for the 96-step day at `start`. Day 1 has none: use the next day (flagged)."""
    src = rows[start - 96:start] if start >= 96 else rows[start + 96:start + 192]
    return [(r["pv"], r["load"]) for r in src]


def run_day(rows, start, soc0, knobs, mode, lam, ci):
    """Rolling MPC over one 96-step day (horizon truncated at day end, terminal value covers the rest)."""
    return run_mpc(rows[start:start + 96], soc0, lambda _d: knobs, mode, lam, ci, day_prior(rows, start))


def day_score(rows, f, lam):
    """€ + λ·kg for a day: bill + wear - stored-energy value, CO2 at the workbook constant, both SoC-adjusted."""
    mean_buy = sum(r["grid"]["buyPrice"] for r in rows) / len(rows)
    d = (f["soc"][-1] - f["soc0"]) * CAP * ETA
    eur = bill(f["imp"], f["exp"], rows) + C_DEG * sum(f["dis"]) - d * mean_buy
    kg = (sum(f["imp"]) - d) * CO2_K
    return eur + lam * kg, eur, kg


# ---------------------------------------------------------------- daily loop
LAMBDAS = (0.0, 0.10, 0.50)
MODES = ("conservative", "upside")
HEADLINE = ("conservative", 0.10)
FLAGS = ["24 h persistence forecast for PV and load; prices assumed known day-ahead",
         "memory seeded from runs A and C of the same week (leaks); day 1 uses the next day as 'yesterday'",
         "Gemini is a capability stand-in for Devstral 2, not a proposal",
         "site = Italy assumed; carbon KPIs at the workbook constant 0.356 kg/kWh",
         "one January week only"]


def gate(rows, start, knobs, mode, lam, ci, mean_buy):
    """Replay gate: the knobs vs default knobs on YESTERDAY's real data (day 1: the next day, flagged),
    rolling MPC from the logged SoC. Blocks knobs that lose on € + λ·kg."""
    g = start - 96 if start >= 96 else start + 96
    soc = rows[g - 1]["bess"]["soc"] if g else soc0_of(rows)
    day = rows[g:g + 96]
    s_k = day_score(day, run_day(rows, g, soc, knobs, mode, lam, ci), lam)[0]
    s_d = day_score(day, run_day(rows, g, soc, default_knobs(mode, mean_buy), mode, lam, ci), lam)[0]
    return bool(s_k <= s_d + 1e-6), round(float(s_k), 4), round(float(s_d), 4)


def run_ours(rows, mode, lam, ci, mem, soc0=0.80):
    import agent
    mean_buy = sum(r["grid"]["buyPrice"] for r in rows) / len(rows)
    f = dict(imp=[], exp=[], chg=[], dis=[], soc=[], soc0=soc0, viol=0)
    days, soc, last_ok = [], soc0, None
    for day in range(len(rows) // 96):
        start = day * 96
        ans, ctx, nb = agent.propose(rows, start, soc, ci, mode, lam, mem)
        knobs, notes = agent.validate(ans["raw"], mode, mean_buy)
        ok, s_k, s_d = gate(rows, start, knobs, mode, lam, ci, mean_buy)
        if ok:
            used, last_ok = "plan", knobs
        elif last_ok:
            used, knobs = "previous valid plan", last_ok
        else:
            used, knobs = "static rule", None
        if knobs is None:
            df = rule_flows(rows[start:start + 96], soc)
        else:
            df = run_mpc(rows, soc, lambda _d, k=knobs: k, mode, lam, ci, day_prior(rows, 0), t0=start, t1=start + 96)
        for key in ("imp", "exp", "chg", "dis", "soc"):
            f[key] += df[key]
        days.append(dict(day=day + 1, start=rows[start]["dt"], context=ctx,
                         neighbours=[dict(label=f"{n['run']} day {n['day'] + 1}", regret=round(n["regret_vs_rule"], 4)) for n in nb],
                         proposed=ans["raw"], validator_notes=notes,
                         gate=dict(passed=ok, score_plan=s_k, score_default=s_d, basis="yesterday" if day else
                                   "next day (day-1 stand-in)"),
                         used=used, knobs=knobs, source=ans["source"], explanation=ans["explanation"],
                         thoughts=ans["thoughts"], tok_in=ans["tok_in"], tok_out=ans["tok_out"]))
        soc = df["soc"][-1]
    return f, days


def schedule(rows, f):
    return [dict(t=r["dt"], pv_kw=round(r["pv"] / DT, 3), load_kw=round(r["load"] / DT, 3),
                 battery_kw=round((c - d) / DT, 3), grid_kw=round((i - e) / DT, 3), soc=round(s, 4),
                 buy_eur=round(r["grid"]["buyPrice"], 4), sell_eur=round(r["grid"]["sellPrice"], 4))
            for r, c, d, i, e, s in zip(rows, f["chg"], f["dis"], f["imp"], f["exp"], f["soc"])]


def compare(rows):
    """Per-step soc / grid_kw / battery_kw of the reference runs on run C's 672 timestamps (compare.json)."""
    rule = rule_flows(rows, 0.80)
    pilots = {}
    for n in ("C", "A"):
        r = load_run(n)
        assert [x["dt"] for x in r] == [x["dt"] for x in rows], n
        pilots[n] = (observed(r), r)

    def ser(f):
        return dict(soc=[round(s, 4) for s in f["soc"]],
                    grid_kw=[round((i - e) / DT, 3) for i, e in zip(f["imp"], f["exp"])],
                    battery_kw=[round((c - d) / DT, 3) for c, d in zip(f["chg"], f["dis"])])
    nb = dict(soc=[None] * len(rows), grid_kw=[round((r["load"] - r["pv"]) / DT, 3) for r in rows],
              battery_kw=[0.0] * len(rows))
    series = {"Static rule": ser(rule), "No battery": nb, "Pilot C": ser(pilots["C"][0]), "Pilot A": ser(pilots["A"][0])}
    notes = {"Static rule": dict(evidence="MODELLED", inputs="run C PV and load", start_soc=0.80),
             "No battery": dict(evidence="MODELLED", inputs="run C PV and load", start_soc=None),
             "Pilot C": dict(evidence="OBSERVED", inputs="run C logged flows (load from the energy balance)",
                             start_soc=round(pilots["C"][0]["soc0"], 3)),
             "Pilot A": dict(evidence="OBSERVED", inputs="run A logged flows (load from the energy balance)",
                             start_soc=round(pilots["A"][0]["soc0"], 3),
                             caveat="not like-for-like: different PV (panel dirt 0.03 vs C 0.26 at start) "
                                    "and start SoC 0.572 vs 0.80")}
    return dict(t=[r["dt"] for r in rows], series=series, notes=notes)


def check_run(rows, f, mode):
    """Acceptance 3: physics and mode rules hold on every step."""
    assert len(f["soc"]) == len(rows) == 672
    assert all(0.1 - 1e-6 <= x <= 0.9 + 1e-6 for x in f["soc"])
    assert all(c <= 5 * DT + 1e-9 and d <= 5 * DT + 1e-9 for c, d in zip(f["chg"], f["dis"]))
    for r, i, e, c, d in zip(rows, f["imp"], f["exp"], f["chg"], f["dis"]):
        assert abs(i - e - (r["load"] - r["pv"] + c - d)) < 0.01
        if mode == "conservative":
            assert c <= max(r["pv"] - r["load"], 0) + 1e-6, "conservative charged from the grid"


def main():
    import json
    import agent
    from carbon import ci_lookup
    ci, src, hours = ci_lookup()
    carbon_source, s3_basis = "constant-0.356", "entsoe-hourly" if hours else None  # S3 is the only hourly KPI
    rows = load_run("C")
    rule = rule_flows(rows, 0.80)
    mem = agent.seed_memory(ci)
    cols = {name: dict(v) for name, v in EXCEL.items()}
    runs = {}
    for mode in MODES:
        for lam in LAMBDAS:
            f, days = run_ours(rows, mode, lam, ci, mem)
            check_run(rows, f, mode)
            calls = sum(d["source"] == "gemini" for d in days)
            tin, tout = sum(d["tok_in"] for d in days), sum(d["tok_out"] for d in days)
            ai = ai_cost(calls, tin, tout, 0, len(rows))  # O3 = 0: the LLM is off the 15-min control path
            k = kpis_excel(rows, f, rule, ai, ci=ci if hours else None)
            runs[(mode, lam)] = (f, days, k, dict(calls=calls, tok_in=tin, tok_out=tout))
            print(f"{mode} λ={lam}: S_net {k['S_net']:.3f} VORB {k['VORB']:+.3f} N1 {k['N1']:.3f} "
                  f"S1 {k['S1']:.1f} kg, gemini days {calls}/7, gate blocks {sum(not d['gate']['passed'] for d in days)}")
    for (mode, lam), (f, days, k, tok) in runs.items():
        k["MAC"] = None
        if lam:  # € per kg avoided by the carbon weight, incl. AI cost (workbook: λ 0 -> 0.10)
            k0 = runs[(mode, 0.0)][2]
            d_kg = k0["S1"] - k["S1"]
            d_eur = (k["C1"] + k["B3"] + k["O5"]) - (k0["C1"] + k0["B3"] + k0["O5"])
            k["MAC"] = d_eur / d_kg if d_kg > 0 else None
        cols[f"Ours {mode} λ={lam}"] = k
        plan = dict(window=dict(start=rows[0]["dt"], step_min=15), mode=mode, lambda_eur_per_kg=lam,
                    model=agent.MODEL, knobs=[d["knobs"] for d in days], schedule=schedule(rows, f),
                    kpis={x: (round(v, 4) if isinstance(v, float) else v) for x, v in k.items()},
                    explanation=" ".join(d["explanation"] for d in days), days=days, tokens=tok,
                    carbon_source=carbon_source, s3_basis=s3_basis, carbon_note=src, honesty_flags=FLAGS)
        (agent.OUT / f"run_{mode}_{lam}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    table = dict(headline=f"Ours {HEADLINE[0]} λ={HEADLINE[1]}", s_star=S_STAR, carbon_source=carbon_source, s3_basis=s3_basis,
                 thresholds={x: dict(direction=d, threshold=t) for x, (d, t) in THRESH.items()},
                 columns={c: {x: dict(value=None if v.get(x) is None else round(v[x], 4), verdict=verdict(x, v.get(x)))
                              for x in THRESH} for c, v in cols.items()},
                 source={c: "workbook" for c in EXCEL} | {c: "computed" for c in cols if c.startswith("Ours")})
    table["good_counts"] = {c: sum(v["verdict"] == "Good" for v in kv.values()) for c, kv in table["columns"].items()}
    (agent.OUT / "kpis.json").write_text(json.dumps(table, indent=1, ensure_ascii=False))
    (agent.OUT / "compare.json").write_text(json.dumps(compare(rows), separators=(",", ":")))
    print("good counts:", table["good_counts"])


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


def check_lp(ci):
    """Acceptance 1c (S* soft check) and 2 (plain S5, no agent, vs the workbook S5 columns)."""
    c = load_run("C")
    mean_buy = sum(r["grid"]["buyPrice"] for r in c) / len(c)
    rule = rule_flows(c, 0.80)
    zero = dict(O5=0, O1=0, O3=0)
    up = run_perfect(c, 0.80, default_knobs("upside", mean_buy), 0, ci)
    s_star = _base(c, up)[1]
    print(f"check 1c: perfect-foresight week LP (upside) S = {s_star:.4f} vs workbook S* {S_STAR} "
          f"({100 * (s_star / S_STAR - 1):+.1f}%)" + ("" if abs(s_star / S_STAR - 1) < 0.03 else "  [SOFT MISS]"))
    prior = [(r["pv"], r["load"]) for r in c[96:192]]  # day 1 stand-in until memory exists
    out = {}
    for mode, col in (("conservative", "S5 conservative"), ("upside", "S5 upside")):
        f = run_mpc(c, 0.80, lambda _d, m=mode: default_knobs(m, mean_buy), mode, 0, ci, prior)
        k = kpis_excel(c, f, rule, zero)
        out[mode] = k
        w = EXCEL[col]
        print(f"check 2 {mode}: S_net {k['S_net']:.4f} (Excel {w['S_net']}, {100 * (k['S_net'] / w['S_net'] - 1):+.1f}%)"
              f"  VORB {k['VORB']:.4f} (Excel {w['VORB']})  IMP {k['IMP']:.1f} ({w['IMP']})  S1 {k['S1']:.1f} ({w['S1']})"
              f"  G1 {k['G1']:.2f} ({w['G1']})")
    return out


if __name__ == "__main__":
    if "--check" in sys.argv:
        from carbon import ci_lookup
        check_excel()
        ci = ci_lookup()[0]
        check_lp(ci)
        c = load_run("C")
        mb = sum(r["grid"]["buyPrice"] for r in c) / len(c)
        bad = dict(soc_floor=0.5, evening_reserve_kwh=8.0, export_hold_eur=0.0, grid_charge=None)
        ok, s_k, s_d = gate(c, 96 * 3, bad, "conservative", 0.10, ci, mb)
        assert not ok, (s_k, s_d)
        print(f"check 5 ok: gate blocks floor 0.5 / reserve 8 kWh ({s_k:.3f} vs default {s_d:.3f} €)")
        import agent
        key = agent._key()
        if key:
            hits = [p.name for p in agent.OUT.glob("*") if p.is_file() and key[:12] in p.read_text(errors="ignore")]
            assert not hits, f"API key prefix found in {hits}"
            print("check 7 ok: no API key in demo/out")
    else:
        main()
