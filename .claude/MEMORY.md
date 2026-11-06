# Memory: key facts & decisions

## Dataset (verified 2026-11-06)
- dataset-001 = **Orchestrator + Cost**: 2,948 LLM requests, 11,690,688 input / 418,362 output tokens, mean LLM time 2,355 ms.
- dataset-002 = **Orchestrator + Cost + Sustainability**: 5,472 requests, 20,049,658 input / 770,858 output tokens, 2,486 ms.
- Both use the same model, Devstral 2 123B (Mistral, cloud API, called from the edge gateway).
- Same window: 2026-01-05 11:00 → 2026-01-12 10:45, 15-min samples. 001 = 672 samples; **002 = 671 (one missing)**.
- Samples are ordered newest first, so sort by `datetime`. Grid `cost` and `penalty` are cumulative, so take diffs.
- BESS: 10 kWh, SoC 0.1–0.9, η_charge = η_discharge = 0.95. Site: 9 PV panels, 1 load, 1 grid connection.
- **No emissions/carbon field.** Sustainability KPIs need an external carbon-intensity series.

## Assumptions
- Site location is not stated. Assume Italy (Reply is Italian) and flag it in every deliverable.

## Decisions
- Research outputs go in `docs/research/0N-*.md`. `00-synthesis.md` is the entry point.
- Work happens on branch `research/agent-assessment`, one commit per research report.

## Data checks (2026-11-06), see docs/research/00-synthesis.md
- The `cost` field is NOT cumulative, despite DATA_MODEL.pdf (range −0.003..0.009 €). Recompute the bill as Σ(import·buyPrice − export·sellPrice).
- Prices are time-varying (134 distinct buyPrice values, €0.035–0.132) and identical in both datasets. Violations, throttling and penalty are all 0 in both.
- **The runs are not controlled.** PV is 93.1 kWh (A) vs 69.1 kWh (B), and SoC start is 0.57 (A) vs 0.15 (B). Compare via baselines on each run's own PV/load, plus a terminal-SoC correction.
- Raw bills: A ≈ €3.23, B ≈ €5.15. LLM cost at $0.40/$2.00 per M tokens: A ≈ $5.51/wk, B ≈ $9.56/wk (+73%).

## Decisions
- KPI catalogue = synthesis §2. Baselines: no-battery, rule-based self-consumption, perfect-foresight LP.
