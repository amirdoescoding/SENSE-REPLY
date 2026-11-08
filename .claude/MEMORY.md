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

## KPI work (2026-11-08), see docs/KPIS.md, docs/FRAMEWORK.md
- `analysis/kpis.py` (stdlib) asserts it reproduces synthesis §1 before printing. Rule baseline derives power limits from its own SoC: data follows maxCharge = min(5, (0.9−SoC)·10), fits within 0.08 kW.
- Headline (robust): LLM cost ≈ 7× (A) / 11× (B) the savings vs no battery (~€0.7/wk). Gap to rule baseline is small (€0.40–0.70/wk) and flips for A once wear (c_deg €0.10) is counted, so present it as a sensitivity.
- B vs A, each vs own rule baseline: B €0.30 cheaper, 2.9 kg CO2 cleaner. Total cost of sustainability ≈ €3.3/wk, almost all LLM.
- PV gap partly soiling: `pv_dirt` 0.20 (A) vs 0.42 (B). PV profile peaks 10:00 and runs ~14 h/day: not Italian January. Flag it.
- Static CI = ISPRA 2024 prelim. consumption factor 198.9 g/kWh (Rapporti 413/2025 Tab. 1.3; 2023 = 234.7).
- Devstral 2 retired 2026-07-31 (replacement Mistral Medium 3.5, ~10× Small 4 price). Revolut self-hosts GLM for coding; no "millions" figure found.
- Redesign decision: optimiser sets kW on the edge, 1 strategy LLM every 1–4 h, twin-scored arbiter, clamp, rule floor; sustainability = λ weight, not an agent.
- Web diagram: https://claude.ai/artifact/ENAndsWgSqt9YYqYxMuY9W
