# 06 – Loop engineering, multi-agent vs single agent, learning from outcomes

Date: 2026-11-08. Author: scientific-literature-researcher agent (raw report, lightly trimmed).
Method: about 17 web searches and 2 page fetches, plus reports 01 and 02.

Labels:
- **[V]** = retrieved this session. Mostly abstract or snippet level; full texts not read.
- **[M]** = from memory, unverified. Check before citing.

## 0. Corrections to earlier reports
- **Reflexion:** the 91% pass@1 on HumanEval is for a GPT-4-based agent, against an 80% GPT-4 baseline [V].
- **Debate:** at matched compute, the evidence that debate helps is weak (§2). This strengthens report 02's case for merging the two agents.
- **Citations:** arXiv 2607.04569 and 2603.08477 exist. Their numbers are snippet-level only.

## 1. "Loop engineering": is it an established term?
**Verdict:** it is an informal industry label from June 2026, not an established research term. It has no academic definition.

| Aspect | Finding [V] |
|---|---|
| Definition | "The practice of designing the system that prompts, checks, remembers, and re-runs an AI agent, rather than a person doing that turn by turn" (Machine Learning Mastery). The loop is: act, get feedback, decide. It repeats until a checkable condition is met. |
| Origin | An X post by Peter Steinberger on 7 Jun 2026, then Addy Osmani's essay "Loop Engineering" on 8 Jun 2026. Boris Cherny (Claude Code) is quoted: "My job is to write loops." |
| Lineage | Prompt engineering (2022–24) → context engineering (2025) → harness engineering (early 2026) → loop engineering (2026). |
| Components | A testable goal, tools, context management, termination and escalation rules, memory, and a hard iteration cap. |
| Evidence | Vendor and SEO articles only. No benchmarks. |

The term comes from coding agents, not energy or control. The gateway already runs a 15-min loop. What it lacks is **outcome feedback into the agent**.

Established concepts that cover the user's intent:

| Intent | Concept | Anchor |
|---|---|---|
| Run continuously and learn from outcomes | Closed-loop control with online learning; RL; experiential agents | Reflexion, ExpeL (§4); RL (§5) |
| Self-tuning weights | Adaptive scalarisation; contextual bandits; Bayesian optimisation; preference-conditioned MORL | Yang et al. 2019 |
| Evaluate, then improve | Evaluator-optimizer pattern (Anthropic, "Building Effective Agents", Dec 2024); prompt optimisation | DSPy, OPRO |
| Test on a simulator before deploying | Digital-twin-in-the-loop; sim-to-real | §5 |

Suggested wording: "Loop engineering is an informal 2026 term for the closed-loop / evaluator-optimizer pattern. The rigorous version is online learning with an outcome signal."

## 2. One agent vs multi-agent

| Paper | Year, venue | Key result | Relevance |
|---|---|---|---|
| Smit et al., "Should we be going MAD?" (arXiv 2311.17371) [V] | 2024, ICML | Debate did not reliably beat self-consistency or ensembling out of the box. Tuning the agreement level helped most. | Debate is sensitive to tuning, and ours is untuned and unmeasured. |
| "Reasoning in Token Economies" (arXiv 2406.06461) [V] | 2024, EMNLP | At matched compute, self-consistency often wins. GSM8K: debate 83.0% vs self-consistency 88.2%. | Debate gains come from aggregating more samples. |
| Li et al., "More Agents Is All You Need" (arXiv 2402.05120) [V] | 2024, TMLR | Sample N answers and take a majority vote; accuracy scales with N. | For a scalar kW, use the median of N samples instead of a debate. |
| Tran & Kiela (arXiv 2604.02460) [V, secondary] | 2026 preprint | At an equal token budget, a single agent matches or beats multi-agent. | Supports merging Cost and Sustainability into one agent. |
| BenchAgent (HF 2606.05670) [V, snippet] | 2026 | At most 1 of 6 multi-agent systems beat a single agent. | Same direction; weak provenance. |
| M3MAD-Bench (arXiv 2601.02854) [V, snippet] | 2026 | Debate is +3–7 points where there is headroom, but ties self-consistency at a matched budget. | Mixed. |
| Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" (arXiv 2503.13657) [V] | 2025, NeurIPS | MAST taxonomy: 14 failure modes in 3 groups (specification, inter-agent misalignment, verification). | Our unverified self-scores are a verification failure. |
| Du et al. 2023 (2305.14325); Huang et al. 2023 (2310.01798) [M] | 2023 | Pro-debate claim, and the critique that self-correction fails without external feedback. | Check before citing. |

