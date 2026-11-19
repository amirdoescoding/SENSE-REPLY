# Restart point

2026-11-19: session 7 closed.
- **Branches:**
  - `demo-pipeline-cue` = PR #11: the pipeline "now" cue. Ready to merge.
  - `demo-live` (built on the cue, pushed, **no PR yet**): the live Gemini week over SSE, the live memory pool, the site passcode and the guards. Deployed on Render free from this branch: https://sense-reply-demo.onrender.com (Basic auth, any user name, password = `DEMO_PASSCODE`).
- **Render measured:** 2:44 / 4:31 / 5:23 per live week, all 7/7 Gemini. The variance is Gemini 503s. The user accepted the free tier.
- **Next:**
  1. Merge PR #11, then open and merge the `demo-live` PR. After the merge, switch the Render branch back to `main`.
  2. When ENTSO-E is back (HTTP 599 all of 2026-11-19), regenerate the replay: `.venv/bin/python demo/sim.py`, 42 Gemini calls, cache misses only where prompts changed. Decide first whether the replay should also use the live memory pool; today it is live-only.
  3. Make `sim.py --check` and `agent.py` fall back to the static factor when ENTSO-E is down, like `api._carbon`.
- **Demo day:**
  - open the site 2–3 min early (the free instance sleeps; the first day is slowest);
  - play at 16× to show each Gemini call pausing on the Agent stage.
- **Render gotcha:** an existing service keeps its old health check path; it must be `/healthz`.
- **Run locally:** `cd demo/web && npm run build && cd ../.. && .venv/bin/uvicorn --app-dir demo api:app`, then open http://localhost:8000. "Run the agent live" spends 7 Gemini calls.
- **Checks:** `.venv/bin/python demo/test_api.py` prints "api ok"; `.venv/bin/python demo/sim.py --check` (needs ENTSO-E).
- **Headless checks:** scratchpad `cdp.mjs` (CDP via Node's WebSocket). It is lost on reboot; it is a ~30-line Node script.
