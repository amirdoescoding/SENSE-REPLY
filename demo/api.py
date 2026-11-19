"""Demo API: serves the precomputed sim runs, a cached live ENTSO-E carbon pull, and a live agent week (SSE).

Run: .venv/bin/uvicorn --app-dir demo api:app
Env: DEMO_PASSCODE (Basic auth on the whole site, any user name), GEMINI_API_KEY (live week), LIVE_CAP (runs/day).
"""
import base64
import json
import os
import queue
import secrets
import sys
import threading
import time
from datetime import date, datetime, timedelta, timezone
from functools import cache
from pathlib import Path
from typing import Literal

import anyio
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import carbon  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
DIST = Path(__file__).resolve().parent / "web" / "dist"
app = FastAPI()
app.add_middleware(GZipMiddleware)  # 6 x ~120 KB runs on a slow free instance
_cache = (0.0, None)  # (monotonic time, payload); real data 1 h, fallback 5 min
PASS = os.environ.get("DEMO_PASSCODE", "").encode()
# ponytail: in-memory guard, resets when the free instance sleeps or restarts; Gemini's own 429 is the backstop
_live = dict(owner=0.0, seen=0.0, day=None, runs=0)  # owner = start time of the running week, seen = its last event
_guard = threading.Lock()


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
def run(mode: Literal["conservative", "upside"], lam: float = Query(alias="lambda")):
    if lam not in (0.0, 0.1, 0.5):
        raise HTTPException(422, "lambda must be 0.0, 0.1 or 0.5")
    return FileResponse(OUT / f"run_{mode}_{abs(lam):.1f}.json")  # abs: -0.0 would format as "-0.0"


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


@cache
def _inputs():
    """Run C rows, the memory (committed memory.json) and the rule flows, once per process."""
    import agent
    import sim
    rows = sim.load_run("C")
    return rows, agent.seed_memory(lambda dt: carbon.STATIC), sim.rule_flows(rows, 0.80)


_ci = []


def _carbon():
    """The week's hourly carbon, pulled once. ENTSO-E down: static factor for this run only, retried next run."""
    if not _ci:
        try:
            _ci.append(carbon.ci_lookup()[0])
        except Exception as e:
            print("live carbon fallback:", type(e).__name__)
            return lambda dt: carbon.STATIC
    return _ci[0]


def _work(mode, lam, q, stop, since):
    import agent
    import sim
    from sim import verdict

    def emit(ev, data):
        if stop.is_set():  # the viewer left: don't spend more of the quota
            raise InterruptedError
        with _guard:
            if _live["owner"] == since:
                _live["seen"] = time.monotonic()  # heartbeat: only a week with no event for 10 min goes stale
        q.put((ev, data))
    try:
        rows, mem, rule = _inputs()
        ci = _carbon()
        q.put(("start", dict(mode=mode, lam=lam, model=agent.MODEL, key=bool(agent._key()))))
        f, days = sim.run_ours(rows, mode, lam, ci, mem, live=True, emit=emit)
        k, tok = sim.ours_kpis(rows, f, days, rule)
        k["MAC"] = None  # needs the λ=0 run
        q.put(("done", dict(tokens=tok, kpis={x: dict(value=None if k.get(x) is None else round(k[x], 4),
                                                      verdict=verdict(x, k.get(x))) for x in sim.THRESH})))
    except InterruptedError:
        print("live: viewer left, run stopped", flush=True)
    except Exception as e:
        print("live error:", type(e).__name__, e, flush=True)
        q.put(("error", dict(msg=type(e).__name__)))
    finally:
        with _guard:
            if _live["owner"] == since:  # a stale takeover started a newer run: leave its slot alone
                _live["owner"] = 0.0


@app.get("/api/live")
def live(request: Request, mode: Literal["conservative", "upside"], lam: float = Query(alias="lambda")):
    """One live agent week, streamed as server-sent events: start, stage*, day x7, done (or error)."""
    if request.headers.get("sec-fetch-site", "same-origin") not in ("same-origin", "none"):
        raise HTTPException(403, "live runs start from the demo page only")  # a foreign page can't spend the cap
    if lam not in (0.0, 0.1, 0.5):
        raise HTTPException(422, "lambda must be 0.0, 0.1 or 0.5")
    with _guard:
        if _live["day"] != date.today():
            _live.update(day=date.today(), runs=0)
        if _live["owner"] and time.monotonic() - _live["seen"] < 600:  # no event for 10 min: a stuck run frees the slot
            raise HTTPException(409, "a live run is in progress, try again in a few minutes")
        if _live["runs"] >= int(os.environ.get("LIVE_CAP", 10)):
            raise HTTPException(429, "today's live runs are used up, the replay is still available")
        since = _live["owner"] = _live["seen"] = time.monotonic()
        _live["runs"] += 1
    q, stop = queue.Queue(), threading.Event()
    threading.Thread(target=_work, args=(mode, abs(lam), q, stop, since), daemon=True).start()

    async def stream():  # async, so a viewer leaving cancels it and `finally` stops the worker (a sync one is never closed)
        try:
            while True:
                try:  # the blocking get runs in a thread: the event loop (and the health check) stays free
                    ev, data = await anyio.to_thread.run_sync(q.get, True, 10, abandon_on_cancel=True)
                except queue.Empty:
                    yield ": ping\n\n"  # keeps proxies from closing a quiet stream (Gemini back-off can be 60 s)
                    continue
                yield f"event: {ev}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                if ev in ("done", "error"):
                    return
        finally:
            stop.set()
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True))
