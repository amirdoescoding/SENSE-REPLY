### Research Synthesis: Assessing LLM Edge Agents for Battery Dispatch (Sense Reply BDD)

#### Executive Summary

This briefing condenses the four research reports (`01`–`04`) into what the assessment needs: a KPI catalogue, comparison methodology, market positioning and framework improvements. It also records data checks made on 2026-11-06 that change how the two configurations can be compared.

1. **The two runs are not a controlled experiment.** Both cover 2026-01-05 → 01-12, use the same price series and have zero grid violations. However, PV energy (93.1 vs 69.1 kWh) and starting SoC (0.57 vs 0.15) differ. The raw € bills (A ≈ €3.23, B ≈ €5.15) therefore mix agent behaviour with different sun and different starting conditions. Normalise before you conclude anything (§3).
2. **The data model and the data disagree on `cost`.** The model says it is cumulative. In the data it moves between −0.003 and 0.009 € and does not accumulate. Recompute the bill from `energyImportInterval × buyPrice − energyExportInterval × sellPrice`, and ask Sense Reply what `cost` is.
3. **There is no carbon signal.** Neither the data nor, probably, the agents see grid carbon intensity. The sustainability agent may be optimising a proxy, most likely PV self-consumption. CO2 KPIs need an external series (ENTSO-E A75 for Italy; see `04`).
4. **Inference cost is small but not negligible relative to the bill.** At $0.40 / $2.00 per M tokens, A costs ≈ $5.51/week and B ≈ $9.56/week. The sustainability agent adds +73% LLM cost, mostly from more calls (4.4 → 8.2 per decision), not longer prompts. Against a ~€3–5/week energy bill, inference is the same order of magnitude. That is a key finding for the trade-off matrix.
5. **The market has no auditable multi-KPI evaluation.** Vendors publish "% savings" with unstated baselines. A transparent, baseline-relative, multi-objective KPI report is itself a differentiator (`03`).

#### Section 1: Verified Data Facts

| Item | Config A: dataset-001 (Orch + Cost) | Config B: dataset-002 (Orch + Cost + Sust) |
|---|---|---|
| Samples (15-min) | 672 | 671 (one missing) |
| LLM requests / input tok / output tok | 2,948 / 11.69M / 0.42M | 5,472 / 20.05M / 0.77M |
| Requests per decision | 4.39 | 8.16 |
| Mean LLM latency | 2,355 ms | 2,486 ms |
| PV energy (Σ 9 panels) | 93.13 kWh | 69.12 kWh |
| Load (Σ load·0.25 h) | 105.10 kWh | 104.31 kWh |
| Grid import / export | 63.82 / 45.09 kWh | 60.49 / 17.57 kWh |
| BESS charged / discharged | 46.27 / 39.57 kWh | 48.92 / 40.83 kWh |
| SoC start → end | 0.572 → 0.800 | 0.151 → 0.452 |
| Recomputed energy bill | €3.23 | €5.15 |
| Violations / throttling / penalty | 0 / 0 / €0 | 0 / 0 / €0 |
| buyPrice / sellPrice | time-varying, 134 distinct values, €0.035–0.132; identical series in both | same |

Open questions for Sense Reply:
- Why does PV differ in the same week? Simulated weather seed, `pv_dirt` or faults?
- What is the `cost` field?
- Which inputs does the sustainability agent receive?

#### Section 2: KPI Catalogue (formulas → fields)

Notation: Δt = 0.25 h. Sum over the samples sorted by `datetime`.

| # | KPI | Formula | Fields / source |
|---|---|---|---|
| **Economic** | | | |
| E1 | Net energy cost (€) | Σ(E_imp·π_buy − E_exp·π_sell) | grid `energyImportInterval`, `energyExportInterval`, `buyPrice`, `sellPrice` |
| E2 | SoC-adjusted cost | E1 − (SoC_end − SoC_start)·E_cap·η_d·π̄_buy | + BESS `soc`, `capacityKwh`, `dischargeEfficiency` |
| E3 | Cost per kWh of load | E2 / Σ load·Δt | + building `load` |
| E4 | Savings vs baseline / oracle-capture | (C_base − C_scn)/C_base; (C_base − C_scn)/(C_base − C_oracle) | recomputed baselines (§3) |
| E5 | Price-timing quality | Σ(E_dis·π_buy) / Σ E_dis − Σ(E_chg·π_buy) / Σ E_chg | BESS interval energies, `buyPrice` |
| **Energy / grid** | | | |
| G1 | Self-consumption | (ΣE_pv − ΣE_exp) / ΣE_pv | `pv_energy_interval`, export (Luthander 2015) |
| G2 | Self-sufficiency | 1 − ΣE_imp / ΣE_load | import, load |
| G3 | Peak import | max P_grid⁺ | grid `power` |
| G4 | Penalty exposure | Σ violation / N; Δ `penalty` | grid `violation`, `penalty` (both 0 in this pilot) |
| **Battery** | | | |
| B1 | Realised round-trip efficiency | (ΣE_dis + ΔE_stored) / ΣE_chg | BESS interval energies, `soc`; nominal 0.9025 |
| B2 | Equivalent full cycles | Σ(E_chg + E_dis) / (2·E_cap) | BESS interval energies |
| B3 | Degradation cost | c_deg · ΣE_dis, with c_deg ≈ €0.06–0.15/kWh (assumed) | BESS; `04` §4 |
| B4 | SoC-limit use / headroom | share of t at SoC ≤ 0.1 or ≥ 0.9; mean SoC | `soc`, min/max SoC |
| B5 | Thermal/health | Δ`soh`, max `temperature`, throttling share | BESS |
| **Sustainability** (external input) | | | |
| S1 | Operational CO2 | Σ E_imp,t · CI_t | import + ENTSO-E-derived CI_t (average); assumed Italy |
| S2 | CO2 avoided vs baseline | S1_base − S1_scn | as above |
| S3 | Marginal-factor sensitivity | S1 with flat 400 g/kWh gas marginal | `04` §1.1 |
| **Agent / operational** | | | |
| A1 | LLM cost per decision | (tok_in·p_in + tok_out·p_out) / N | DataIndex.xlsx + price |
| A2 | Calls & tokens per decision | requests/N; tokens/N | DataIndex.xlsx |
| A3 | Decision latency | mean LLM ms × calls/decision (upper bound) | DataIndex.xlsx |
| A4 | Net value per decision | (C_base − C_scn)/N − A1 | E4 + A1 |
| A5 | Dispatch smoothness / flip-rate | share of t with sign(P_t) ≠ sign(P_t−1); mean abs ΔP | BESS `power` |
| **Trade-off** | | | |
| T1 | Marginal abatement cost (€/kg CO2) | (C_B − C_A) / (CO2_A − CO2_B); report "dominated" if signs don't fit | E2, S1 |
| T2 | Total cost of sustainability | ΔE2 + ΔB3 + ΔA1 (energy + wear + inference) | combined |

