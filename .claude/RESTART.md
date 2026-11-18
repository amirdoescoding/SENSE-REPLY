# Restart point

2026-11-18: Branch `demo-sim-engine` (not pushed, 4 commits). Session 2 of 5 is done except the Gemini answers.
- First: `.venv/bin/python -u demo/sim.py` (about 6 min; it needs `GEMINI_API_KEY` quota). Check `run.log` for "gemini days N/7". Then commit `demo/out/gemini_cache.json` + the refreshed run JSONs.
- If 3.8 Flash keeps returning 503, change `agent.MODEL` (the models are listed via the API; all are free tier).
- Then `.venv/bin/python demo/sim.py --check`, merge, and next session `demo-api` (session 3).