**Synthesis (moderate confidence):** at the same token budget, role-splitting rarely beats a single agent or self-consistency, and it costs more (8.2 vs 4.4 calls per decision). It is justified only when the roles verify each other, and ours do not.

## 3. Arbitration and self-scores

| Paper | Finding | Relevance |
|---|---|---|
| Panickssery, Bowman, Feng (arXiv 2404.13076, NeurIPS 2024) [V] | LLMs favour their own outputs; self-preference correlates with self-recognition. | Both agents run the same model and score their own proposals. |
| Zheng et al., MT-Bench (arXiv 2306.05685) [V] | Position and verbosity bias. | Randomise order. |
| Ye et al., CALM (arXiv 2410.02736, ICLR 2025) [V] | 12 types of judge bias; robustness-rate metric. | Gives a calibration metric. |
| "Judging the Judges" 2026 [V, snippet] | Style bias dominates and position bias is negligible on new models. | Bias depends on the model, so measure it on Devstral. |
| gTLO (2204.04988); Tercan & Prabhu (2408.13493) | Threshold lexicographic ordering. | Arbitration rule. |

Alternatives to self-scores, ranked:
1. **Simulator-computed scores:** cost = price × flow; resilience = SoC reserve; comfort = unmet load; CO2 = import × CI.
2. **Feasibility filter, then ε-lexicographic choice:** cheapest within ε, with CO2 as the tie-break.
3. **Pareto filter**, then pick by the current weight.
4. **Separate judge model**, pairwise, randomised order, used only for explanations.

**First diagnostic:** Spearman ρ between self-scores and simulator scores. If ρ is low, arbitration is effectively random.

## 4. Learning from outcomes

| Method | Source | Evidence | Fit |
|---|---|---|---|
| Reflexion | Shinn et al. 2303.11366 [V] | Verbal reflections stored in an episodic buffer; 91% vs 80% on HumanEval. | Reflect on delayed regret computed by the simulator, not on self-scores. |
| ExpeL | Zhao et al. 2308.10144 [V] | Extracts insights and retrieves similar successful episodes as few-shot examples. | Closest match to "retrieval over past decisions". |
| Memory management | Xiong et al. 2505.16067 [V] | Errors propagate through memory; a deletion strategy gave about +10%. | Retrieve only outcome-verified cases, and prune. |
| DSPy / MIPROv2 | Khattab et al. 2310.03714 [M] | Optimises the prompt and demonstrations against a metric; needs 50+ examples. | Feasible, using regret on the twin. |
| OPRO / TextGrad | 2309.03409 / 2406.07496 [M] | LLM as the optimiser of prompts. | Verify before citing; no head-to-head benchmark found. |
| Eureka | Ma et al. 2310.12931 [V] | The LLM writes reward code and the simulator scores it. | Pattern: the LLM writes the scalarisation. |

All of this evidence is from text and code tasks; there is no peer-reviewed result for LLM battery dispatch. Test on the twin.

## 5. Self-tuning weights, RL, safety

| Topic | Paper | Finding | Relevance |
|---|---|---|---|
| Preference-conditioned MORL | Yang, Sun, Narasimhan (arXiv 1908.08342, NeurIPS 2019) [V] | One network covers any linear preference (envelope Q-learning). | Matches the MODRL briefing's instant preference switching. |
| Weight tuning for carbon | No direct paper found | Gap. | Frame it as a contextual bandit: context = (price, SoC, CI forecast), reward = −(cost + λ·CO2). LinUCB [M] or offline Bayesian optimisation [M]. Our proposal. |
| RL-tuned MPC weights | IEEE TVT, Mar 2025 [V, snippet] | SAC tunes MPC weights online (battery thermal). | Closest analogue. |
| LLM + MPC | Wu, Ai, Bartels, Li (arXiv 2512.05876) [V] | The LLM maps context to disturbance forecasts for the MPC; online refinement with an O(√(T log T)) regret bound. | Direct template. |
| InstructMPC | arXiv 2504.05946 [V] | The LLM predicts disturbances for a building with battery and PV. | Same pattern. |
| Safe RL | Eichelbeck et al. 2205.06212; Ceusters et al. 2207.03830, 2304.08897; 2503.11696 [V] | Projection layers and shields keep RL safe and still near-optimal. | Pattern for the deterministic safety clamp. |
| Survey | Su et al. 2407.00304 [V] | Safe RL for power systems. | Background. |
| Naive RL warning | arXiv 2609.14776 (from report 01) | MPC reached 99.2% of MILP; SAC did worse than no storage. | RL needs the twin and a shield. |

