# 2026-11-08 kpi-framework

## Recap
- 4-agent team: research-analyst (hosting, 05), scientific-literature-researcher (loop/learning, 06), agent-organizer and multi-agent-coordinator (independent redesigns, merged into FRAMEWORK.md).
- `analysis/kpis.py` (stdlib, self-check against synthesis numbers) and `analysis/carbon.py` (ENTSO-E CSV or static ISPRA 198.9 g/kWh; parser self-test).
- `docs/KPIS.md`: KPIs by cost agent / sustainability agent / orchestrator / framework, with now/logs tags and A/B values.
- `docs/FRAMEWORK.md` + diagram (repo PNG/SVG + claude.ai artifact).
- Advisor review caught that the rule baseline borrowed the agent's SoC-dependent limits and ignored wear. Fixed, and the headline was reframed.

## QA
- The `/qa` skill was not run: the repo has no app or site to drive. QA = both scripts' assert self-checks pass, plus the synthetic ENTSO-E CSV test. `/verify` found no declared checks.

## Self-rating: 7/10
- Good: real numbers, baseline bug caught before Monday, every KPI traced to a field or a named source.
- Weak: hourly carbon and LP oracle are still open; the `.excalidraw` export is image-only; several prices in research 05 are estimates.
