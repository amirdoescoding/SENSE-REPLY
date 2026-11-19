# 08: Which model replaces Devstral 2, where it runs, and what it costs

Date: 2026-11-19. Branch `local-model`. Sources:
- four research passes: models; hardware and competitors; a hosting-slot opinion; a pressure-test;
- one local bench: `demo/local_bench.py`;
- one cost model: `analysis/model_cost.py`.

V = verified at the linked source. E = our estimate. The demo keeps Gemini as a placeholder.

## 1. Decision

| | Choice |
|---|---|
| **Model family** | **Mistral Ministral 3**, open weights, Apache-2.0, EU (France), Jan 2026 ([HF](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512)) V |
| **Default: central** | **Ministral 3 8B Instruct**, Q4 or FP8, on Reply's on-prem platform |
| **Edge upsell** | **Ministral 3 3B** (2.15 GB Q4) on an AI-capable gateway, for clients who need offline operation or require that no data leave the site |
| **Benched alternative** | **Qwen3.5-4B** (Apache-2.0, CN). It passed our bench 14/14 (§4). Use it if a client has no origin constraint. |
| **Fallback, unchanged** | yesterday's valid plan → the static rule. The edge needs no model to keep running. |

**Why this model.**
1. **Governance.** With open weights, Reply holds the file. Nobody can retire it: Devstral 2 was retired on 2026-07-31, and Medium 3.5 is deprecated. Model updates become Reply's decision, gated by the replay gate.
2. **Licence and origin.** Apache-2.0 allows commercial use with no custom terms. EU origin is the easiest procurement and AI Act story for an Italian client. Qwen is equally capable but Chinese-origin.
3. **Continuity.** It is the same vendor family as Devstral, which eases the port. Its card claims native JSON and function calling (V) and lists Italian explicitly (V).
4. **Fit to the task.** The task is three numbers plus two sentences, once a day. Our bench shows a 4B model already gets it right (§4), so an 8B on the server has headroom and a 3B fits a gateway.
5. **Cost.** On shared on-prem compute the AI bill is €0.02–0.18 per site per week at 1k–10k sites. The pilot's bill was €7.71 (§7).

**Not yet proven:** Ministral itself has not run our prompts. The Mac (8 GB) crashed loading the 8B. Next step: bench Ministral 3 3B (2.15 GB), which uses the same chat template.

## 2. Where it runs, mapped to the brief's "Agentic Operations for E&U" diagram
- **Today:** the LLM is the dashed *External AI Service Provider* box hanging off the Centralized Platform.
- **Proposal:** replace that box with the open-weight model in the platform's own *Computational Resources*. The platform is already "Cloud **or On-Premise**" in the brief. Nothing else in the diagram moves.
- **Edge Apps Store:**
  - it already ships agents to the IoT Edge Gateways, where they run as *Edge AI Agents*;
  - it keeps shipping our edge agent (rule/MPC, validator, clamp, last plan);
  - for the edge upsell, it also ships the signed model weights (A/B slots, rollback; doc 07 §2).
  - The Apps Store is the distribution channel; it is not where inference runs.
- **The memory and replay logs live in the Data Lake.** Pooled across sites, they feed the replay gate and, later, a LoRA fine-tune.
- **Precedent:** Sense Reply's MAGO describes a "multi-agent decision framework deployed on edge, controlled and audited from central system" ([reply.com](https://www.reply.com/sense-reply/en/our-services/multi-asset-grid-optimization)) V.

**Why central first, edge as upsell.**
- Offline resilience does not need an edge model. The agent's inputs (day-ahead prices, CO2) come from the internet anyway. When the link drops, the edge keeps dispatching on yesterday's plan, then the rule.
- A box per site costs more than the battery saves (§7).
- Edge wins only for:
  - air-gapped or no-external-processor clients;
  - sites where capable hardware is already installed;
  - intraday re-planning without connectivity.
  Price the edge option as a premium. It is not a saving.

## 3. Shortlist (models available Nov 2026)

