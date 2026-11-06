# 01 – Literature review: KPIs and evaluation of LLM multi-agent BESS control (Sense Reply case)

**Method note.** The bgpt `search_papers` tool was not connected in this session, so I used WebSearch only. I ran 8 searches and did not open full texts. That limits what I could verify:
- Items marked **(verified-snippet)** were confirmed in a search result, but only from abstracts or snippets.
- Items marked **(unverified)** come from my background knowledge, or from a snippet I could not cross-check. Check these against the original paper before quoting them.
- I give no DOIs I could not see. Where the DOI is missing, the entry says "DOI (unverified)" or gives an arXiv URL.
- Several arXiv IDs from the searches (26xx.xxxxx) are very recent preprints. Their numbers and claims need a manual check.

---

## 1. Executive summary

- **KPI formulas.** The literature gives a stable set of definitions for self-consumption, self-sufficiency, grid dependency, equivalent full cycles, round-trip efficiency, throughput-based degradation cost and net cost. All of them can be computed from the existing data fields. Emissions need an external grid carbon-intensity series because the dataset has no emissions field. The literature is clear that **marginal** emission factors, not average ones, are the correct basis for "emissions avoided" by a battery (Siler-Evans et al. 2012; Hittinger & Azevedo 2015).
- **LLM controllers.** Peer-reviewed or preprint evaluation of LLM energy controllers is new (2025–2026) and mostly benchmarks against a MILP oracle. Typical findings:
  - The LLM captures most of the MILP savings.
  - Low cost does not guarantee feasibility or safety.
  - Action-format reliability (native function calling versus parsed text) matters.
  - Authors recommend an independent deterministic validator before actuation.
  - Metrics used: cost gap to the optimum, feasibility and constraint violations, model-to-model comparison. Latency and token cost are rarely reported (unverified).
  - I found no paper that benchmarks an LLM against MPC, MILP and RL together on a residential battery.
- **Trade-off assessment.** The standard tools are:
  - Pareto front and hypervolume.
  - Marginal abatement cost, written as ΔCost / ΔCO2 in € per kg CO2 avoided.
  - Weighted-sum (linear scalarization) versus lexicographic/threshold (TLO) methods.
  - Linear scalarization can only reach convex parts of the Pareto front. TLO is a non-linear alternative.
  - With only two configurations, you get two points, not a front. You can only compute a single price of sustainability between A and B, plus its sensitivity to the emission-factor assumption.
- **Coordination quality.** In multi-agent energy systems it is measured indirectly, through system-level cost, constraint violations and the achieved fraction of oracle performance. Agent-level metrics such as agreement rate and win share of the orchestrator pick are bespoke and have no standard.
- **Baselines.** Use three: no battery, rule-based self-consumption (charge from PV surplus, discharge to cover load), and perfect-foresight optimum (MILP/LP). Report "% of oracle value captured" to normalise across weather and load. This is the most robust cross-config metric.

---

## 2. Scope 1: KPI formulas in home/community EMS and BESS evaluation

Notation, mapped to the dataset. Interval Δt = 0.25 h, t = 1..672.
- P_pv: PV power.
- P_load: building load.
- P_bess: battery power. Sign convention to be confirmed; below, positive means charging.
- P_imp, P_exp: grid import and export power, or the E_imp / E_exp interval energies.
- π_buy, π_sell: buyPrice and sellPrice.
- SoC: state of charge. E_cap = 10 kWh. η_c = η_d = 0.95.

### 2.1 Core definitions

**Energy cost / net bill.** Standard in HEMS work; no single source.
C = Σ_t (π_buy,t · E_imp,t − π_sell,t · E_exp,t) + C_penalty
This should match the "cumulative cost" field. Check whether that field already includes the penalty.

