# 07: Self-hosting, memory learning, and a simpler framework

Date: 2026-11-17. There were four research passes: an architecture review, edge hardware, LLM memory design, and market and pricing.
Figures marked **(unverified)** come from agent knowledge and were not checked against a source. Re-check them before quoting.

## 1. Architecture review of the simple framework
- **The design is close to minimal.** It fixes the observed problems: a 15-min LLM debate, export valued at zero, a fixed 80% target, and a sustainability agent with no price or CO2 input.
- **Cut 1: the LLM writes knobs, not setpoints.** It outputs 3–4 knobs per day: evening reserve kWh, grid-charge window, and discharge priority. It should not write 96 kW setpoints. A small model writing 96 numbers is the weakest link. Knobs fail gracefully, because the rule turns them into kW using live SoC.
- **Cut 2: λ (€ per kg CO2) is an owner dial in config.** The LLM does not reason about it.
- **Add 1: measure regret against the self-consumption rule**, so no LP is needed.
- **Add 2: a replay gate.** Ship only if the new design beats the rule on logged weeks.
- **Add 3: test Step 1 on its own first, on today's model.**
- **Failure handling:**
  - Model down → keep the last valid plan (TTL 24 h), then fall back to the rule.
  - Bad output → schema check, bounds, and clamp to SoC 0.1–0.9 and ±5 kW. If the simulated plan is worse than the rule, use the rule.
  - Stale plan → replan when SoC drifts more than 1 kWh from the plan.
  - Plan after day-ahead prices are out (~13:00 CET).
- **One agent instead of two:** both agents control the same single number, the battery kW. The money-vs-CO2 trade-off is a policy choice. The owner should set it once, not have bots renegotiate it 96 times a day.

## 2. Edge hardware (8B model, Q4, ~5k-token prompt)
Prefill (reading the prompt) dominates time, not generation. Prices and speeds are **(unverified)** unless a source is given.

| Hardware | RAM | Est. time per call | Verdict |
|---|---|---|---|
| Raspberry Pi 5 8 GB | 8 GB | 2–6 min | Rule + 3–4B model only |
| Jetson Orin Nano Super 8 GB (67 TOPS, 102 GB/s, [NVIDIA](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/)) | 8 GB shared | 15–45 s | Works, but tight on memory |
| Jetson Orin NX 16 GB | 16 GB | 10–35 s | Comfortable |
| x86 N100 gateway | 16–32 GB | 1–2.5 min | Too slow for 8B |