## 6. LLM + optimiser hybrids for home energy (HEMS)

| Paper | Design | Result |
|---|---|---|
| Jonah et al. 2607.04569 [V, snippet] | LLM calls tools; compared with MILP | 96.7–98.0% of oracle savings. Native function calling gave 100% success; text-parsed actions are much less reliable. |
| El Makroum et al. 2510.26603 [V] | LLM schedules directly | Benchmarked against MILP; % not retrieved. |
| Michelon et al. 2501.07919 [V] | LLM parses preferences into HEMS parameters | 88% parameter accuracy. |
| "Physically Constrained Agentic AI" 2608.09029 | | 18.56% cost gap to optimum for one model. |

No paper was found that reports both MILP-optimality % and token use for an "LLM strategy + MPC setpoints" design. The "~98% fewer tokens" figure is our estimate.

## 7. Agent-level KPIs from the literature
J(·) is the simulator-computed cost over a horizon, a_t is the executed action, and a_t^i is agent i's proposal.

| KPI | Formula | Source |
|---|---|---|
| Orchestrator regret | (1/T) Σ [J(a_t) − min_i J(a_t^i)] | Bandit regret; 2512.05876 |
| Win rate of agent i | (1/T) Σ 1[J(a_t^i) ≤ J(a_t^j) ∀j] | Bespoke |
| Selection share | (1/T) Σ 1[a_t = a_t^i] | Bespoke |
| Oracle capture | (C_base − C_scn)/(C_base − C_oracle) | 2607.04569 |
| Calibration | Spearman ρ(self-score, simulator score); ECE-style binned gap | MLflow [V]; ECE [M] |
| Judge robustness | Share of verdicts unchanged under an order swap | CALM |
| Self-preference gap | mean own self-score − mean simulator-normalised score | Adapted from Panickssery |
| Agreement | (1/T) Σ 1[abs(a^c − a^s) ≤ ε] | Report 02 |
| Value of second agent | ΔJ / Δ(cost per decision) | Report 02 |
| Failure-mode rate | Share of traces with MAST tags | Cemri |

## 8. Ranked: 5 changes to make the framework learn

| # | Change | Evidence | Effect |
|---|---|---|---|
| 1 | Simulator-computed scores + delayed-regret outcome labels + logging; feasibility filter + ε-lexicographic choice | Moderate | Removes the weakest link and gives the outcome signal every later step needs |
| 2 | One multi-objective call; median-of-N only on disagreement; sustainability check only when a threshold trips | Moderate | 8.2 → 2–3 calls per decision |
| 3 | Outcome-filtered memory: k nearest low-regret cases as few-shot, prune, reflect on regret | Moderate (text), weak (energy) | Plausible lower regret at small token cost |
| 4 | Contextual-bandit (or offline Bayesian optimisation) weight tuning on the twin with real CI; later preference-conditioned MORL | Weak–moderate | Adaptive trade-off; a Pareto front instead of 2 points |
| 5 | Hybrid: LLM sets strategy, MPC sets kW, a shield enforces safety; DSPy prompt optimisation against twin regret | Moderate (hybrid) | Biggest token cut, fast, safe offline mode |

Order: 1, then 2 and 5 together, then 3, then 4 (which needs the carbon series).

## References
[V]: 2311.17371; 2406.06461; 2402.05120; 2604.02460; HF 2606.05670; 2601.02854; 2503.01935; 2602.03128; 2503.13657; 2404.13076; 2306.05685; 2410.02736; 2412.05579; mlflow.org/articles/llm-judge-calibration; 2303.11366; 2308.10144; 2505.16067; 2506.06698; 1908.08342; 2310.12931; 2512.05876; 2504.05946; 2205.06212; 2304.08897; 2207.03830; 2503.11696; 2407.00304; 2607.04569; 2510.26603; 2501.07919.
Loop engineering: machinelearningmastery.com/an-introduction-to-loop-engineering/ ; mindstudio.ai/blog/what-is-loop-engineering-autonomous-ai-agent-workflows ; zbrain.ai/loop-engineering/ ; dassum.medium.com/loop-engineering-with-agents-5e9b984e8d8a
[M]: 2305.14325; 2310.01798; 2310.03714; 2309.03409; 2406.07496; LinUCB 1003.0146; Snoek 2012; Guo 2017 (ECE).
(All numeric IDs are arXiv unless noted.)
