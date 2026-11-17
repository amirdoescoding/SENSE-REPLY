"""Grid carbon intensity CI_t (gCO2/kWh) for Italy. Stdlib only.

Source order:
1. ENTSO-E Transparency API, "Actual Generation per Production Type" (A75) for Italy (10YIT-GRTN-----B).
   Token: env var ENTSO_API or an ENTSO_API=... line in the repo .env (gitignored).
   CI_t = sum_k gen_k,t * EF_k / sum_k gen_k,t  (15-min mix averaged into the Italian local hour, imports ignored).
2. Fallback when there is no token: one static factor, ISPRA consumption factor 2024 (preliminary) = 198.9 g/kWh,
   ISPRA Rapporti 413/2025 Tabella 1.3 (direct CO2, includes imports at 0 and grid losses).

Run: python3 analysis/carbon.py  -> prints source and CI range.
"""
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
API = "https://web-api.tp.entsoe.eu/api"
IT = "10YIT-GRTN-----B"
WEEK = ("202601050000", "202601140000")  # UTC, covers the dataset window 5-12 Jan with margin
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
# ENTSO-E psrType codes -> production type names (as on the Transparency site)
PSR = {
    "B01": "Biomass", "B02": "Fossil Brown coal/Lignite", "B03": "Fossil Coal-derived gas", "B04": "Fossil Gas",
    "B05": "Fossil Hard coal", "B06": "Fossil Oil", "B07": "Fossil Oil shale", "B08": "Fossil Peat",
    "B09": "Geothermal", "B10": "Hydro Pumped Storage", "B11": "Hydro Run-of-river and pondage",
    "B12": "Hydro Water Reservoir", "B13": "Marine", "B14": "Nuclear", "B15": "Other renewable", "B16": "Solar",
    "B17": "Waste", "B18": "Wind Offshore", "B19": "Wind Onshore", "B20": "Other", "B25": "Energy storage",
}


def ef_for(production_type):
    c = production_type.lower()
    return next((v for key, v in EF if key in c), None)


def token():
    if os.environ.get("ENTSO_API"):
        return os.environ["ENTSO_API"]
    env = ROOT / ".env"
    for line in env.read_text().splitlines() if env.exists() else []:
        k, _, v = line.partition("=")
        if k.strip() == "ENTSO_API":
            return v.strip()
    return None