**Self-consumption (SC) and self-sufficiency (SS).**
- Luthander, Widén, Nilsson & Palm (2015), Applied Energy 142:80–94 **(verified-snippet)**. The review defines SC as the share of PV production used on site, and SS as the share of consumption covered by PV. Exact wording not checked.
- Formulas:
  - SC = (Σ E_pv − Σ E_exp) / Σ E_pv
  - SS = (Σ E_load − Σ E_imp) / Σ E_load = 1 − grid dependency
- Caveat: with a battery, the energy in the battery at the end of the period is counted as neither. Correct for ΔSoC, or use long enough windows.
- A DTU paper "Re-thinking the definition of self-sufficiency" **(verified-snippet)** argues the Luthander SS definition suits PV-only households and proposes an alternative for systems with storage. Citation details are not verified.

**Grid dependency / import share.** GD = Σ E_imp / Σ E_load.

**Peak import.** P_peak = max_t P_imp,t. Optionally the mean of the top-k daily peaks, or a demand charge.

**Round-trip efficiency (RTE).**
- Nominal: η_c · η_d = 0.9025.
- Realised: RTE = Σ E_discharged / Σ E_charged, using the BESS interval and totals fields.
- Correct for ΔSoC: RTE_adj = (Σ E_dis + ΔE_stored) / Σ E_chg.
- Temperature or throttling may reduce the realised value.

**Equivalent full cycles (EFC).**
EFC = Σ (E_chg + E_dis) / (2 · E_cap)
Many papers use discharge throughput only: EFC = Σ E_dis / E_cap. State which one you use. The usable window is 0.8 × 10 = 8 kWh, so the usable-capacity variant divides by 8.

**Battery degradation cost.** Three families:
1. *Throughput / amortised replacement cost.*
   - C_deg = (C_batt / (2 · N_life · E_cap · DoD)) · Σ (E_chg + E_dis), or equivalently c_deg [€/kWh] · Σ E_dis.
   - Example from a search snippet **(verified-snippet, source unclear)**: a $200/kWh pack with 2000 rated cycles gives about $100/MWh per full cycle.
   - A caveat from the same snippet: this approach does not maximise the profit or utilisation of the battery over its lifetime.
2. *Marginal degradation cost.* Values the loss of future opportunity (He et al., cited in the snippet). Related: "Power System Dispatch with Marginal Degradation Cost of Battery Storage", arXiv:1904.07771 **(verified-snippet)**.
3. *DoD / Wöhler-Miner cycle-life models.* Cycle life N(DoD) = a · DoD^(−b); damage D = Σ n_i / N_i with rainflow counting **(verified-snippet, from an open-source implementation and a 2026 preprint, arXiv:2609.12968)**.

For a one-week window, family 1 is the only practical choice. Use data-sheet cycle life, which is an assumption you must state.

**Penalty / violation metrics.** Defined by the case's own fields:
- Violation rate = (number of intervals with violation flag = 1) / 672.
- Total penalty = last cumulative penalty value.
- Optionally also count SoC-limit breaches, power-limit breaches and throttling events computed from the data.
- Papers on LLM controllers report these as feasibility or constraint-violation counts (see section 3).

**Emissions.**
- Operational emissions: CO2 = Σ_t E_imp,t · EF_t. EF_t is the grid carbon intensity at time t. You must source this externally, since the dataset has none (for example an Italian grid intensity series from Terna, ENTSO-E or Electricity Maps; not verified).
- Avoided emissions versus a counterfactual: CO2_avoided = CO2_baseline − CO2_scenario. Baseline = no-battery or rule-based.
- **Average versus marginal.**
  - Siler-Evans, Azevedo & Morgan (2012) **(verified-snippet)**: average emission factors "may badly misstate" emissions avoided by an intervention, and regional marginal factors vary widely. Full details: "Marginal Emissions Factors for the US Electricity System", Environ. Sci. Technol. 46(9):4742–4748 (DOI unverified). A PDF copy is at watttime.org.
  - Hittinger & Azevedo (2015) **(verified-snippet, via secondary summaries)**: storage doing energy arbitrage in US wholesale markets could raise CO2 emissions, because it charges at night when coal is at the margin and discharges by day. This depends on region and may change as grids decarbonise. Citation: Hittinger & Azevedo, "Bulk energy storage increases United States electricity system emissions", Environ. Sci. Technol. 49(5):3203–3210, 2015 (DOI unverified).
  - A 2019 study found that charging when grid emissions are low and discharging when they are high can save more carbon than manufacture emits **(verified-snippet, source not identified)**. A 2026 preprint on marginal emission intensity for carbon-aware storage dispatch also criticises storage studies that use average intensity (arXiv:2506.16454 appeared in the results; relation unverified).
