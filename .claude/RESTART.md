# Restart point

2026-11-18: Branch `demo-ui-sim` (not pushed). Session 4 of 5 is done.
- Next:
  - push and open a PR;
  - then session 5 `demo-ui-kpis`: the KPI table, the live ENTSO-E card, and the Render deploy.
  - Read "Session 5 inputs" under session 4 in `.claude/TODOS.md` first.
- Run locally:
  - prod-like: `cd demo/web && npm run build && cd ../.. && .venv/bin/uvicorn --app-dir demo api:app`, then open http://localhost:8000;
  - dev: run uvicorn plus `cd demo/web && npm run dev`, then open http://localhost:5173.
- Checks: `.venv/bin/python demo/sim.py --check` and `.venv/bin/python demo/test_api.py` → "api ok".