| Model | Size Q4 | Licence / origin | Structured output | Maths | Italian | Edge speed | Verdict |
|---|---|---|---|---|---|---|---|
| **Ministral 3 8B** | 5.2 GB V | Apache-2.0, EU | native JSON / function calling (vendor claim) V; no IFEval/BFCL published | MATH 0.876 V | listed V | ~15–19 tok/s Orin (E) | **Central default** |
| **Ministral 3 3B** | 2.15 GB V | Apache-2.0, EU | as above | MATH 0.830 V | listed V | ~20+ tok/s (E) | **Edge upsell** |
| **Qwen3.5-4B** | 2.74 GB V | Apache-2.0, CN | IFEval 89.8, BFCL-V4 50.3 V | MMLU-Pro 79.1 V | 201 languages | 10.2 tok/s Orin Nano V | **Benched: 14/14** |
| Qwen3.5-9B | 5.68 GB V | Apache-2.0, CN | IFEval 91.5, BFCL-V4 66.1 V | MMLU-Pro 82.5 V | yes | tight on 8 GB | quality ceiling |
| Gemma 4 E4B | 5.3 GB V | Apache-2.0, US | Tau2 42.2 V | AIME26 42.5 V | 35+ languages | 9.5 tok/s Orin Nano V | best Jetson evidence |
| Granite 4.0 H-Micro | ~2 GB E | Apache-2.0, US | IFEval 86.9, BFCL 57.6 V | GSM8K 81.4 V | weak (MMMLU 55) | n/a | viable, weak Italian |

Dropped:
- Phi-4-mini: English-centric.
- Llama: custom licence.
- Hailo-10H boards: 2k-token context cap V.

