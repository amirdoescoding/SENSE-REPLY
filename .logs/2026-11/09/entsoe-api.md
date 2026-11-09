# 2026-11-09 entsoe-api

## Recap
- `analysis/carbon.py`: ENTSO-E API (A75, Italy) replaces the hand-downloaded CSVs. Stdlib urllib + ElementTree. Token from env/.env. Parser self-test with inline XML, plus an Acknowledgement error test.
- Parity: API hourly CI = old CSV CI on all 216 h (max diff 0.0). `kpis.py` output identical except the source line. CSVs deleted.
- `analysis/forecast_check.py`: CO2 persistence + day-ahead (A69 wind/solar, A65 load) correction. Naive 8.7% → 5.2%, FC2 0.40. Assert keeps naive = 8.69%.
- Docs: KPIS carbon how-to (token, no-token warning), FRAMEWORK §7b result + caveat, ARCHITECTURE.
- `.env` was already gitignored by the user's own commit; my duplicate append was reverted.

## QA
- `/qa` not run: no app to drive. `/verify`: no declared checks. QA = carbon.py self-check, kpis.py asserts, forecast_check asserts, all pass.

## Self-rating: 8/10
- Good: exact parity before deleting data, the model nests the naive model so FC2 is clean, the token never printed.
- Weak: one test week; forecast_check takes ~55 s (3 API calls, no cache); stumbled on ElementTree `iter` + `{*}`.
