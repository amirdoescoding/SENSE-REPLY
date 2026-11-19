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
k = get("/api/kpis").json()
assert "columns" in k and set(k["meta"]) == set(k["thresholds"])
r = get("/")  # the SPA must be mounted, else the leak checks below pass on plain 404s
assert r.status_code == 200 and "<div id=\"root\">" in r.text, "demo/web/dist missing: run npm run build"
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

# live week, no key: the memory fallback runs, so no quota is spent (and no network: token patched above)
import agent, time  # noqa: E401
agent._key = lambda: None
r = c.get("/api/live?mode=conservative&lambda=0.1")
assert r.status_code == 200 and r.headers["content-type"].startswith("text/event-stream")
ev = [l[7:] for l in r.text.splitlines() if l.startswith("event: ")]
assert ev[0] == "start" and ev.count("day") == 7 and ev[-1] == "done" and "stage" in ev, ev
done = __import__("json").loads(r.text.rsplit("data: ", 1)[1])
assert done["kpis"]["N1"]["value"] is not None and done["tokens"]["calls"] == 0, done
bodies.append(r.text)
time.sleep(0.2)
assert api._live["busy"] == 0.0
api._live["busy"] = time.monotonic()
assert c.get("/api/live?mode=upside&lambda=0").status_code == 409
api._live.update(busy=0.0, runs=99)
assert c.get("/api/live?mode=upside&lambda=0").status_code == 429
assert c.get("/api/live?mode=upside&lambda=0.3").status_code == 422
api._live["runs"] = 0

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
for k in ("ENTSO_API", "GEMINI_API_KEY"):
    v = os.environ.get(k) or env.get(k)
    if v:
        assert not any(v in b for b in bodies), f"{k} leaked"
print("api ok")
