"""Grid carbon intensity CI_t (gCO2/kWh) for Italy. Stdlib only.

Source order:
1. ENTSO-E "Aggregated Generation per Type" CSV export(s) for Italy, saved by hand to
   data/external/AGGREGATED_GENERATION_PER_TYPE*.csv (long format, MTU in UTC; split files are merged).
   CI_t = sum_k gen_k,t * EF_k / sum_k gen_k,t  (hourly, generation mix, imports ignored).
2. Fallback: one static factor, ISPRA consumption factor 2024 (preliminary) = 198.9 g/kWh,
   ISPRA Rapporti 413/2025 Tabella 1.3 (direct CO2, includes imports at 0 and grid losses).

Run: python3 analysis/carbon.py  -> prints source and CI range.
"""
import csv
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DIR = Path(__file__).resolve().parent.parent / "data/external"
PATTERN = "AGGREGATED_GENERATION_PER_TYPE*.csv"
LOCAL = ZoneInfo("Europe/Rome")  # dataset timestamps assumed Italian local time
STATIC = 198.9
STATIC_SRC = "static: ISPRA 2024 prelim. consumption factor 198.9 g/kWh (Rapporti 413/2025, Tab. 1.3)"
# IPCC AR5 WGIII Annex III Table A.III.2 lifecycle medians (gCO2eq/kWh), via secondary reproductions.
# Oil and "other" are not in AR5: 650 / 700 are Electricity Maps-style assumptions. Storage = 0 (no double count).
# First keyword match wins, so "Fossil Coal-derived gas" -> coal, "Other renewable" before "other".
EF = [
    ("lignite", 820), ("coal", 820), ("peat", 820), ("gas", 490), ("oil", 650), ("biomass", 230),
    ("waste", 700), ("nuclear", 12), ("geothermal", 38), ("pumped", 0), ("storage", 0), ("hydro", 24),
    ("solar", 48), ("wind", 11), ("marine", 24), ("other renewable", 50), ("other", 700),
]


def ef_for(production_type):
    c = production_type.lower()
    return next((v for key, v in EF if key in c), None)


def _hour_key(mtu):
    """'05/01/2026 13:15:00 - 05/01/2026 13:30:00' (UTC) -> Italian local hour 'YYYY-MM-DDTHH'."""
    utc = datetime.strptime(mtu[:19], "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc)
    return utc.astimezone(LOCAL).strftime("%Y-%m-%dT%H")


def load_entsoe(paths):
    """Hourly CI dict {'YYYY-MM-DDTHH' local: g/kWh}. 15-min mixes are averaged into the hour."""
    num, den = {}, {}  # per 15-min MTU
    for path in paths:
        with Path(path).open(newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                ef = ef_for(r["Production Type"])
                try:
                    mw = float(r["Generation (MW)"])
                except ValueError:  # 'n/e', 'N/A', blank
                    continue
                if ef is None:
                    continue
                mtu = r["MTU (UTC)"]
                num[mtu] = num.get(mtu, 0.0) + mw * ef
                den[mtu] = den.get(mtu, 0.0) + mw
    acc = {}
    for mtu, d in den.items():
        if d > 0:
            acc.setdefault(_hour_key(mtu), []).append(num[mtu] / d)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def ci_lookup():
    """Return (fn(datetime_str) -> g/kWh, source label, hourly keys or None).
    Missing hours fall back to STATIC, so callers check coverage."""
    files = sorted(DIR.glob(PATTERN))
    if files:
        ci = load_entsoe(files)
        assert ci, f"no usable rows in {files}: check 'MTU (UTC)', 'Production Type', 'Generation (MW)' headers"
        src = f"ENTSO-E hourly mix x IPCC AR5 lifecycle EFs ({len(files)} files, {len(ci)} h, UTC->Europe/Rome)"
        return (lambda dt: ci.get(dt[:13], STATIC)), src, set(ci)
    return (lambda dt: STATIC), STATIC_SRC, None


if __name__ == "__main__":
    fn, src, hours = ci_lookup()
    print("source:", src)
    if hours:
        vals = list(load_entsoe(sorted(DIR.glob(PATTERN))).values())
        print(f"CI min/mean/max g/kWh: {min(vals):.0f} / {sum(vals) / len(vals):.0f} / {max(vals):.0f}")
        assert 50 < sum(vals) / len(vals) < 600, "CI mean implausible for Italy, check CSV columns"
    assert ef_for("Fossil Gas") == 490 and ef_for("Fossil Coal-derived gas") == 820
    assert ef_for("Hydro Pumped Storage") == 0 and ef_for("Other renewable") == 50 and ef_for("Other") == 700
    assert _hour_key("05/01/2026 23:15:00 - 05/01/2026 23:30:00") == "2026-01-06T00"  # UTC+1 in January
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as t:
        t.write('"MTU (UTC)","Area","Production Type","Generation (MW)"\n'
                '"05/01/2026 11:00:00 - 05/01/2026 11:15:00","Italy (IT)","Fossil Gas","500"\n'
                '"05/01/2026 11:00:00 - 05/01/2026 11:15:00","Italy (IT)","Solar","500"\n'
                '"05/01/2026 11:00:00 - 05/01/2026 11:15:00","Italy (IT)","Nuclear","n/e"\n')
    assert load_entsoe([t.name]) == {"2026-01-05T12": 269.0}  # (500*490+500*48)/1000, local = UTC+1
    print("self-check ok")
