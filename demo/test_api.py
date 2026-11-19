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

for lam in (0.0, 0.1, 0.5):
    r = get(f"/api/run?lambda={lam}")
    assert r.status_code == 200 and len(r.json()["schedule"]) == 672, lam
assert get("/api/run?lambda=0.3").status_code == 422
assert get("/api/run?lambda=-0").status_code == 200  # -0.0 must map to the 0.0 file
assert get("/api/live?lambda=0.1").status_code in (404, 405)  # the live week is gone (SPA fallback answers GET with 404)
k = get("/api/kpis").json()
assert "columns" in k and set(k["meta"]) == set(k["thresholds"])
r = get("/")  # the SPA must be mounted, else the leak checks below pass on plain 404s
assert r.status_code == 200 and "<div id=\"root\">" in r.text, "demo/web/dist missing: run npm run build"
cmp = get("/api/compare")
assert cmp.status_code == 200 and len(cmp.json()["t"]) == 672
assert set(cmp.json()["series"]) == {"Static rule", "No battery", "Pilot C", "Pilot A"}
for name in ("memory.json", "model_cache.json"):
    for u in (f"/api/{name}", f"/{name}", f"/out/{name}", f"/api/compare/../{name}"):
        r = get(u)
        assert r.status_code != 200 or "knobs" not in r.text[:2000] and "contents" not in r.text[:2000], u

api._cache = (0.0, None)
api.carbon.token = lambda: None
api.carbon.hourly_ci = lambda *a: (_ for _ in ()).throw(AssertionError("network call"))
j = get("/api/live/carbon").json()
assert j["source"] == "constant-0.356" and j["points"] == [], j

# site passcode (Basic auth, any user), health check stays open for Render
api.PASS = b"letmein"
assert c.get("/api/kpis").status_code == 401
assert c.get("/api/kpis", auth=("jury", "nope")).status_code == 401
assert c.get("/api/kpis", headers={"Authorization": "Basic !!!"}).status_code == 401
assert c.get("/api/kpis", auth=("jury", "letmein")).status_code == 200
assert c.get("/healthz").status_code == 200
api.PASS = b""

env = {}
f = D.parent / ".env"
if f.exists():
    for line in f.read_text().splitlines():
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip("'\"")
for k in ("ENTSO_API",):
    v = os.environ.get(k) or env.get(k)
    if v:
        assert not any(v in b for b in bodies), f"{k} leaked"
print("api ok")
