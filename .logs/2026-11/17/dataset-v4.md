# 2026-11-17: DatasetV4 re-analysis and simple proposal

**Recap.**
- Analysed the new dataset-003 (C) and the prompts and assets.
- Used C vs A (same dirt) as the main test, SoC-adjusted and baseline-relative.
- Replaced the guessed wear cost with BSS.json values (20× lower).
- Added timeseries.py.
- Wrote KPIS.md (dashboard, trade-off matrix, teammate reconciliation), TIMESERIES.md, PROPOSAL.md (exec summary + 3-step framework) and research/07 (4 research agents: architect, IoT, LLM architect, research analyst).
- Split into 8 commits on `dataset-v4`.

**Verification.**
- kpis.py asserts pass for A/B (unchanged) and C (bill 2.89, PV 93.06, import 58.73, export 42.87).
- timeseries.py asserts that per-day sums equal the weekly totals.
- forecast_check.py runs (FC2 0.40).

**Skipped.**
- /qa: no web app or CLI to test here.
- Charts: matplotlib is not installed.
- The proposal's energy result is an estimate (not replayed yet; that is in the backlog).

**Self-rating 7/10.**
- Analysis and docs are solid and traceable.
- The proposal's benefit is still argued, not simulated.
- Some hardware and price figures in research/07 are unverified.