- Practical consequence for this case: if you only have an average intensity (for example from a public series), label the result "average-intensity emissions, an upper-bound proxy". A cheap sensitivity check is to run the comparison with both an average and a marginal factor series.

### 2.2 KPI catalogue

| KPI | Formula | Data fields needed | Source |
|---|---|---|---|
| Net energy cost | Σ(π_buy·E_imp − π_sell·E_exp) + penalty | import/export energy, buyPrice, sellPrice, cumulative penalty (or cumulative cost) | Standard HEMS practice (no single source) |
| Cost saving vs baseline | (C_base − C_scn) / C_base | as above, per scenario | Standard |
| Self-consumption | (ΣE_pv − ΣE_exp) / ΣE_pv | PV energy, export energy | Luthander et al. 2015 |
| Self-sufficiency | 1 − ΣE_imp / ΣE_load | load, import energy | Luthander et al. 2015 (DTU critique for storage cases) |
| Grid dependency | ΣE_imp / ΣE_load | import, load | Derived (= 1 − SS) |
| Peak import | max P_imp (or mean of daily maxima) | grid power | Standard |
| Realised RTE | ΣE_dis / ΣE_chg (ΔSoC corrected) | BESS energy charged/discharged, SoC | Derived; nominal 0.9025 from case parameters |
| Equivalent full cycles | Σ(E_chg + E_dis) / (2·E_cap) | BESS energy charged/discharged | Standard (convention must be stated) |
| Throughput degradation cost | c_deg · Σ E_dis, or C_batt/(2·N_life·E_cap) · ΣE_throughput | BESS energy; assumed C_batt, N_life | Amortised-replacement family (e.g. arXiv:1904.07771 for the marginal variant) |
| SoC-limit compliance | share of t with 0.1 ≤ SoC ≤ 0.9 | SoC | Derived from case spec |
| Violation rate / penalty | count(flag)/672; final cumulative penalty | violation flag, cumulative penalty | Case fields; feasibility metric in LLM-HEMS papers |
| Throttling share | share of t with throttling = 1 | BESS throttling, temperature | Case field |
| Operational CO2 | Σ E_imp,t · EF_t | import energy + **external** EF series | Siler-Evans et al. 2012 (EF choice) |
| CO2 avoided | CO2_base − CO2_scn | as above, two scenarios | Hittinger & Azevedo 2015 (marginal logic) |
| Marginal abatement cost | (C_B − C_A) / (CO2_A − CO2_B) [€/kg] | cost and CO2 for A and B | Standard economics; see section 4 |
| Oracle-capture ratio | (C_base − C_scn) / (C_base − C_oracle) | all three runs | Used in LLM-HEMS benchmarks (section 3) |
| Decision flip-rate / smoothness | share of t with sign(P_t) ≠ sign(P_{t−1}); mean abs ΔP | BESS power | Derived (no standard definition found) |
| Orchestrator agreement | share of t where selected proposal = cost agent's proposal | agent proposals (dataset-002 logs) | Derived (see section 5) |

---

## 3. Scope 2: Evaluating LLM agents as energy/BESS controllers (2023–2026)

All items below are **(verified-snippet)** unless stated. Check the claimed numbers against the full PDFs.