def _utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def parse(body, side):
    """GL_MarketDocument XML -> {psrType ('' if none): {utc datetime: MW}}.
    Keeps only series with `side` ('inBiddingZone_Domain' = generation, 'outBiddingZone_Domain' = load/consumption).
    Curve A03 skips repeated values, so positions are forward-filled to the end of each Period."""
    root = ET.fromstring(body)
    if root.tag.endswith("Acknowledgement_MarketDocument"):  # API errors come back as HTTP 200 + this document
        raise RuntimeError("ENTSO-E: " + " ".join(t.text or "" for t in root.iterfind(".//{*}text")))
    out = {}
    for ts in root.iterfind(".//{*}TimeSeries"):
        if ts.find(f"{{*}}{side}.mRID") is None:
            continue
        s = out.setdefault(ts.findtext("{*}MktPSRType/{*}psrType", ""), {})
        for per in ts.iterfind(".//{*}Period"):
            t0, t1 = (_utc(per.findtext(f"{{*}}timeInterval/{{*}}{k}")) for k in ("start", "end"))
            step = timedelta(minutes=int(per.findtext("{*}resolution")[2:-1]))  # PT15M / PT60M
            pts = {int(p.findtext("{*}position")): float(p.findtext("{*}quantity")) for p in per.iterfind("{*}Point")}
            q = None
            for i in range((t1 - t0) // step):
                q = pts.get(i + 1, q)
                s[t0 + i * step] = q
    return out


def fetch(params, start, end, side="inBiddingZone_Domain"):
    """One API call; start/end 'YYYYMMDDHHMM' UTC. The token stays out of errors and logs."""
    q = urllib.parse.urlencode({**params, "periodStart": start, "periodEnd": end, "securityToken": token()})
    with urllib.request.urlopen(f"{API}?{q}", timeout=120) as r:
        return parse(r.read(), side)


def hourly(series):
    """{utc datetime: value} -> {'YYYY-MM-DDTHH' Italian local: mean value}."""
    acc = {}
    for t, v in series.items():
        acc.setdefault(t.astimezone(LOCAL).strftime("%Y-%m-%dT%H"), []).append(v)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def ci_mix(gen):
    """{psrType: {t: MW}} -> {t: g/kWh}."""
    num, den = {}, {}
    for psr, s in gen.items():
        ef = ef_for(PSR[psr])
        for t, mw in s.items():
            num[t] = num.get(t, 0.0) + mw * ef
            den[t] = den.get(t, 0.0) + mw
    return {t: num[t] / d for t, d in den.items() if d > 0}


def hourly_ci(start, end):
    return hourly(ci_mix(fetch({"documentType": "A75", "processType": "A16", "in_Domain": IT}, start, end)))


def ci_lookup():
    """Return (fn(datetime_str) -> g/kWh, source label, hourly keys or None).
    Missing hours fall back to STATIC, so callers check coverage."""
    if token():
        ci = hourly_ci(*WEEK)
        src = f"ENTSO-E API A75 hourly mix x IPCC AR5 lifecycle EFs ({len(ci)} h, UTC->Europe/Rome)"
        return (lambda dt: ci.get(dt[:13], STATIC)), src, set(ci)
    return (lambda dt: STATIC), STATIC_SRC, None


if __name__ == "__main__":
    fn, src, hours = ci_lookup()
    print("source:", src)
    if hours:
        vals = [fn(h) for h in hours]
        print(f"CI min/mean/max g/kWh: {min(vals):.0f} / {sum(vals) / len(vals):.0f} / {max(vals):.0f}")
        assert 50 < sum(vals) / len(vals) < 600, "CI mean implausible for Italy, check psrType mapping"
    assert ef_for("Fossil Gas") == 490 and ef_for("Fossil Coal-derived gas") == 820
    assert ef_for("Hydro Pumped Storage") == 0 and ef_for("Other renewable") == 50 and ef_for("Other") == 700
    assert all(ef_for(n) is not None for n in PSR.values())
    sample = """<GL_MarketDocument xmlns="urn:x">
      <TimeSeries><inBiddingZone_Domain.mRID>IT</inBiddingZone_Domain.mRID><MktPSRType><psrType>B04</psrType></MktPSRType>
        <Period><timeInterval><start>2026-01-05T10:00Z</start><end>2026-01-05T11:00Z</end></timeInterval>
        <resolution>PT15M</resolution><Point><position>1</position><quantity>500</quantity></Point></Period></TimeSeries>
      <TimeSeries><inBiddingZone_Domain.mRID>IT</inBiddingZone_Domain.mRID><MktPSRType><psrType>B16</psrType></MktPSRType>
        <Period><timeInterval><start>2026-01-05T10:00Z</start><end>2026-01-05T11:00Z</end></timeInterval>
        <resolution>PT15M</resolution><Point><position>1</position><quantity>500</quantity></Point></Period></TimeSeries>
      <TimeSeries><outBiddingZone_Domain.mRID>IT</outBiddingZone_Domain.mRID><MktPSRType><psrType>B10</psrType></MktPSRType>
        <Period><timeInterval><start>2026-01-05T10:00Z</start><end>2026-01-05T11:00Z</end></timeInterval>
        <resolution>PT15M</resolution><Point><position>1</position><quantity>9999</quantity></Point></Period></TimeSeries>
    </GL_MarketDocument>"""
    gen = parse(sample, "inBiddingZone_Domain")
    assert set(gen) == {"B04", "B16"} and len(gen["B04"]) == 4  # consumption dropped, A03 forward-filled
    assert hourly(ci_mix(gen)) == {"2026-01-05T11": 269.0}  # (500*490+500*48)/1000, local = UTC+1 in January
    try:
        parse('<Acknowledgement_MarketDocument xmlns="urn:y"><Reason><text>No matching data</text></Reason>'
              "</Acknowledgement_MarketDocument>", "inBiddingZone_Domain")
        raise AssertionError("acknowledgement not raised")
    except RuntimeError as e:
        assert "No matching data" in str(e)
    print("self-check ok")
