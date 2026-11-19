"""Demo API: serves the precomputed sim runs (Ministral 3 8B replay) and a cached live ENTSO-E carbon pull.

Run: .venv/bin/uvicorn --app-dir demo api:app
Env: DEMO_PASSCODE (Basic auth on the whole site, any user name), ENTSO_API (carbon card).
"""
import base64
import os
import secrets
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import carbon  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
DIST = Path(__file__).resolve().parent / "web" / "dist"
app = FastAPI()
app.add_middleware(GZipMiddleware)  # 3 x ~120 KB runs on a slow free instance
_cache = (0.0, None)  # (monotonic time, payload); real data 1 h, fallback 5 min
PASS = os.environ.get("DEMO_PASSCODE", "").encode()


@app.middleware("http")
async def passcode(request: Request, call_next):
    if PASS and request.url.path != "/healthz":
        h = request.headers.get("authorization", "")
        try:
            ok = h.startswith("Basic ") and secrets.compare_digest(base64.b64decode(h[6:]).partition(b":")[2], PASS)
        except ValueError:
            ok = False
        if not ok:
            return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Sense Reply demo"'})
    return await call_next(request)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/api/run")
def run(lam: float = Query(alias="lambda")):
    if lam not in (0.0, 0.1, 0.5):
        raise HTTPException(422, "lambda must be 0.0, 0.1 or 0.5")
    return FileResponse(OUT / f"run_{abs(lam):.1f}.json")  # abs: -0.0 would format as "-0.0"


@app.get("/api/kpis")
def kpis():
    return FileResponse(OUT / "kpis.json")


@app.get("/api/compare")
def compare():
    return FileResponse(OUT / "compare.json")


@app.get("/api/live/carbon")
def live_carbon():
    global _cache
    if _cache[1] and time.monotonic() - _cache[0] < 3600:
        return _cache[1]
    now = datetime.now(timezone.utc)
    try:
        if not carbon.token():
            raise LookupError
        f = "%Y%m%d%H%M"
        ci = carbon.hourly_ci((now - timedelta(hours=26)).strftime(f), now.strftime(f))
        pts = [{"hour": k, "g_per_kwh": round(ci[k], 1)} for k in sorted(ci)[-24:]]
        if not pts:  # an empty pull must not be cached as real data for an hour
            raise LookupError
        _cache = (time.monotonic(), {"source": "entsoe-a75", "tz": "Europe/Rome", "points": pts, "fetched_at": now.isoformat()})
        return _cache[1]
    except Exception as e:  # the token is in the request URL, so log the type only
        print("carbon fallback:", type(e).__name__)
        # cache the fallback for 5 min so an ENTSO-E outage doesn't make every visitor wait out the timeout
        _cache = (time.monotonic() - 3300, {"source": "constant-0.356", "g_per_kwh": 356, "points": [], "fetched_at": now.isoformat()})
        return _cache[1]


if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True))
