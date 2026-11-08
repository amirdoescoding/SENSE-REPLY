# Backlog

- [x] Research sprint → `docs/research/00..04`
- [ ] Ask Sense Reply: meaning of the `cost` field, why PV differs between runs, sustainability agent inputs, agent proposal logs
- [x] KPI catalogue → `docs/KPIS.md` (team to agree at Monday consolidation)
- [ ] Download ENTSO-E Italy generation CSV to `data/external/entsoe_IT_gen_2026-01.csv` (steps in KPIS.md); send API-token email. Devstral 2 retired 2026-07-31, price stays aggregator-only
- [x] `analysis/kpis.py` loader
- [x] KPIs per config (`analysis/kpis.py`)
- [ ] KPIs per day
- [x] Baselines: no-battery, rule-based (+30% reserve variant)
- [ ] Perfect-foresight LP oracle (needs `pip install scipy` approval)
- [ ] Time-series analysis: dispatch vs price, SoC, grid profiles, anomalies
- [x] Trade-off T1/T2 (B vs A, baseline-relative)
- [ ] Re-run carbon KPIs with hourly ENTSO-E CI
- [ ] KPI dashboard
- [ ] Executive summary + recommendations
- [x] Framework redesign → `docs/FRAMEWORK.md` + diagram
- [ ] Ask Sense Reply: PV clock (peak 10:00, 14 h/day in Jan), site location, twin accuracy, target fleet size