1. **"LLMs for Agentic Home Energy Management"**, Jonah et al., arXiv:2607.04569 (July 2026). https://arxiv.org/abs/2607.04569
   - Five LLM backends against a MILP benchmark, across tariff days, constraint conflicts, weather-aware scheduling and a 7-day deployment.
   - Native function calling reaches near-optimal cost on ordinary days. Text-parsed actions are less reliable.
   - Over seven days the agents captured 96.7–98.0 % of the savings between an off-peak timer and the MILP oracle, and beat rule-based policies.
   - "Low cost does not guarantee feasible or safe behaviour." The authors recommend an independent deterministic feasibility validator before actuation.
   - Metrics: cost gap and savings captured versus the oracle, feasibility under conflicts, model comparison. This is the closest analogue to your evaluation design.
2. **"Agentic AI Home Energy Management System: A LLM Framework for Residential Load Scheduling"**, El Makroum et al., arXiv:2510.26603 (2025). https://arxiv.org/pdf/2510.26603
   - Uses a MILP benchmark. The evaluation did not test cases where calendar constraints conflict with cost minimisation (flagged as future work).
3. **"Physically Constrained Agentic AI for Energy Scheduling"**, arXiv:2608.09029 (2026). https://arxiv.org/pdf/2608.09029
   - Reports an 18.56 % cost gap to the matched optimum for one model under the occupied-window policy (snippet only).
4. **HEMA**, arXiv:2602.15219 (2026): multi-agent assistant for home energy management; not a direct MILP comparison. https://arxiv.org/pdf/2602.15219
5. **Behavioural generative agents, home-battery testbed**, arXiv:2603.08477 (March 2026). https://arxiv.org/abs/2603.08477
   - Random prices and blackout events; LLM decisions compared with dynamic programming.
   - With blackout examples in context the LLM learned to discharge fully during blackouts and keep more reserve afterwards, departing from profit-maximising DP behaviour. Relevant to your "resilience" score.
6. **Classical comparators** for baseline choice:
   - "Comparative Evaluation of MILP, MPC, and Reinforcement Learning for Commercial Battery Dispatch Under Time-of-Use Tariffs", arXiv:2609.14776. Perfect-foresight MILP is the oracle. Persistence-based MPC reached 99.2 % of the MILP benchmark. SAC RL did worse than the no-storage baseline. https://arxiv.org/pdf/2609.14776
   - Benchmarking deep RL for battery dispatch (BNAIC 2024 paper and an IEEE version from Leiden, authors/DOI unverified).
   - Schonenberg et al., residential HEMS benchmark (MILP, RL, heat pump): MILP best, MDQL close; the authors note the field lacks a common benchmark problem setting. Full citation unverified.
7. **LLM + MARL for P2P energy trading**, arXiv:2507.14995. The LLM generates expert strategies that agents imitate. It reports lower economic cost and voltage violation rates. https://arxiv.org/pdf/2507.14995

**Metrics seen across these papers:** cost, gap to the MILP oracle, percentage of savings captured, feasibility or constraint violations, robustness under conflicting constraints, comparison across LLM backends. I found no standard definitions of decision consistency, latency or token cost. Those need to be defined by you. Suggested definitions:
- Consistency: variance of P_bess across repeated runs with identical inputs (needs repeated calls at temperature > 0), or the flip-rate in the catalogue.
- Latency: p50/p95 call time per decision, against the 15-minute window.
- Token cost: tokens per decision × price per token.

**Gap.** None of the papers above evaluates a 123B open-weights model from an edge gateway, or a multi-agent cost/sustainability setup with self-assigned scores (unverified as a claim of absence).

---

## 4. Scope 3: Multi-objective trade-off assessment

