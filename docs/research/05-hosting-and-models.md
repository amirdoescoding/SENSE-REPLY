# 05 – LLM hosting options and break-even (Mistral, Bedrock EU, self-host, edge)

Date: 2026-11-08. Author: research-analyst agent (raw report, lightly trimmed).
Status labels:
- **V** = fetched today, with a URL.
- **E** = estimate or unverified third-party figure.

## 0. Corrections to earlier reports
- **Devstral 2 is retired.** Devstral 2 (`devstral-2512`) was deprecated on 2026-05-22 and retired on **2026-07-31**. Devstral Small 2 was retired on 2026-03-31. Mistral names **Mistral Medium 3.5** as the replacement (V, docs.mistral.ai/getting-started/models). The Jan 2026 week is still valid as measured, but forward cost must use a current model.
- **Devstral prices:** the $0.40 / $2.00 per M figures come only from aggregators. Mistral's own page no longer lists Devstral.
- **Self-host estimate:** "4×H100 ≈ $1,680/wk" assumed $2.5 per GPU-hour. EU list price is about $3.0 per GPU-hour, which gives about **$2,016/wk**.

## 1. Revolut: what was actually claimed
| Item | Finding | Status |
|---|---|---|
| Source | David Abitbol (Revolut infrastructure), AI Engineer NYC, Oct 2026; reported by The Register on 3 Nov 2026 | V |
| What | Self-hosted open-weight models became the default for **AI coding assistance** for about 2,000 engineers | V |
| Models | Z.ai GLM-5.1, then GLM-5.3 (earlier: Gemini, then Claude Code) | V |
| Hardware | 56 Nvidia B200 GPUs (about 7 DGX B200 systems) | V |
| Cost | About $0.30 per M tokens, about 1/10 of Codex or Claude Code; inference cost down about 90% in a year | V |
| "Saves millions" | **No dollar total in any source found.** The claim is a percentage plus a per-token cost. | V (absence) |
| Caveats | The $0.30/M excludes staff, cloud and observability. Revolut still uses Claude, Codex and Gemini for some work. | E |

**What transfers:**
- Self-hosting wins at high, steady volume with good GPU utilisation.
- Inference engineering (quantisation, prefix caching, prefill/decode split) matters as much as the hardware.
- Keeping a frontier API as an exception path is the same cascade idea as in report 02.

**What does not transfer:**
- Revolut's baseline was frontier coding prices (about $3+/M). Ours is Small-class pricing.
- Config B on Mistral Small 4 blends to about **$0.17/M**, already below Revolut's self-host cost.
- Revolut has one central platform team. We have many small regulated tenants.
- For us, the driver is residency, not cost (§6).

## 2. Current API prices (USD per M tokens)
**Mistral** (V, docs.mistral.ai/inference/pricing). Cached input costs 10% of input. Batch is 50% off.

| Model | In | Cached in | Out |
|---|---|---|---|
| Mistral Small 4 | 0.15 | 0.015 | 0.60 |
| Ministral 3 14B | 0.20 | 0.02 | 0.20 |
| Ministral 3 8B | 0.15 | 0.015 | 0.15 |
| Ministral 3 3B | 0.10 | 0.01 | 0.10 |
| Mistral Large 4 | 0.70 | 0.07 | 2.10 |
| Mistral Medium 3.5 (E, aggregators) | 1.50 | 0.15 | 7.50 |

The EU-residency terms on Mistral's "Regional inference" page could not be read. **Ask Mistral.**

**Claude** (V, platform.claude.com pricing + Bedrock page)

| Model | In | Out | Cache read | Bedrock |
|---|---|---|---|---|
| Haiku 5.5 (prompts up to 100k) | 0.10 | 0.50 | 0.01 | access gated |
| Haiku 4.5 | 1.00 | 5.00 | 0.10 | open |
| Sonnet 5.5 | 2.00 | 10.00 | 0.10 | access gated |
| Sonnet 5 | 2.00 | 10.00 | 0.20 | open |