- **Memory per call:** weights ~4.5 GB at Q4. The KV cache (the model's working memory for the prompt) is ~0.3 GB (Qwen2.5-7B) to ~0.6 GB (Llama-3.1-8B) for 5k tokens.
- **Ops:**
  - Push model weights (~5 GB) by signed manifest plus an HTTPS pull from EU storage, not over the IoT message channel. Use A/B slots with rollback.
  - Cap the Jetson at 15 W in closed cabinets.
  - At 1–6 calls a day, heat is not an issue.

## 3. Cost: self-host vs API at the new call volume
- Proposal volume: about 1–6 calls a day × ~5k tokens = 5–15k tokens/day. Today config C uses 2.7M/day, so that is **~180–540× less**.

| Option (per site per year) | 1 site | 100 sites | 1,000 sites |
|---|---|---|---|
| EU API at Devstral-class prices ($0.40/$2.00 per M) | ~$9 | ~$9 | ~$9 |
| EU API, small model (OVH Qwen3.5-9B €0.10/€0.15, Mistral-Small-3.2 €0.09/€0.28 per M, [OVH](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/)) | ~€2 | ~€2 | ~€2 |
| Edge Jetson (~€400 over 5 yr + power) **(unverified)** | ~€90 | ~€90 | ~€90 + ops |
| Self-hosted EU GPU, batched **(unverified)** | €4–13k | €40–130 | €10–25 |

- **Conclusion:** after the call cut, cost is no longer a reason to self-host. Self-host for:
  1. **Data residency.** 15-min home load data is personal data under GDPR.
  2. **Offline operation.**
  3. **Model churn.** Mistral gives 6 months' notice ([lifecycle](https://docs.mistral.ai/models/model-lifecycle)). Devstral 2 is retired, and [Medium 3.5 is deprecated](https://docs.mistral.ai/models/model-cards/mistral-medium-3-5-26-04) from 2026-10-31 in favour of Large 4.
- **Break-even for a GPU fleet against cheap open-model APIs** is billions of tokens per month ([Cohorte, Sept 2026](https://cohorte.co/blog/self-hosted-llm-cost-vs-api-break-even)). Engineering and on-call often cost more than the GPUs themselves.
- **Small 4 price is uncertain:** $0.10/$0.30 (Mistral page snippet) vs $0.15/$0.60 (aggregators). Re-check before quoting.

## 4. "Learning from the past" without training
- **Method:** case-based reasoning ([Aamodt & Plaza 1994](https://doi.org/10.3233/AIC-1994-7104)) with in-context retrieval. Closest pattern: [ExpeL](https://arxiv.org/abs/2308.10144) (AAAI 2024). Show past plans next to their scores, as in OPRO ([arXiv 2309.03409](https://arxiv.org/abs/2309.03409)). Similar examples beat random ones (Liu et al. 2022, DeeLIO).
- **Caveat:** most gains are shown with GPT-4-class models. Small models lean more on priors (Wei et al. 2023, [arXiv 2303.03846](https://arxiv.org/abs/2303.03846)).
  - Test: LLM vs a **non-LLM baseline that copies the knobs of the nearest low-regret day**.
  - If the 7B model doesn't win, its value is explanation, not decisions.
- **Complexity:**

| Item | Size |
|---|---|
| Storage | 1 row per day ≈ 20 numbers ≈ 1 KB → < 1 MB per site per year |
| Retrieval | Brute-force k-NN, O(D·d) = 3,650 × 10 operations ≈ 5 ms in pure Python. No vector database. |
| Prompt | ≈ 4k + k × 120 tokens; with k = 5, ≈ 4.6k |

- **Safeguards:**
  - Retrieve only low-regret days, and show the regret.
  - Recency half-life of ~60 days.
  - Add season sin/cos and `pv_dirt` as features.
  - Minimum similarity, else use the rule.
  - Store forecast error separately.
  - Explore ~5% of days within safe bounds.
- **LoRA fine-tune: later.** Only once there are ≥ 2–5k pooled days, in-context learning has stopped improving as k grows, and the gain is > €0.05 per site per day on a held-out season. These thresholds are our rule of thumb. Supporting papers: [LoRA](https://arxiv.org/abs/2106.09685), Mosbach et al. 2023.

## 5. External evidence and market
- [arXiv 2607.04569](https://arxiv.org/abs/2607.04569) (2026): a **single** ReAct agent for home energy management, run over 7 days, captures 96.7–98.0% of the savings available against an off-peak-timer baseline, measured against a MILP oracle. It reports fabricated schedules and invalid commits, so it requires a deterministic validator. This supports "one agent + clamp".
- [arXiv 2603.08477](https://arxiv.org/abs/2603.08477): behaviour found by a strong model transferred to a smaller LLM through in-context examples.
- **No paper found** that tests single-agent vs multi-agent battery dispatch against an MPC baseline. Do not imply evidence either way.
- **Market:**
  - Home batteries are price-first: Tibber Smart Battery and sonnen VPP.
  - CO2 appears as a user weight or as a side effect:
    - Monta SmartCharge uses [Electricity Maps](https://electricitymaps.com/industries/smart-charging) for CO2.
    - An unofficial Octopus Homey app has a "greenness" slider.
  - So a tunable CO2 weight is a differentiator, not an industry standard.