- **Pareto front and hypervolume.** Standard references: Roijers, Vamplew, Whiteson & Dazeley, "A Survey of Multi-Objective Sequential Decision-Making", JAIR 48 (2013), arXiv:1402.0590 **(verified-snippet)**. https://jair.org/index.php/jair/article/view/10836 Hypervolume HV = volume of objective space dominated by the solution set and bounded by a reference point. Needs several non-dominated solutions. With A and B only, you can say "B dominates A", "A dominates B" or "neither" on (cost, CO2). Do not report hypervolume from two points.
- **Marginal abatement cost / price of sustainability.**
  - MAC = (C_B − C_A) / (CO2_A − CO2_B) in € per kg CO2 avoided, where B is the sustainability-aware config.
  - If B costs more and emits less, MAC is positive: compare with a carbon price (for example EU ETS, value unverified) to judge whether it is acceptable.
  - If B costs less and emits more, or both costs and emissions go up, the sign logic changes. Report "dominated" rather than a number.
  - A German industry study of storage dispatch found a minimum mean CO2 abatement cost of about €14.13 per tonne across 50 firms **(verified-snippet, source not identified)** and compared several dynamic emission factors, average and marginal. Useful as an order of magnitude only.
  - Since a one-week sample with a small battery gives tiny absolute differences, report per-kWh and per-week values and give uncertainty.
- **Weighted-sum versus lexicographic.**
  - Linear scalarization only reaches solutions on convex parts of the Pareto front. Thresholded Lexicographic Ordering (TLO) is a non-linear alternative that handles constraint-like objectives first (Gábor et al., TLQ; Dornheim et al., gTLO, arXiv:2204.04988 **(verified-snippet)**; Tercan & Prabhu, arXiv:2408.13493 **(verified-snippet)**, noting that such methods are heuristics without Bellman-equation guarantees).
  - **Nguyen et al. link.** I could not retrieve the Nguyen et al. paper in this session. My recollection is T. T. Nguyen, N. D. Nguyen, P. Vamplew, S. Nahavandi, R. Dazeley, C. P. Lim, "A multi-objective deep reinforcement learning framework", Engineering Applications of AI 96 (2020), arXiv:1803.02965 **(unverified)**. A search result described a deep TLQ + DQN work as "dTLQ" without confirming authorship. If your case brief cites a linear-versus-TLO insight from Nguyen et al., use that wording and verify the page and claim yourself.
  - Mapping to the case: the orchestrator picking one proposal by a weighted combination of self-assigned scores is a linear scalarization. The lexicographic alternative would be: first enforce hard constraints (SoC, power limits, resilience reserve), then minimise cost, then use sustainability as a tie-breaker within a cost threshold ε. The ε-threshold plays the role of the TLO threshold and also gives a Pareto sweep.
  - A 2024–25 empirical study of scalarization limits in discrete MORL **(verified-snippet, title "Limitations of Scalarisation in MORL: A Comparative Study in Discrete Environments")** found linear scalarization beat Chebyshev on hypervolume in its environments, but weight sweeps are costly and many weights converge to identical solutions. So linear weights are not always inferior; the claim depends on front shape.
- **Practical test for your data.** Sweep the sustainability weight in a re-run or replay of the orchestrator (offline, using the logged proposals) to build a front (cost, CO2). See whether any point lies in a non-convex region.

---

## 5. Scope 4: Multi-agent negotiation/arbitration in energy

- **EnergyTwin** (arXiv:2511.20590, Nov 2025). Asset agents negotiate with a central agent that forecasts and allocates energy via contracts; rolling-horizon planning; tested on a campus microgrid. No LLM evident from the snippet. https://arxiv.org/pdf/2511.20590 **(verified-snippet)**
- **Agentic AI microgrid framework** (Islam, IEOM 2026 proceedings). An LLM orchestrator coordinates specialised agents across planning, supervision and execution; emphasis on human-reviewed safe operation. https://ieomsociety.org/proceedings/milwaukee2026/158.pdf **(verified-snippet; check authorship)**
- **CoSSMic** (EU project): software agents for collaborating consumers and producers negotiating energy peer-to-peer **(verified-snippet; no citation)**.
- **Stackelberg, voting, consensus.** I found no source on these in this session. Background knowledge: Stackelberg leader-follower games are widely used for prosumer-aggregator pricing (typical refs: Maharjan et al., IEEE Trans. Smart Grid 2013; details unverified). Treat as general background, not as verified citation.
- **How coordination quality is measured.** In what I found it is system-level (cost, violations, share of oracle value). Candidate case-specific agent metrics, none standard:
  - Selection share: fraction of intervals where each agent's proposal is chosen.
  - Disagreement magnitude: |P_cost − P_sust| at each step.
  - Score calibration: correlation between an agent's self-assigned score and the realised outcome of its proposal (replay in a simulator).
  - Orchestrator regret: outcome of the chosen proposal versus the best proposal ex post.
  - Self-score inflation: do agents' self-assigned scores differ systematically? Self-assigned scores are not comparable across agents, so they are weak evidence for selection.

