# demo-api (session 3)

- Planned with graphify plus 4 gstack-style questions: deploy later, `demo/web/`, strict 422, 24 h live carbon with a 1 h cache.
- Five agents at the user's request:
  - fastapi-developer wrote `api.py`;
  - backend-developer wrote the test and `render.yaml`;
  - api-designer, llm-architect and architect-reviewer reviewed.
- Review fixes:
  - `lambda=-0` returned a 500;
  - the ENTSO-E outage fallback is now cached for 5 min;
  - an empty pull is no longer cached;
  - gzip;
  - tz label.
- Engine gaps were deferred to session 4 (see TODOS): price/comparison series and the `carbon_source` label.
- Checks: `demo/test_api.py` passes ("api ok"); `sim.py --check` still passes; live uvicorn returned 24 ENTSO-E points and the second call hit the cache in 14 ms.
- Skipped: /qa, because there is no UI yet (API covered by test_api.py); the Render deploy, per the user.
- Self-rating 8/10: small and well tested. The reviews caught a real 500 and the outage stall. The engine gaps should have been spotted at session 2 close.