- **Bedrock EU regions:** Frankfurt, Zurich, Stockholm, Milan, Spain, Ireland, London and Paris have Global and EU endpoints. Stockholm and Ireland also have in-region-only endpoints.
- **Regional endpoints cost +10% over global** (global can route outside the EU). Haiku 5.5 EU is therefore about **$0.11 / $0.55**.
- Bedrock has no Message Batches, so no batch discount.

## 3. Self-hosting cost
| GPU | Price | Status |
|---|---|---|
| OVHcloud H100 80GB | €2.80/h (about $3.0) | E |
| Scaleway L40S | $1.64/h | V (computeprices.com) |
| Scaleway H100 | $3.2–3.8/h | E |

Always-on weekly cost: H100 **$504/wk**, L40S **$275/wk**, 4×H100 **$2,016/wk**. Re-check official pages before quoting.

**Throughput (all E, not benchmarked).** Sites per GPU: S = C × u × 604,800 / T_in, where C = prefill tokens/s, u = 0.5 utilisation, and T_in = 20.05M tokens/wk for B.

| Option | C | Sites per unit (B) | Sites per unit (A) |
|---|---|---|---|
| 123B on 4×H100 | 8k tok/s | about 120 | about 200 |
| 24B on 1×H100 | 25k tok/s | about 300 (derated) | about 500 |
| 7–8B on 1×L40S | 15k tok/s | about 225 | about 380 |

A 2× error in C moves break-even by 2×.

## 4. Edge-local option
| Device | Capex | Evidence |
|---|---|---|
| Jetson Orin Nano Super | about $249–399 | Gemma 2B 25.6 tok/s; Qwen 3B 22.6 tok/s; Llama 8B INT4 19 tok/s (V/E) |
| Pi 5 + AI HAT+ 2 | about $500 | The HAT is slower than the Pi's CPU (Llama 3B 2.7 vs 5.6 tok/s) |
| Hailo-10H | about $260–299 | Under 10 tok/s; 2k context cap, too small for our prompt |

Estimates for one 4k-token call:
- **Jetson, 3–4B Q4:** about 7–13 s per call, so 1–2 min per decision (8 calls). Fits in 15 min.
- **Pi 5 CPU:** 70–130 s per call, so 10–17 min per decision. **Does not fit.**

Cost: $400–500 capex over 260 weeks plus 15 W of power is about **$2.5/wk per site, flat**. The open question is quality, not cost, so benchmark on a golden set.

## 5. Break-even (USD per site per week, config B)
Formulas:
- API = T_in·p_in + T_out·p_out, with T_in = 20.05M and T_out = 0.771M (A: 11.69M / 0.418M).
- Self-host = ⌈N/S⌉·(GPUs·$/h·168)/N + F/N, where F = fixed ops cost.
- Edge = capex/260 + power.
- Break-even N* solves API·N = ⌈N/S⌉·G + F.

| Option | A | B |
|---|---|---|
| Devstral 2 $0.40/$2.00 (retired, E) | 5.51 | 9.56 |
| Mistral Medium 3.5 (E) | 20.7 | 35.9 |
| Mistral Small 4 | 2.00 | 3.47 |
| Ministral 8B | 1.82 | 3.12 |
| Ministral 3B | 1.21 | 2.08 |
| Haiku 5.5 Bedrock EU | 1.52 | 2.63 |
| Sonnet 5.5 Bedrock EU | 30.3 | 52.6 |

Prompt caching with a 70% hit rate on input cuts Small 4 B to about $1.3.

| B, per site/wk | N=1 | 10 | 100 | 1,000 | 10,000 |
|---|---|---|---|---|---|
| Mistral Small 4 API | 3.47 | 3.47 | 3.47 | 3.47 | 3.47 |
| Haiku 5.5 EU API | 2.63 | 2.63 | 2.63 | 2.63 | 2.63 |
| Medium 3.5 API | 35.9 | 35.9 | 35.9 | 35.9 | 35.9 |
| 24B on H100 (S=300) | 504 | 50.4 | 5.04 | 2.02 | 1.71 |
| 8B on L40S (S=225) | 275 | 27.6 | 2.76 | 1.38 | 1.24 |
| 123B on 4×H100 (S=120) | 2,016 | 202 | 20.2 | 18.1 | 16.9 |
| Edge Jetson | 2.5 | 2.5 | 2.5 | 2.5 | 2.5 |

