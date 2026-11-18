# Restart point

2026-11-19: Branch `demo-polish` (6 commits, not pushed). Session 6 is done: UI/UX polish + QA.
- Next (session 7): **live Gemini calls in the demo**. Test latency, 503 "high demand" and the free-tier quota (gemini-3.5-flash-lite, 500 req/day) in a live run. **If it performs badly, roll back to the original plan: precompute + playback** (what is on main now). Keep the work on its own branch so the rollback is just not merging it.
- Also open: push `demo-polish` + PR; Render deploy (Blueprint, `ENTSO_API` secret, warm up before the demo).
- Run locally: `cd demo/web && npm run build && cd ../.. && .venv/bin/uvicorn --app-dir demo api:app`, then open http://localhost:8000 (`#kpis` for the KPIs tab). An old uvicorn may already hold :8000; it serves the fresh `dist` from disk.
- Checks: `.venv/bin/python demo/sim.py --check` and `.venv/bin/python demo/test_api.py` → "api ok".
