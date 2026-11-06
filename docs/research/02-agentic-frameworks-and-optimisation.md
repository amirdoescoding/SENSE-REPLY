# 02 – Agentic frameworks, evaluation and optimisation

> Editor's note: this report divides config B by 672 samples. dataset-002 actually has 671, so B's per-sample figures are about 0.15% low (e.g. 8.16 rather than 8.14 requests per sample). The conclusions are unaffected. Only Devstral 2 pricing (third-party aggregators) and the OpenTelemetry GenAI status were verified live. Everything else is background knowledge, marked "(unverified)" where relevant.

## Executive summary

- **Arithmetic check.** A week has 7 x 96 = 672 fifteen-minute samples. Input tokens per sample are 11.69M/672 = 17,396 (A) and 20.05M/672 = 29,836 (B), so about 17.4k and 29.8k. The "29.9k" in the brief should read 29.8k.
  - Requests per sample are 4.39 (A) and 8.14 (B).
  - Output tokens per sample are about 625 (A) and 1,146 (B).
  - Adding the Sustainability agent raised requests by 1.86x and input tokens by 1.71x, while latency per call rose only 5.6%.
  - Input per request is almost the same in both configs (about 3,970 vs 3,660), so the cost driver is the number of calls, not prompt size.
- **Cost (not yet assessed in the case).** At $0.40/M input and $2.00/M output (aggregator prices, unverified against Mistral's own page):
  - A costs about $5.5/week, or $0.008 per decision.
  - B costs about $9.6/week, or $0.014 per decision.
  - Annualised, that is about $290 (A) and about $500 (B) per site.
  - Input tokens are 85% of the cost.
- **Pattern fit.** "Propose + score + arbitrate" is a supervisor/judge hybrid with a debate step. Self-assigned scores are the weakest part: uncalibrated, self-preferring and not comparable across agents. Have a deterministic simulator compute the scores and keep the self-scores only as rationale.
- **Biggest lever: a hybrid architecture.** The LLM sets strategy (mode, weights, reserve). An MPC/MILP solver computes the kW setpoint. A deterministic constraint layer clamps the result. This removes most debate calls and gives a safe offline mode.
- **Evaluation.** Use OpenTelemetry traces (GenAI conventions are still "Development") with Langfuse, LangSmith or Phoenix. Evaluate trajectory, tool use, constraint violations, consistency and regret versus a MILP oracle via offline replay.
- **Local models.** 3-8B models at 4-bit run on a Jetson Orin class device, and borderline on a Raspberry Pi 5. They suit a bounded fallback, not replacing the 123B model (unverified).

## 1. Agentic frameworks and orchestration patterns

### 1.1 Framework comparison (capabilities from background knowledge; verify versions)

| Framework | Core model | Patterns | Strengths for this case | Weaknesses | Edge fit |
|---|---|---|---|---|---|
| LangGraph | Explicit state graph, typed state, checkpointing | Supervisor, hierarchical, custom debate/vote loops, human-in-loop | Deterministic control flow (orchestrator = a node); replay; LangSmith tracing | Learning curve | Fine in Python on a gateway |
| AutoGen / AG2 | Conversational multi-agent (GroupChat) | Group chat, debate, nested chats | Natural for "agents discuss" | Token growth per round; non-deterministic speaker selection; AutoGen reportedly folded into Microsoft Agent Framework (unverified) | Token-heavy |
| CrewAI | Role-based crews and tasks | Sequential, hierarchical | Fast prototype; roles map to Cost/Sustainability | Less state control; weaker observability | Light, little determinism |
| OpenAI Agents SDK | Agents, handoffs, guardrails, tracing | Handoffs, agent-as-tool, guardrails | Built-in guardrails and tracing; reportedly usable with other providers (unverified) | OpenAI-centric defaults | Light |
| Mistral Agents API | Hosted agents, connectors, handoffs, MCP | Handoffs | Same vendor as Devstral 2 (EU billing/residency) | Cloud-only, useless offline | None |
| Google ADK | Code-first; sequential/parallel/loop workflow agents | Workflow agents, hierarchical delegation, A2A | Deterministic workflows; built-in eval | Gemini/Vertex-leaning; younger | OK |
| MCP | Protocol exposing tools/resources to LLM clients | Not an orchestrator | Wrap battery/PV/forecast as reusable tool servers | Schema tokens per call; auth needs care | Good if schemas are small |
| A2A | Agent-to-agent protocol (agent cards, tasks) | Cross-vendor interop | Useful for third-party agents (e.g. a utility's) | Overkill for two in-process agents | Not needed in pilot |

### 1.2 Pattern fit for "propose + score + arbitrate"

| Pattern | Fit | Note |
|---|---|---|
| Supervisor / orchestrator-worker | High | Current setup. Keep the orchestrator deterministic. |
| Judge | High, if the judge is not the proposer | Replace self-scores with a simulator or a separate judge. |
| Debate | Medium | Tokens and latency grow roughly linearly with rounds. Benefit is unclear for numeric control (unverified). |
| Voting / ensemble | Medium-high | Median of N samples is robust for a kW value (self-consistency, Wang et al. 2022). |
| Blackboard | Medium | Implement as shared typed state (SoC, forecasts) in LangGraph. |

Recommended shape: parallel proposers, then a deterministic evaluator (simulator plus constraint check), then rule-based selection.

### 1.3 Weaknesses of self-assigned scores (cf. Zheng et al. 2023 and later work on self-preference bias)

1. Self-preference bias: models rate their own output higher.
2. Poor calibration: the same state can score 0.7 or 0.9 on different calls.
3. Role bias: a Cost agent scores "cost" high for its own proposal by construction, so scores are not comparable across agents.
4. Scale clustering around 7-9/10 and anchoring.
5. No grounding: nothing is simulated, so "resilience 8/10" is a guess.
6. If all proposals score high, the arbitration is effectively arbitrary.

Mitigations:
- Compute the four criteria numerically. Cost: price forecast x energy flow. Sustainability: grid carbon intensity x import. Resilience: SoC reserve after N hours versus a backup threshold. Comfort: unmet load.
- If an LLM judge is still wanted, use a different model, pairwise comparison and randomised order.
- Log the correlation between self-scores and simulator scores. If it is low, drop the self-scores.

## 2. How the industry evaluates agents

### 2.1 Evaluation areas (examples from background knowledge)

| Area | What it measures | Examples |
|---|---|---|
| Tool-use accuracy | Right tool, valid arguments, no needless calls | BFCL, tau-bench / tau2-bench, ToolBench |
| Trajectory evaluation | Step and tool-call sequence versus an acceptable path | LangSmith agentevals, Google ADK trajectory metrics |
| End-to-end success | Outcome against ground truth | AgentBench, GAIA (not domain-relevant) |
| LLM-as-judge | Rubric scoring of reasoning or explanations | G-Eval, MT-Bench judge, Ragas, DeepEval |
| Consistency / determinism | Variance on identical input | pass^k in tau-bench; own test: N=10 reruns per state, report std dev of kW |
| Constraint-violation rate | Share of decisions breaking SoC/power/grid limits | Must be built; no standard benchmark |
| Domain outcome | Cost, self-consumption, CO2 versus baseline or oracle | Offline replay versus rule baseline and perfect-foresight MILP |

Practical design for the pilot:
- **Golden set:** 100-300 logged states, stratified by season, price spread and SoC, including edge cases.
- **Counterfactual replay:** re-run agents on logged states and score with the simulator.
- **Regret:** (agent cost - oracle cost) / oracle cost.
- **Baselines:** add a rule-based baseline and a "no battery action" baseline to the same week. One week and one site is anecdotal, so call it a pilot, not a result.

### 2.2 Observability

| Tool | Notes |
|---|---|
| Langfuse | Open source, self-hostable (useful for EU data), traces, cost, evals, prompt management, accepts OpenTelemetry |
| LangSmith | Commercial; strongest with LangGraph; trajectory evals |
| Arize Phoenix | Open source, OpenTelemetry/OpenInference-based, local evals |
| OpenTelemetry GenAI semantic conventions | Attributes such as gen_ai.operation.name (invoke_agent) and gen_ai.usage.input_tokens. As of mid-2026 gen_ai.* attributes are still "Development"; only inherited error.type, server.address and server.port are Stable. The conventions reportedly moved to a dedicated repo on 12 June 2026 (v1.42.0), per secondary sources. Pin the version and expect renames. |

Recommendation: instrument with OpenTelemetry on the gateway and send traces to self-hosted Langfuse or Phoenix to avoid lock-in.

### 2.3 Agent operational KPIs

| KPI | Formula | Why |
|---|---|---|
| Cost per decision | (in_tok x p_in + out_tok x p_out) / decisions | Unit economics; about $0.008 (A), $0.014 (B) |
| Tokens per decision (in/out) | total tokens / samples | 17.4k/625 (A), 29.8k/1,146 (B) |
| LLM calls per decision | requests / samples | 4.39 (A), 8.14 (B); main driver |
| Input tokens per call | input tokens / requests | About 3,970 / 3,660; shows caching potential |
| Decision latency p50/p95/p99 | percentiles of trigger-to-setpoint time | Mean per call (2.4-2.5 s) hides the tail. If calls are sequential, per decision about 4.39 x 2.36 = 10 s (A) and 8.14 x 2.49 = 20 s (B), an upper bound (unverified). Far below the 900 s interval. |
| Timeout / failure rate | failed calls / calls | Triggers fallback; SLO e.g. under 1% |
| Fallback rate | decisions by fallback / decisions | Measures cloud dependence |
| Schema-invalid rate | outputs failing schema / calls | Cheap quality signal |
| Constraint-violation rate (pre-guard) | out-of-limit proposals / proposals | Shows how often the guard saves the system; post-guard must be 0 |
| Guard-clamp magnitude | mean abs(proposed - applied kW) | How much the guard corrects the LLM |
| Consistency | std dev of kW over N reruns of identical state | Determinism |
| Agreement rate | share of decisions where Cost and Sustainability proposals are within epsilon kW | High agreement means the debate adds cost without value |
| Regret vs oracle | (agent cost - oracle cost) / oracle cost | Real decision quality |
| Improvement vs baseline | (baseline cost - agent cost) / baseline cost | Business value |
| Net value per decision | savings per decision - inference cost per decision | Does the agent pay for itself |
| Tool-call success and redundancy | valid calls / calls; repeated identical calls / calls | Tool hygiene |
| Self-score vs simulator correlation | Spearman between the two | Tests whether self-scores carry information |

## 3. Agent optimisation

### 3.1 Fewer tokens and calls (estimates are unverified)

| Lever | Mechanism | Expected effect |
|---|---|---|
| Prompt caching | Static prefix first (system prompt, rules, tool schemas, few-shot), dynamic state last. Aggregators list a $0.04/M cache-read price for Devstral 2 (10x cheaper). | If 60-80% of input is prefix, input cost falls 54-72%. Needs a byte-identical prefix and provider support; check Mistral's docs. |
| State compression | Compact numeric state; forecasts truncated to the relevant horizon | Plausibly -30-50% input |
| Fewer discussion rounds | One proposal round; merge Cost and Sustainability into one two-objective call | Calls per decision from 8.1 to about 2-3 |
| Event-triggered invocation | Call the LLM only on changes (price band, SoC threshold crossing, forecast deviation, load spike) | LLM calls down 50-80% if most slots are "no change"; measure from logs |
| Plan-ahead | One call produces a multi-hour plan; re-plan on deviation | Same savings as event triggering |
| Structured output, short rationale | JSON schema, capped reasoning. Output costs 5x input per token. | Modest; output is already about 140 tokens per call |
| Pre-injected state | Send battery/PV state in the prompt instead of tool calls | Removes a round trip per decision |

### 3.2 Routing and cascades
- Cascade: try a small local model first and escalate to Devstral 2 on low confidence, schema failure, constraint violation or high-stakes states. References: FrugalGPT (2023), RouteLLM (2024).
- Route by state class: easy states (night, mid SoC, flat price) go to the rule layer or small model.
- Devstral is a coding-focused family. A general model (e.g. Mistral Small or Medium) may do the same control reasoning more cheaply. Benchmark on the golden set (unverified).

### 3.3 Edge hardware (all figures unverified)

| Item | Estimate |
|---|---|
| Models | Gemma (2B-27B), Qwen (0.5B-72B), Ministral (3B/8B) |
| Quantisation | 4-bit (GGUF Q4_K_M, AWQ, GPTQ) cuts memory about 4x with small quality loss; loss is larger on small models |
| Memory | 4-bit 7-8B needs about 4.5-6 GB; 3-4B needs about 2-3 GB |
| Raspberry Pi 5 (8 GB) | CPU only; about 5-10 tok/s for 3B Q4, about 2-4 tok/s for 7-8B. A 500-token prompt plus 150 output tokens takes tens of seconds. Feasible as fallback, not primary. |
| Jetson Orin Nano/NX/AGX | GPU with shared memory (8 GB to 64 GB). 7-8B Q4 reaches tens of tok/s on NX/AGX. Comfortable for fallback and possibly primary. |
| Runtimes | llama.cpp, Ollama, vLLM (Jetson), MLC |
| Limits | Weaker tool-calling on 1-4B models; use constrained decoding (grammar/JSON schema) |

The 123B model cannot run on this hardware, so "local fallback" means a much weaker model. Evaluate it separately on the golden set and keep the safety layer identical.

### 3.4 Distillation
- Fine-tune a small model (LoRA/QLoRA on Qwen or Gemma) on logged teacher decisions that were verified near-optimal by the simulator (low regret).
- Data is limited: about 2,900-5,500 decisions per week per site. Pool across sites and filter by regret so the student does not copy the teacher's errors.
- Cheaper alternative: behaviour cloning into a small numeric policy (gradient-boosted trees or a small network) for the 1-D kW output. No LLM at the edge; often competitive (unverified).
- Check the Devstral 2 licence before distilling. The 123B reportedly uses a modified MIT licence with commercial restrictions (unverified).

### 3.5 Hybrid architecture (main recommendation)

```
Cloud LLM (every 1-4 h or on events)
  -> strategy: objective weights, reserve SoC, mode
MPC / MILP (every 15 min, on the gateway, ms to seconds)
  -> optimal kW from forecasts, tariff, battery model
Safety layer (deterministic hard constraints)
  -> clamp SoC, power, grid limits, ramp rate
Inverter / battery
```

- A 10 kWh battery with PV and a tariff is a small LP/MILP. Open-source solvers (HiGHS, OR-Tools, CBC, CVXPY) solve it in well under a second.
- The LLM adds value where the maths is weak: user preferences, unusual events, trade-off weights, explanations.
- If the cloud is lost, the optimiser keeps running on the last strategy. A local LLM is needed only for strategy, which changes rarely.
- Letting the LLM formulate the MILP (e.g. OptiMUS) is still unreliable. Fix the formulation and let the LLM choose parameters only.

### 3.6 Safety guards (deterministic, outside the LLM)
1. Clamp power to the charge/discharge limits.
2. Enforce SoC_min and SoC_max, including energy over the interval (kW x 0.25 h).
3. Grid import/export limits and inverter ramp limits.
4. Schema validation: type, range, finite number; reject NaN or text.
5. Emergency backup reserve unless explicitly overridden.
6. Watchdog: on timeout, apply the fallback rule (e.g. self-consumption) and log it.
7. Log proposed and applied values; alarm on repeated clamps.
8. Rate-limit mode flips to limit battery wear.

The OpenAI Agents SDK and Google ADK offer guardrail hooks, but a guard in the gateway code is safer than one inside an agent framework.

## 4. Learning from history

| Technique | How | Fit and caveats |
|---|---|---|
| RAG over past decisions | Store (state, decision, outcome); retrieve the k most similar | Good first step. For numeric state use nearest neighbour on a feature vector (hour, SoC, price level, forecast PV), not text embeddings. Adds k x ~150 input tokens. |
| Few-shot from best cases | Retrieve cases with the lowest regret or best realised savings | Filter by computed outcome, not self-score. Outcomes are known only after the fact (e.g. 24 h later). Beware survivorship bias and seasonal shift. |
| Reflection | Agent writes lessons after outcomes (Reflexion, Shinn et al. 2023) | Cheap to test, but lessons can drift. Review them and cap memory. |
| Offline RL | Learn a policy from logs (CQL, IQL) | Needs far more data and action coverage than one LLM-driven week provides. Prefer simulation-based RL or MPC. |
| Fine-tuning | SFT or LoRA on selected decisions | See 3.4. |

Order of effort: logging and outcome labelling, then RAG/few-shot, then distillation, with offline RL last.

## 5. Quantified improvement ideas

### Baseline unit economics ($0.40/M in, $2.00/M out; aggregator figures, unverified)

| | A | B |
|---|---|---|
| Samples/week | 672 | 672 (actual: 671) |
| Requests/sample | 4.39 | 8.14 |
| Input tokens/sample | 17,396 | 29,836 |
| Output tokens/sample | 625 | 1,146 |
| Input per request | 3,966 | 3,664 |
| Output per request | 142 | 141 |
| Weekly input cost | $4.68 | $8.02 |
| Weekly output cost | $0.84 | $1.54 |
| Weekly total | $5.52 | $9.56 |
| Cost per decision | $0.0082 | $0.0142 |
| Annual per site (x52) | about $287 | about $497 |
| Per 1,000 sites per year | about $0.29M | about $0.50M |

### Scenarios on B (assumptions unverified)

| # | Idea | Calculation | Result |
|---|---|---|---|
| 1 | Caching, 70% of input as cached prefix at $0.04/M | 20.05M x (0.3 x 0.40 + 0.7 x 0.04) = $2.97, plus $1.54 output | about $4.51/week, -53% |
| 2 | LLM called on 40% of samples (event-triggered) | $9.56 x 0.4 | about $3.82/week, -60% |
| 3 | Ideas 1 + 2 | $4.51 x 0.4 | about $1.80/week, -81% |
| 4 | One merged call plus an optimiser setpoint (about 2 calls per sample, about 3,700 tokens in) | 4.97M in = $1.99, plus about 0.19M out = $0.38 | about $2.37/week, -75% |
| 5 | Hybrid: a strategy call every 4 h (about 84 calls/week, about 4k tokens each) | about 0.34M input tokens | about $0.2/week, -98%; the optimiser carries the 15-min decisions |
| 6 | Local fallback during an outage | 96 decisions per day at no cloud cost | Zero marginal cost, quality must be tested |

Idea 5 also makes decision latency milliseconds and removes cloud dependence from the safety-critical path.

### Quality tests
- Replace self-scores with simulator scores and measure how often the orchestrator's pick changes. If it rarely changes, the self-scores are redundant.
- Measure the Cost vs Sustainability agreement rate. If it exceeds about 70%, run Sustainability only on disagreement or events. B costs about 73% more tokens than A, and its value should be measured on regret and savings, not tokens.
- Report p50 and p95 latency, not just the mean.

### Four-week plan
1. Instrument OpenTelemetry/Langfuse; build the golden set; add rule and MILP baselines.
2. Implement the constraint layer and simulator scoring; replay A and B offline.
3. Add caching, state compression and event triggering; measure tokens, cost and regret.
4. Test the hybrid (strategy LLM plus MILP) and local fallback on a Jetson/Pi.

## Recommendations for Sense Reply

1. Fix the headline numbers: 17.4k vs 29.8k input tokens/sample, 4.4 vs 8.1 calls/sample, and report cost per decision ($0.008 vs $0.014, subject to the real contract price).
2. Add outcome metrics (cost, self-consumption, constraint violations, regret vs a MILP oracle). Token savings mean nothing without decision quality.
3. Do not trust self-assigned scores. Compute criteria by simulation, or use a separate judge with pairwise comparison, and log the correlation.
4. Move to the hybrid: LLM for strategy, MPC/MILP for the kW, deterministic guard on top.
5. Take the cheap wins first: prompt caching, compact numeric state, event-triggered invocation, pre-injected state.
6. Use LangGraph or Google ADK workflow agents so the orchestrator is a deterministic graph. Use MCP only if tools need reuse. Skip A2A in the pilot. Keep free-form AutoGen-style chat out of the control loop.
7. Instrument with OpenTelemetry and self-hosted Langfuse or Phoenix. Pin semantic-convention versions.
8. Fallback: start with a rule/MPC fallback (no LLM). Add a quantised 3-8B model for strategy only, on a Jetson-class device. A Raspberry Pi works only if tens of seconds of latency is acceptable. Evaluate the fallback on the same golden set.
9. Start logging outcome-labelled decisions now, then RAG with outcome-filtered few-shot. Consider distillation once several sites' data exist.
10. State the pilot's limits (one week, one site, one season) and plan a multi-week, multi-site evaluation.

## References

Verified via web search, retrieved 2026-11-06:
- Devstral 2 pricing ($0.40 in / $2.00 out / $0.04 cache read per M tokens; aggregators, not Mistral's own page, so unverified): https://pricepertoken.com/pricing-page/model/mistral-ai-devstral-2-123b ; https://pi.dev/models/mistral/devstral-latest ; https://opencode.ai/data/mistral/devstral-medium-latest.md
- OpenTelemetry GenAI agent spans: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans
- OpenTelemetry GenAI client spans: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans
- Status of the GenAI conventions (secondary sources): https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained ; https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions ; https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke

Background knowledge, not re-verified (check before citing):
- Zheng et al. 2023, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (arXiv 2306.05685)
- Wang et al. 2022, "Self-Consistency Improves Chain of Thought Reasoning" (arXiv 2203.11171)
- Chen et al. 2023, "FrugalGPT" (arXiv 2305.05176)
- Ong et al. 2024, "RouteLLM" (arXiv 2406.18665)
- Shinn et al. 2023, "Reflexion" (arXiv 2303.11366)
- Yao et al. 2024, "tau-bench" (arXiv 2406.12045)
- Berkeley Function-Calling Leaderboard: gorilla.cs.berkeley.edu
- Framework docs: langchain-ai.github.io/langgraph, ag2.ai, docs.crewai.com, openai.github.io/openai-agents-python, docs.mistral.ai/agents, google.github.io/adk-docs, modelcontextprotocol.io, a2a-protocol.org
- Observability: langfuse.com, smith.langchain.com, phoenix.arize.com
- Edge: github.com/ggml-org/llama.cpp, developer.nvidia.com/embedded

Unverified: Pi/Jetson throughput figures, cache hit-rate and event-trigger assumptions, all section 5 savings, framework feature claims (including the AutoGen/Microsoft Agent Framework merger and the Devstral 2 licence terms), and the evaluation-benchmark descriptions.