---

## 6. Scope 5: Counterfactual baselines and normalisation

- **Baselines (use all three).**
  1. *No battery.* Grid-only with PV; computable directly from P_pv, P_load and prices. Gives the battery's total value.
  2. *Rule-based self-consumption.* Charge with PV surplus, discharge to cover load, respecting SoC limits and η. This is the usual HEMS baseline; the LLM-HEMS paper above used an off-peak timer and rule-based policies.
  3. *Perfect-foresight optimum.* LP/MILP over the 672 intervals with the same constraints. Practical upper bound on savings (as in arXiv:2609.14776 and arXiv:2607.04569). Run it twice, with cost-only objective and with cost + carbon objective, to obtain the full Pareto front of what is attainable.
  4. Optional: MPC with a persistence forecast (realistic non-LLM comparator; reached 99.2 % of the MILP in arXiv:2609.14776 **(verified-snippet)**).
- **Normalisation when weather/load differ.** The two configs ran over the same week, which controls weather, load and prices. That is the strongest design point of the case, so state it. If you must compare across weeks:
  - Use the oracle-capture ratio, (C_base − C_scn) / (C_base − C_oracle), not absolute euros.
  - Report cost per kWh of load and CO2 per kWh of load.
  - Correct for end-of-period SoC difference by valuing ΔE_stored at the average buy price (or at the mean price paid for stored energy).
- **Caveats.** Same-week comparison still has a single-sample, single-run limit: LLM decisions are stochastic. Without repeated runs you cannot separate config effect from sampling noise. One week in January also has low PV, which limits how much the battery can matter.

---

## 7. Implications for our assessment

1. Compute the KPI catalogue from the data fields for both datasets, plus the three baselines, and report each as a delta versus the baseline.
2. State clearly that there is **no emissions field**. Bring in an external hourly grid carbon-intensity series for Italy and run the CO2 analysis with both average and marginal intensity (or two alternative series) as a sensitivity check. Label CO2 results as modelled, not measured.
3. Compare A and B on (cost, CO2). Report dominance if there is one; otherwise report MAC in € per kg CO2 avoided with a carbon-price comparison. Do not report hypervolume for two points. Instead, build a Pareto front from the replayed orchestrator weight sweep and the oracle LP.
4. If B (sustainability agent) shows no CO2 benefit, check whether it is because the dataset has no carbon signal available to the agents in the first place (a data-design flaw rather than an agent flaw). Without an emissions signal, "sustainability" is likely proxied by PV self-consumption, which can conflict with the true marginal-emissions effect (Hittinger & Azevedo).
5. Use the lexicographic idea for improvements: hard constraints first (SoC, power, resilience reserve), then cost within an ε threshold, then sustainability. Add a deterministic feasibility validator before actuation, as recommended in arXiv:2607.04569.
6. Add LLM-specific KPIs: violation rate, flip-rate/smoothness, latency per decision against the 15-minute window, tokens and token cost per decision, agreement share and orchestrator regret. Replay the same inputs several times to estimate decision variance.
7. Treat self-assigned scores as uncalibrated. Recommend replacing them with scores computed by the environment (predicted cost, predicted CO2, SoC reserve) or with a calibration check against realised outcomes.
8. Account for degradation: compute EFC and an assumed throughput cost per kWh. A config with lower bill but much higher cycling may not be better after degradation cost. State the C_batt and N_life assumptions.
9. Be explicit about limits: one week, one site, one run per configuration, winter PV, and unverified claims noted above.

