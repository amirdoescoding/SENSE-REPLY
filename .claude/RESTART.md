# Restart point

2026-11-18: Branch `demo-ui-kpis` (not pushed). Session 5 of 5 is done in code; only the deploy is left.
- Next:
  - push and open a PR (also `demo-ui-sim` if still open);
  - on Render: New → Blueprint from the repo (`render.yaml`), set the `ENTSO_API` secret, check the build log for Node 22 and Python 3.14.0, then open `/#kpis` and check the CO2 card says "ENTSO-E A75";
  - the free instance sleeps: warm it up before the demo.
- Run locally: `cd demo/web && npm run build && cd ../.. && .venv/bin/uvicorn --app-dir demo api:app`, then open http://localhost:8000 (`#kpis` for the KPIs tab).
- Checks: `.venv/bin/python demo/sim.py --check` and `.venv/bin/python demo/test_api.py` → "api ok" (needs `web/dist`).
