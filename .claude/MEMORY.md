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
