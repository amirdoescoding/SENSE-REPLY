# Restart point

2026-11-18: Branch `demo-api` (not pushed). Session 3 of 5 is done.
- Next: merge or open a PR, then session 4 `demo-ui-sim` (Vite/React in `demo/web/`, three.js site, agent-flow pipeline, playback, λ slider). Read the "Session 4 inputs" under session 3 in `.claude/TODOS.md` first: price/comparison series and the carbon label are engine fixes.
- Run the API: `.venv/bin/uvicorn --app-dir demo api:app`. Check: `.venv/bin/python demo/test_api.py` → "api ok".
