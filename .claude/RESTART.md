# Restart point

2026-11-19, session 7.
- **Branches:**
  - `demo-pipeline-cue` = PR #11: the pipeline "now" cue. Ready to merge.
  - `demo-live` (built on the cue, pushed, no PR): the live Gemini week over SSE, the site passcode and the guards.
- **Where I stopped:** all review fixes applied. `demo-live` is pushed (no PR until Render passes). PR #11 includes the cue finish fixes.
- **Next (needs the user): Render measurement.**
  1. Point the Blueprint at `demo-live`.
  2. Set `GEMINI_API_KEY`, `DEMO_PASSCODE` and `ENTSO_API`.
  3. Warm up and run 2 live weeks.
  4. Pass (< ~3 min/week, ≥ 5/7 days from Gemini): open a PR and merge.
  5. Slow: Starter ($7). Bad: don't merge; main stays playback + cue.
- **Run locally:** `cd demo/web && npm run build && cd ../.. && .venv/bin/uvicorn --app-dir demo api:app`, then open http://localhost:8000. "Run the agent live" spends 7 Gemini calls.
- **Checks:**
  - `.venv/bin/python demo/test_api.py` prints "api ok" (live stream via the memory fallback, 409/429/403/401, /healthz);
  - `.venv/bin/python demo/sim.py --check`.
- **Headless checks without the Chrome extension:** scratchpad `cdp.mjs` (CDP over Node's WebSocket). Env `RM=1` emulates reduced motion; `WS=390,2900` sets the window size.
