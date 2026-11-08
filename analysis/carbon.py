"""Grid carbon intensity CI_t (gCO2/kWh) for Italy. Stdlib only.

Source order:
1. ENTSO-E "Actual Generation per Production Type" CSV for Italy, saved by hand to
   data/external/entsoe_IT_gen_2026-01.csv  (see docs/KPIS.md for download steps).
   CI_t = sum_k gen_k,t * EF_k / sum_k gen_k,t  (hourly, generation mix, imports ignored).
2. Fallback: one static factor, ISPRA consumption factor 2024 (preliminary) = 198.9 g/kWh,
   ISPRA Rapporti 413/2025 Tabella 1.3 (direct CO2, includes imports at 0 and grid losses).

Run: python3 analysis/carbon.py  -> prints source and CI range.
"""
import csv
import re
from datetime import datetime
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "data/external/entsoe_IT_gen_2026-01.csv"
STATIC = 198.9
STATIC_SRC = "static: ISPRA 2024 prelim. consumption factor 198.9 g/kWh (Rapporti 413/2025, Tab. 1.3)"
# IPCC AR5 WGIII Annex III Table A.III.2 lifecycle medians (gCO2eq/kWh), via secondary reproductions.
# Oil and "other" are not in AR5: 650 / 700 are Electricity Maps-style assumptions. Storage = 0 (no double count).
EF = [
    ("lignite", 820), ("coal", 820), ("gas", 490), ("oil", 650), ("biomass", 230), ("waste", 700),
    ("nuclear", 12), ("geothermal", 38), ("pumped", 0), ("storage", 0), ("hydro", 24),
    ("solar", 48), ("wind", 11), ("marine", 24), ("other renewable", 50), ("other", 700),
]


def ef_for(column):
    c = column.lower()
    return next((v for key, v in EF if key in c), None)


def _hour_key(cell):
    """'05.01.2026 00:00 - 05.01.2026 01:00 (CET/CEST)' or ISO -> 'YYYY-MM-DDTHH'."""
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2})", cell)
    if m:
        d, mo, y, h, _ = m.groups()
        return f"{y}-{mo}-{d}T{h}"
    return datetime.fromisoformat(cell.strip()[:19]).strftime("%Y-%m-%dT%H")


def load_entsoe(path=CSV):
    """Hourly CI dict {'YYYY-MM-DDTHH': g/kWh}. Sub-hourly rows are averaged into the hour."""
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    t_col = next(i for i, h in enumerate(head) if "MTU" in h or "time" in h.lower())
    gen_cols = [(i, ef_for(h)) for i, h in enumerate(head) if "[MW]" in h and "Consumption" not in h and ef_for(h) is not None]
    acc = {}
    for r in rows[1:]:
        num = den = 0.0
        for i, ef in gen_cols:
            try:
                mw = float(r[i])
            except ValueError:  # 'n/e', '-', ''
                continue
            num += mw * ef
            den += mw
        if den > 0:
            acc.setdefault(_hour_key(r[t_col]), []).append(num / den)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def ci_lookup():
    """Return (fn(datetime_str) -> g/kWh, source label, hourly keys or None).
    Dataset time assumed Italian local time (CET). Missing hours fall back to STATIC, so callers check coverage."""
    if CSV.exists():
        ci = load_entsoe(CSV)
        assert ci, f"no usable rows in {CSV}: check the MTU column and [MW] headers"
        return (lambda dt: ci.get(dt[:13], STATIC)), f"ENTSO-E hourly mix x IPCC AR5 lifecycle EFs ({len(ci)} h)", set(ci)
    return (lambda dt: STATIC), STATIC_SRC, None


if __name__ == "__main__":
    fn, src, _ = ci_lookup()
    print("source:", src)
    if CSV.exists():
        vals = list(load_entsoe().values())
        print(f"CI min/mean/max g/kWh: {min(vals):.0f} / {sum(vals) / len(vals):.0f} / {max(vals):.0f}")
        assert 50 < sum(vals) / len(vals) < 600, "CI mean implausible for Italy, check CSV columns"
    assert ef_for("Fossil Gas - Actual Aggregated [MW]") == 490
    assert ef_for("Hydro Pumped Storage - Actual Aggregated [MW]") == 0
    assert ef_for("Other renewable - Actual Aggregated [MW]") == 50
    assert _hour_key("05.01.2026 13:15 - 05.01.2026 13:30 (CET/CEST)") == "2026-01-05T13"
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as t:
        t.write('"Area","MTU","Fossil Gas - Actual Aggregated [MW]","Solar - Actual Aggregated [MW]",'
                '"Hydro Pumped Storage - Actual Consumption [MW]"\n'
                '"IT","05.01.2026 12:00 - 05.01.2026 13:00 (CET/CEST)","500","500","200"\n')
    assert load_entsoe(Path(t.name)) == {"2026-01-05T12": 269.0}  # (500*490+500*48)/1000, pumping ignored
    print("self-check ok")
