"""How predictable are load, grid CO2 and panel soiling, and what is a better forecast worth? Stdlib only.

Run: python3 analysis/forecast_check.py   (uses kpis.load and carbon.ci_lookup)
"""
from collections import defaultdict

from carbon import WEEK, hourly_ci
from kpis import DT, FILES, ROOT, load

STEPS_DAY = 96


def mae(pairs):
    return sum(abs(f - a) for f, a in pairs) / len(pairs)


def load_check(rows):
    """Same-as-yesterday vs mean-of-previous-days, per 15-min step and for the 17-22h evening block."""
    ld = [r["load"] for r in rows]
    yday = [(ld[i - STEPS_DAY], ld[i]) for i in range(STEPS_DAY, len(ld))]
    avg = []
    for i in range(2 * STEPS_DAY, len(ld)):
        past = [ld[j] for j in range(i - STEPS_DAY, -1, -STEPS_DAY)]
        avg.append((sum(past) / len(past), ld[i]))
    evening = defaultdict(float)  # kWh 17:00-21:59 per day
    for r in rows:
        if 17 <= int(r["dt"][11:13]) < 22:
            evening[r["dt"][:10]] += r["load"]
    days = sorted(evening)[1:-1]  # drop partial first/last day
    ev = [evening[d] for d in days]
    ev_err = [abs(b - a) / b for a, b in zip(ev, ev[1:])]
    mean = sum(ld) / len(ld)
    return {
        "load MAE same-as-yesterday, % of mean": 100 * mae(yday) / mean,
        "load MAE mean-of-past-days, % of mean": 100 * mae(avg) / mean,
        "evening 17-22h kWh per day (min / max)": f"{min(ev):.1f} / {max(ev):.1f}",
        "evening kWh same-as-yesterday error, mean %": 100 * sum(ev_err) / len(ev_err),
    }


def over_reserve(rows):
    """Energy still in the battery when morning PV surplus starts, that could have replaced night imports.
    A perfect load forecast lets the optimiser empty the battery to the floor exactly; this is what it could recover."""
    lost_kwh = lost_eur = 0.0
    night_imp, night_cost, prev_surplus = 0.0, 0.0, True
    for r in rows:
        b, g = r["bess"], r["grid"]
        surplus = r["pv"] > r["load"]
        if not surplus:
            night_imp += g["energyImportInterval"]
            night_cost += g["energyImportInterval"] * g["buyPrice"]
        if surplus and not prev_surplus and night_imp > 0:  # first surplus step of the morning
            usable = max(b["soc"] - b["minimumStateOfCharge"], 0) * b["capacityKwh"] * b["dischargeEfficiency"]
            k = min(usable, night_imp)
            lost_kwh += k
            lost_eur += k * night_cost / night_imp
            night_imp = night_cost = 0.0
        prev_surplus = surplus
    return lost_kwh, lost_eur


def soiling(rows, path):
    """PV = clean PV x (1 - dirt) exactly in this simulator (checked A vs B). Energy lost to dirt this week."""
    import json
    raw = {s["datetime"]: s for s in json.loads(path.read_text())}
    lost = lost_lo = lost_hi = 0.0
    dirts = []
    for r in rows:
        d = next(a["pv_dirt"] for a in raw[r["dt"]]["state"]["assets"] if "pv_dirt" in a)
        dirts.append(d)
        e = r["pv"] * d / (1 - d)
        lost += e
        lost_lo += e * r["grid"]["sellPrice"]  # if it would have been exported
        lost_hi += e * r["grid"]["buyPrice"]  # if it would have replaced an import
    rate = (dirts[-1] - dirts[0]) / (len(rows) * DT / 24)
    return dirts[0], dirts[-1], rate, lost, lost_lo, lost_hi


def co2_check():
    ci = hourly_ci(*WEEK)
    hours = sorted(ci)
    yday = [(ci[hours[i - 24]], ci[hours[i]]) for i in range(24, len(hours))]
    mean = sum(ci.values()) / len(ci)
    by_hour = defaultdict(list)
    for h in hours:
        by_hour[int(h[11:13])].append(ci[h])
    prof = {h: sum(v) / len(v) for h, v in by_hour.items()}
    clean, dirty = min(prof, key=prof.get), max(prof, key=prof.get)
    return {
        "CO2 MAE same-as-yesterday, % of mean": 100 * mae(yday) / mean,
        "cleanest / dirtiest hour (avg g/kWh)": f"{clean}h {prof[clean]:.0f} / {dirty}h {prof[dirty]:.0f}",
        "daily swing / mean": (prof[dirty] - prof[clean]) / mean,
    }


def main():
    out = {}
    for name, f in FILES.items():
        path = ROOT / "data/DatasetV3" / f
        rows = load(path)
        for k, v in load_check(rows).items():
            out.setdefault(k, {})[name] = v
        kwh, eur = over_reserve(rows)
        out.setdefault("over-reserve: kWh left at sunrise that could replace night imports", {})[name] = kwh
        out.setdefault("over-reserve: € that a perfect forecast could recover", {})[name] = eur
        d0, d1, rate, lost, lo, hi = soiling(rows, path)
        out.setdefault("dirt start -> end", {})[name] = f"{d0:.3f} -> {d1:.3f}"
        out.setdefault("dirt growth per day", {})[name] = rate
        out.setdefault("PV lost to dirt kWh", {})[name] = lost
        out.setdefault("PV lost to dirt € (export .. import price)", {})[name] = f"{lo:.2f} .. {hi:.2f}"
    print("| Check | A | B |\n|---|---|---|")
    for k, v in out.items():
        f = lambda x: x if isinstance(x, str) else f"{x:.2f}"
        print(f"| {k} | {f(v['A'])} | {f(v['B'])} |")
    print()
    for k, v in co2_check().items():
        print(f"{k}: {v if isinstance(v, str) else f'{v:.2f}'}")
    assert out["dirt growth per day"]["A"] > 0  # soiling grows, no cleaning in the week


if __name__ == "__main__":
    main()