**Break-even points:**
- 24B self-host vs Small 4 API: about **150 sites** (1 GPU, no ops cost). About 290 sites with an HA pair. **300–600 sites** with about $500/wk of ops cost.
- Self-host vs Haiku 5.5 EU or Ministral 8B: wins only above about **1,000 sites** once ops cost is included.
- **123B self-host never pays back** against Devstral-level API prices.

**Takeaway:** the big lever is model choice and caching (Medium 3.5 → Small 4 is 10×), not hosting. Self-hosting a small model saves less than 2×, even at 10,000 sites.

## 6. Regulation and data residency (background, verify with counsel)
| Regime | Applies? | Implication |
|---|---|---|
| GDPR | Probably yes. 15-min load and PV data reveal occupancy, so it is personal data when linkable to a home. | The API provider becomes a processor, so you need a DPA and EU-only processing. Self-hosting or on-device shortens the processor chain. |
| EU AI Act | Annex III §2 covers safety components of critical infrastructure (electricity). A home cost optimiser is probably not one; a fleet VPP or grid-balancing product could be closer to the line. | Mistral and Anthropic are GPAI providers; Sense Reply is the deployer. The Digital Omnibus moved Annex III obligations to **2 Dec 2027** (V via Gibson Dunn summary). |
| NIS2 | Energy is in Annex I, including aggregation, demand response and storage. | The cloud API is a supply-chain risk. You need an offline-safe fallback and security terms. |
| EU Data Act | In force since Sep 2025. | Favours portable, model-agnostic designs (an LLM abstraction layer). |

**At small scale, residency and control are the real reasons to self-host, not cost.** Self-hosting also avoids forced model retirement: see Devstral 2.

## 7. Recommendation by fleet size
- **Under 50 sites:** EU API (Mistral Small 4, Ministral 8B, or Haiku 5.5 on Bedrock EU) at about $2–4 per site per week. Benchmark them against Medium 3.5; don't default to Medium.
- **50–300 sites:** stay on the API. Cut tokens with prompt caching, event-triggered calls and fewer sustainability-agent calls. Add a Jetson only for offline-critical clients.
- **300–1,000 sites:** evaluate self-hosting a 24B (H100 pair) or 8B (L40S). Measure vLLM throughput and include ops cost.
- **Over 1,000 sites:** self-host 8–24B in an EU cloud, with the API as a cascade for hard cases. A Revolut-style platform makes sense at about 5–10k sites.
- **At any size, choose by client constraint:** EU API if a DPA is acceptable; EU self-host if third-country processors are banned; on-device 3–8B for fallback or offline-only sites.

## References
- Mistral: https://docs.mistral.ai/inference/pricing ; https://mistral.ai/pricing ; https://docs.mistral.ai/getting-started/models
- Medium 3.5 (E): https://pricepertoken.com/pricing-page/model/mistral-ai-mistral-medium-3.5
- Claude: https://platform.claude.com/docs/en/about-claude/pricing ; https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock ; (E) https://www.requesty.ai/models-new/bedrock/claude-haiku-5-5-eu-north-1
- Revolut: https://www.theregister.com/a/5307345 ; https://ibl.ai/blog/revolut-self-hosted-open-models-ai-coding-costs ; https://www.computing.co.uk/news/2026/ai/revolut-turns-to-self-hosted-ai-to-cut-coding-costs-tenfold-over-claude
- GPUs: https://computeprices.com/providers/scaleway/gpus/l40s ; https://www.spheron.network/blog/ovhcloud-gpu-pricing-2026-h100-cost-and-sovereign-ai/
- Edge: https://computingforgeeks.com/edge-llm-jetson-orin-vs-ai-hat-2-vs-hailo-10h/
- AI Act Omnibus: https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/