**Correction to doc 05.** Mistral Small 4 is a **119B MoE** with ~6B active parameters, not a 24B model ([Mistral](https://mistral.ai/news/mistral-small-4/)) V. Re-derive doc 05's self-host rows before quoting them.

Sources:
- [Ministral 3 8B](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-GGUF)
- [Ministral 3 3B](https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF)
- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)
- [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B)
- [Qwen3.5-4B on Jetson](https://www.jetson-ai-lab.com/models/qwen3-5-4b/)
- [Gemma 4 E4B](https://huggingface.co/google/gemma-4-E4B-it)
- [Gemma 4 E4B on Jetson](https://www.jetson-ai-lab.com/models/gemma4-e4b)
- [Granite 4.0 H-Micro](https://huggingface.co/ibm-granite/granite-4.0-h-micro)

## 4. Local bench: does a small model do the job?
**Setup.**
- `demo/local_bench.py` swaps only `agent.ask` for a llama.cpp call. The prompts, validator, replay gate and rolling MPC are the same as the demo.
- Run: run C week, λ 0.10, fixed A+C memory, 7 plan windows per mode.
- Model: Qwen3.5-4B Q4_K_M on a MacBook M1 8 GB, which is in the memory class of a Jetson Orin Nano. Context 4,096, thinking off, JSON-object grammar.
- Results: `demo/out/local_bench.json`. The demo does not serve that file.

| | Qwen3.5-4B local | Gemini 3.5 Flash-Lite | No LLM (copy nearest good day) |
|---|---|---|---|
| Valid JSON | 14/14 | 14/14 | n/a |
| Clamped or invalid knobs | 0 | 0 | 0 |
| Gate pass, conservative / upside | 5/7 / 7/7 (2 days ran the previous valid plan) | 7/7 / 7/7 | 7/7 / 7/7 |
| S_net €/wk, conservative / upside | 1.156 / 1.568 | 1.156 / 1.568 | 1.156 / 1.568 |
| Tokens/week, in / out | 7,945 / 965 | 7,947 / 5,112 (with thinking) | 0 |
| Time per call | 15–17 s (prefill ~165 tok/s, decode ~16 tok/s) | 1–7 s (cloud) | ~0 |

**What this proves:**
- a 4B local model, on laptop-class hardware, writes valid and unclamped plans;
- its knobs match Gemini's to within a cent of export hold;
- its owner explanations read well;
- a call takes ~16 s, which is irrelevant once a day.

**What it does not prove.** This week, all three columns equal the no-LLM baseline. Knob regret against the rule is about ±1 cent a day in January (MEMORY). The model's proven value this week is reliable JSON plus a plain-language explanation, not better decisions. This argues for the **smallest reliable model**, which is why 3–8B and not larger. The model has to beat the memory baseline on other weeks (summer surplus, price or CO2 spikes) to earn decision credit. That test is in the backlog.

## 5. Hardware

| Device | Price | RAM / power | Speed, 8B Q4 | Use |
|---|---|---|---|---|
| Jetson Orin Nano Super devkit | **$399** (was $249: NVIDIA raised prices up to 101% in Jul 2026) V | 8 GB, 7–25 W V | Llama 3.1 8B decode 19 tok/s V | Edge, 3–4B |
| Jetson Orin NX 16GB module | **$999** (was $599) V | 16 GB, 10–25 W V | Qwen3-8B prefill 696, decode 17.5 tok/s V | Edge, 8B |
| Industrial Orin NX box (Axiomtek, OnLogic, Advantech) | €1.5–3k (E, price on request) | −25…+70 °C (Axiomtek) V | as NX | Edge, industrial |
| Raspberry Pi 5, RK3588, Hailo-10H | $120–520 V | | 8B: 0.6–5 tok/s, or a 2k context cap | Out |
| L40S card | €7.7k (DE) V; server ~€15–20k E | 48 GB, 350 W V | 1.2–1.6k output tok/s batched V | Central, upper bound |

At 1 call a day, speed never binds. One node at the M1's measured 16 s per call handles ~5k sites in the 22 h plan window. Plans are due at 11:00 the next day, so there is no burst to size for.

Sources:
- [cnx-software, price rise](https://www.cnx-software.com/2026/07/22/nvidia-increases-the-price-of-jetson-modules-and-devkits-by-up-to-101/)
- [TensorRT Edge-LLM benchmarks](https://nvidia.github.io/TensorRT-Edge-LLM/latest/user_guide/performance/performance-benchmarks.html)
- [Axiomtek AIE900B-ONX](https://www.axiomtek.com/products/systems-and-platforms/machine-vision/edge-ai-system/aie900b-onx)
- [L40S price](https://gpudojo.com/l40s)
- [Red Hat MLPerf](https://www.redhat.com/en/blog/efficient-and-reproducible-llm-inference-red-hat-mlperf-inference-v51-results)

## 6. Competitors
- **No vendor ships an on-device LLM for battery dispatch.** We searched sonnen, Tibber, SMA, Huawei, SolarEdge, Enphase, Fronius and Tesla. Their dispatch is believed to be rules plus price- or forecast-driven optimisation (E).
- **Cloud LLM features exist, all user-facing:**
  - Sigenergy SigenAgent ([link](https://www.sigenergy.com/th/newsroom/blogs/ai-home-energy-management-sigenagent)) V;
  - AlphaESS AI agent ([link](https://taiyangnews.info/technology/alphaess-ai-agent-ess-benelux-country)) V;
  - EcoFlow OASIS;
  - the Kraken AI access layer ([link](https://www.kraken.tech/press-releases/kraken-expands-open-kraken-with-ai-access-layer-and-marketplace)) V.
- **Optimisers:** gridX, Kiwigrid and Schneider (MPC) (doc 03).
- **Takeaway:** "a self-hosted, open-weight LLM planner under a deterministic clamp" is open ground. Being central and self-hosted is a governance differentiator, not a novelty risk.

## 7. Cost per site and the KPIs
`python3 analysis/model_cost.py`.
- **Self-check:** it reproduces pilot C's O5 of €7.7086/wk.
- **Tokens:** measured from the bench, 7,973 in / 965 out per site-week. The pilot used 18.8 M / 0.72 M.
- **Hardware:** amortised over 5 years.
- **Power:** €0.32/kWh, Italian household price H1 2026 ([Euronews](https://www.euronews.com/2026/11/12/eu-household-electricity-and-gas-prices-fell-in-the-first-half-of-2026-who-pays-the-most)) V.
- **Ops (E):**
  - local: 0.1 FTE, €7k/yr, for model pinning, replay-gate re-validation and updates;
  - API: €3.5k/yr to re-validate when the vendor retires the model.

**AI cost O5, € per site per week**

| Option | 100 sites | 1,000 | 10,000 | Fleet where AI ≤ 10% of gain |
|---|---|---|---|---|
| Devstral 2 API (retired; the pilot's price) | 0.68 | 0.072 | 0.011 | 659 |
| EU API, Ministral 3 8B ($0.15/$0.15) | 0.67 | 0.069 | 0.008 | 659 |
| **Central on-prem, right-sized GPU node (€4k, 100 W, HA pair)** | 1.76 | **0.18** | **0.018** | 1,714 |
| Central on-prem, L40S server (upper bound) | 3.05 | 0.31 | 0.039 | 2,764 |
| Edge upsell: Orin Nano Super + case (€400) | 1.86 | 1.86 | 1.86 | never |
| Edge upsell: industrial Orin NX (€2,000) | 8.12 | 8.12 | 8.12 | never |

**N1 (net value after AI, €/wk), report's S5 conservative = €1.1156 before AI**

| Option | 100 sites | 1,000 | 10,000 |
|---|---|---|---|
| Pilot C (for reference) | −7.31 | −7.31 | −7.31 |
| Devstral 2 API, as in the report (no ops) | +1.10 | +1.10 | +1.10 |
| EU API, Ministral 3 8B | +0.44 | +1.05 | +1.11 |
| **Central on-prem, right-sized** | −0.65 | **+0.94** | **+1.10** |
| Edge upsell, Orin Nano Super | −0.75 | −0.75 | −0.75 |

**Upside mode** (S_net €1.7957): central right-sized gives N1 +0.03 / +1.62 / +1.78. The full N1, N2 and F1 tables for both modes are printed by the script.

**Reading.**
- **The model is nearly free; people and boxes are not.** Ops dominates at small fleets. Under ~700 sites (API) or ~1,700 sites (on-prem), AI eats more than 10% of the gain.
- **Central on-prem from ~1,000 sites.** It keeps N1 at +€0.94–1.10/wk, against −€7.31 for the pilot. That is still a 98–99.8% cut in AI cost, with Reply owning the model.
- **A small pilot (≤ a few hundred sites) should start on an EU API with the same open-weight model,** then move in-house at ~1,000 sites. The prompt and weights are identical, so the move is a config change.
- **Edge is a paid upsell.** The box costs €97/yr (Nano Super) to €422/yr (industrial NX) per site, against a ~€58/yr gain. Price the offline/residency option at or above that floor. The break-even box price is ~€206 over 5 years, below any Jetson today.
- **What changes in the deck's headline:** the "+€1.10/wk at €0.01 AI cost" assumed Devstral list prices with no ops. With a named self-hosted model and ops included, it becomes **+€0.94/wk at 1,000 sites, +€1.10 at 10,000**. The deck stays unchanged until the user says so.

## 8. Assumptions and flags
- Site = Italy. FX 0.86 €/$. Hardware life 5 years. Power at the household rate, including the server room (E).
- Ops FTE share, the right-sized node's price and its 25k-site capacity are estimates (E). Industrial box prices are on request (E).
- Tokens were measured with thinking off. With memory examples the prompt can grow to ~5k tokens (doc 07); input cost scales linearly and stays below 1 cent a week on the APIs.
- The bench covers one winter week and one model, Qwen3.5-4B. Ministral has not been benched on our prompts.
- Jetson prices are post-July-2026 list prices; doc 07's €90/site/yr is stale.

## 9. Risks and next steps

| Risk | Likelihood | Impact | Mitigation | Owner role |
|---|---|---|---|---|
| Ministral 3 has not run our prompts. The only bench is Qwen3.5-4B, on one winter week. | High | Medium | Bench Ministral 3 3B first, with the same chat template and the same 7 windows. | ML engineer |
| The LLM does not beat the no-LLM memory baseline on other weeks. In January all three columns tie. | Medium | High | Replay summer and price or CO2 spike weeks before claiming decision value. If it never wins, ship the rule and keep the LLM for explanations. | Analyst |
| Ops cost is underestimated. The 0.1 FTE (€7k/yr) is our estimate. | Medium | High below ~1,000 sites | Confirm the FTE with Sense Reply. Rerun `analysis/model_cost.py` with their figure. | Project manager |
| Model update or rollout fails on the Edge Apps Store. | Low | High | Signed weights, A/B slots with rollback, replay gate before promotion. The old slot stays live until the new one passes. | Platform lead |
| Fleet too small for on-prem (under ~1,000 sites). | High early | Medium | Start on an EU API with the same open weights. Move in-house at ~1,000 sites. The move is a config change. | Product owner |
| Edge upsell priced below the hardware floor. Box cost is €97–422/yr against a ~€58/yr gain. | Medium | High | Price edge at or above the floor. Sell it as a residency and offline option, not a saving. | Commercial lead |
| GDPR: home load is personal data. | Low | High | Prompts send daily aggregates only. Audit prompts and logs for raw 15-min data. EU hosting with a DPA. Legal review before launch. | Data protection lead |

**Next steps, in order**
1. **Bench Ministral 3 3B on the 8 GB Mac.** Load one model at a time; never the 8B there.
   - Done when the results file shows 14/14 valid JSON and 0 clamped knobs, with gate-pass counts next to Qwen's.
2. **Replay a summer week and a price or CO2 spike week against the memory baseline.**
   - Done when each week reports the model's knob regret against the no-LLM baseline as a win, a tie or a loss.
3. **Confirm the ops FTE with Sense Reply.**
   - Done when `analysis/model_cost.py` reruns with their figure and the N1 table is updated.
4. **Only when the team says so:** add the local-model slot to a copy of the brief diagram, and update the deck and script numbers.
   - Done when the team signs off the diff.