Not computable from the data: orchestrator agreement, self-score calibration, orchestrator regret. These need the agent proposal logs, which are not in the JSON. Request them as a recommendation.

#### Section 3: Comparison Methodology

- **Baselines:**
  - (i) No battery: P_bess = 0, so grid = load − PV.
  - (ii) Rule-based self-consumption: charge on PV surplus, discharge to cover load, within SoC and power limits and η.
  - (iii) Perfect-foresight LP over the week. Run it twice, once cost-only and once cost + carbon, which gives the attainable Pareto front.
- **Run each baseline on each dataset's own PV/load series.** Then compare configs by *oracle-capture ratio* and *savings vs rule baseline*, not raw €. This neutralises the PV difference (93 vs 69 kWh).
- **Correct for terminal SoC** (E2). B ends with 3 kWh more stored than it started with. A's stored energy rises by about 2.3 kWh.
- **Two configs give two points, not a front.** Report dominance or the MAC, plus the LP Pareto front as context. Do not compute hypervolume.
- **Limits:** one week, one site, one stochastic run per config, January PV. Call the results "pilot evidence".

#### Section 4: Market and Framework Takeaways

- **Competitors** (`03`):
  - Utility-scale optimisers (Fluence, Stem, Tesla) sell revenue uplift.
  - Home/C&I EMS players (gridX, Kraken, Schneider) sell bill savings.
  - LLM-agentic entrants (SigenAgent, Proximal) keep a human confirmation step.
  - Hyperscaler edge runtimes (AWS Greengrass, Azure IoT Operations) ship generic agent runtimes with no energy KPIs.
  - None of them publishes cycling, degradation-adjusted or multi-objective results.
- **Literature** (`01`):
  - LLM home-energy controllers capture about 97–98% of MILP savings in recent preprints, but cost ≠ feasibility. Authors call for a deterministic validator.
  - Marginal, not average, carbon factors decide "emissions avoided".
- **Frameworks** (`02`):
  - "Propose + self-score + arbitrate" is a supervisor/judge pattern.
  - Self-assigned scores are its weakest link: uncalibrated, role-biased, not comparable across agents.

#### Section 5: Shortlist of Framework Improvements

1. **Give the sustainability agent a real carbon signal.** Use a grid carbon-intensity forecast, not a PV proxy.
2. **Use simulator-computed scores, not self-scores.** Compute cost, CO2, resilience reserve and comfort numerically for each proposal, then arbitrate deterministically. Lexicographic: constraints → cost within ε → CO2.
3. **Hybrid control.** The LLM sets strategy (weights, reserve SoC, mode) every 1–4 h or on events. An LP/MPC on the gateway computes the 15-min kW. A deterministic safety clamp sits on top. This gives about −75 to −98% tokens and a cloud-independent fallback.
4. **Cheap token wins.** Prompt caching of the static prefix, compact numeric state, event-triggered invocation, and calling the sustainability agent only when it disagrees with the cost agent.
5. **Observability.** OpenTelemetry GenAI traces into self-hosted Langfuse/Phoenix. Log every proposal, score, choice and applied setpoint, so agreement, regret and calibration become measurable.
6. **Local fallback.** Use a rule/MPC fallback first. A quantised 3–8B model (Gemma, Qwen, Ministral) on Jetson-class hardware is for strategy only.
7. **Learning from history.** Outcome-labelled decision log → nearest-neighbour few-shot retrieval → distillation once multi-site data exist.

#### Section 6: Next Steps

1. Ask Sense Reply about the `cost` field, the PV discrepancy, the sustainability agent's inputs and the proposal logs.
2. Pull the ENTSO-E A75 Italy series for 5–13 Jan 2026 and confirm Devstral 2 pricing on Mistral's page.
3. Build `analysis/`: loader → KPI table → three baselines → LP oracle → trade-off matrix.