---

## 8. References

Verified at snippet level (abstract or search result only; full texts not read):
- Luthander, R., Widén, J., Nilsson, D., Palm, J. (2015). Photovoltaic self-consumption in buildings: A review. *Applied Energy* 142, 80–94. https://ideas.repec.org/a/eee/appene/v142y2015icp80-94.html (DOI unverified)
- Roijers, D. M., Vamplew, P., Whiteson, S., Dazeley, R. (2013). A Survey of Multi-Objective Sequential Decision-Making. *JAIR* 48. arXiv:1402.0590. https://jair.org/index.php/jair/article/view/10836
- Dornheim et al. (2022). gTLO: A Generalized and Non-linear Multi-Objective Deep RL Approach. arXiv:2204.04988. (Author list unverified.)
- Tercan, H., Prabhu, V. (2024). Thresholded Lexicographic Ordered Multiobjective Reinforcement Learning. arXiv:2408.13493. (Author names taken from the snippet; check.)
- Jonah et al. (2026). LLMs for Agentic Home Energy Management. arXiv:2607.04569. https://arxiv.org/abs/2607.04569
- El Makroum et al. (2025). Agentic AI Home Energy Management System: A LLM Framework for Residential Load Scheduling. arXiv:2510.26603.
- Physically Constrained Agentic AI for Energy Scheduling (2026). arXiv:2608.09029. (Authors not retrieved.)
- HEMA (2026). arXiv:2602.15219. (Title and authors incomplete.)
- Behavioural generative agents for home battery (2026). arXiv:2603.08477. (Title and authors not retrieved.)
- Comparative Evaluation of MILP, MPC, and Reinforcement Learning for Commercial Battery Dispatch Under Time-of-Use Tariffs (2026). arXiv:2609.14776.
- LLM-enhanced MARL for P2P energy trading (2025). arXiv:2507.14995. (Title and authors not retrieved.)
- EnergyTwin: A Multi-Agent System for Simulating and Coordinating Energy Microgrids (2025). arXiv:2511.20590.
- Islam (2026). Agentic AI microgrid framework. IEOM Society proceedings, Milwaukee 2026. https://ieomsociety.org/proceedings/milwaukee2026/158.pdf (title and authorship unverified)
- Power System Dispatch with Marginal Degradation Cost of Battery Storage (2019). arXiv:1904.07771. (Authors not retrieved.)
- End-to-End Battery Dispatch with Exact Rainflow Degradation via Mixed-Integer Differentiable Predictive Control (2026). arXiv:2609.12968.

From background knowledge, not verified in this session (check before citing):
- Siler-Evans, K., Azevedo, I. L., Morgan, M. G. (2012). Marginal Emissions Factors for the US Electricity System. *Environ. Sci. Technol.* 46(9), 4742–4748. (Existence confirmed via snippet that references it; DOI unverified.)
- Hittinger, E., Azevedo, I. M. L. (2015). Bulk energy storage increases United States electricity system emissions. *Environ. Sci. Technol.* 49(5), 3203–3210. (Findings seen only in secondary summaries.)
- Nguyen, T. T., Nguyen, N. D., Vamplew, P., Nahavandi, S., Dazeley, R., Lim, C. P. (2020). A multi-objective deep reinforcement learning framework. *Eng. Appl. Artif. Intell.* 96, 103915; arXiv:1803.02965. (unverified)
- Maharjan, S. et al. (2013). Dependable demand response management in the smart grid: A Stackelberg game approach. *IEEE Trans. Smart Grid* 4(1). (unverified)
- Schonenberg et al., residential HEMS benchmark with MILP and RL (year and venue unverified).
- Benchmarking Deep RL for Battery Dispatch Optimisation, BNAIC 2024 / Leiden IEEE version (authors unverified).
