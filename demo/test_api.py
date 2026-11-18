import os, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from fastapi.testclient import TestClient
import api

c = TestClient(api.app)
bodies = []

def get(url):
    r = c.get(url)
    bodies.append(r.text)
    return r

for m in ("conservative", "upside"):
    for lam in (0.0, 0.1, 0.5):
        r = get(f"/api/run?mode={m}&lambda={lam}")
        assert r.status_code == 200 and len(r.json()["schedule"]) == 672, (m, lam)
assert get("/api/run?mode=conservative&lambda=0.3").status_code == 422
assert get("/api/run?mode=foo&lambda=0.1").status_code == 422
assert get("/api/run?mode=upside&lambda=-0").status_code == 200  # -0.0 must map to the 0.0 file
assert "columns" in get("/api/kpis").json()
cmp = get("/api/compare")
assert cmp.status_code == 200 and len(cmp.json()["t"]) == 672
assert set(cmp.json()["series"]) == {"Static rule", "No battery", "Pilot C", "Pilot A"}
for name in ("memory.json", "gemini_cache.json"):
    for u in (f"/api/{name}", f"/{name}", f"/out/{name}", f"/api/compare/../{name}"):
        r = get(u)
        assert r.status_code != 200 or "knobs" not in r.text[:2000] and "contents" not in r.text[:2000], u

api._cache = (0.0, None)
api.carbon.token = lambda: None
api.carbon.hourly_ci = lambda *a: (_ for _ in ()).throw(AssertionError("network call"))
j = get("/api/live/carbon").json()
assert j["source"] == "constant-0.356" and j["points"] == [], j

env = {}
f = D.parent / ".env"
if f.exists():
    for line in f.read_text().splitlines():
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip("'\"")
for k in ("ENTSO_API", "GEMINI_API_KEY"):
    v = os.environ.get(k) or env.get(k)
    if v:
        assert not any(v in b for b in bodies), f"{k} leaked"
print("api ok")
