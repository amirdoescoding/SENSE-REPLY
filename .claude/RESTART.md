# Restart point

2026-11-18: Branch `demo-sim-engine` (not pushed). Session 2 of 5 is done, with real Gemini answers cached.
- Next: merge or open a PR, then session 3 `demo-api` (FastAPI `/api/run?lambda=&mode=`, `/api/kpis`, `/api/live/carbon`, render.yaml). The API serves `demo/out/*.json`.
- Rerun the engine: `.venv/bin/python -u demo/sim.py` (~6 min, cached answers are free). Checks: `--check`.
