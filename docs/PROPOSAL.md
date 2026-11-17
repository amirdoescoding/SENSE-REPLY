# Executive summary and proposal

**For:** the Sense Reply platform and commercial teams.
**Evidence:**
- one simulated week (5–12 Jan 2026) and three runs (`data/DatasetV4/`);
- the agent prompts and asset files;
- the ENTSO-E hourly carbon intensity for Italy (assumed site).

Details are in `KPIS.md` (dashboard and trade-off matrix), `TIMESERIES.md` and `research/07`.

## 1. Verdict
**Keep sustainability as a goal, but drop the second agent.** Merge the two into one agent and give it the inputs it lacks.

The clean test is run C (Cost + Sustainability) vs run A (Cost only), on the same panels. Each run is measured against its own rule baseline, and all figures are corrected for the different battery level at the end of the week.

| What adding the Sustainability agent changed | Per week |
|---|---|
| Energy bill | **€0.02 lower** (no real change) |
| Grid CO2 | **1.5 kg less** (−6%) |
| Grid import | 3.8 kWh less |
| Peak grid draw (99th percentile) | 2.5 kW instead of 3.1 kW |
| Grid penalties | none in either run |
| LLM bill | **+€3.0** (7.6 instead of 4.4 calls per 15-min decision) |
| **Cost per tonne of CO2 avoided** | **≈ €2,000/t**, 20–25× the EU carbon price |

There is a bigger problem than the choice between 1 and 2 agents:
- **A free rule beats both setups**: €0.40–0.70 cheaper and 10–12 kg less CO2 a week.
- **The AI costs 7–12× what the battery saves.**

The agents are not reasoning badly. They follow their instructions.

## 2. Why: the instructions, not the intelligence
- **Fixed 80% target** (`BSS.json` `targetStateOfCharge`). The battery fills by 11:00, partly from the grid at morning prices, then sits full while ~4 kWh of midday sun is exported each day.
- **Export valued at zero.** Both prompts say surplus "is not valued", so exporting looks free. In the real bill it is sold at ~€0.09, then bought back at €0.11–0.12 in the evening.
- **The Sustainability agent is blind.** Its prompt has **no price and no CO2 input**. It can only push "import less", so it never times imports to cleaner hours (both runs buy at hours 5% dirtier than average).
- **Two agents control one number.** Both set the same battery kW. A debate every 15 minutes adds calls but no new information.
- **This week, price and CO2 point the same way** (clean midday, dirty evening peak). So fixing the habits above helps both money and CO2.

## 3. The proposal: one agent, carbon-aware, learns from past days
Built on the existing prompt stack. Each step is small and is measured before the next one starts.

**Step 1: one merged prompt (days of work).**
- One agent with one goal: **€ + λ × kg CO2**. λ is a dial the owner sets in config, for example €0.10/kg. The agent does not debate it.
- Give it the **price** and the **hourly grid CO2** (ENTSO-E, already built in `analysis/carbon.py`).
- Value export at `sellPrice`.
- Replace the fixed 80% target with "keep enough for tonight's evening load".
- Test this on today's model first. It should capture most of the gain on its own.

**Step 2: plan once a day, act with a rule (days of work).**
- The agent runs once a day, after day-ahead prices are out (~13:00), plus one replan if the battery drifts more than 1 kWh off plan.
- It returns **3–4 knobs, not 96 numbers**: evening reserve kWh, grid-charge window (or none), and discharge priority.
- A plain rule turns the knobs into kW every 15 minutes from live SoC. A safety clamp enforces SoC 10–90% and ±5 kW.
- **If the LLM is down or returns nonsense:** keep yesterday's plan (valid 24 h), then fall back to the self-consumption rule. The battery is never unmanaged.

**Step 3: learn from past days, with no training (1–2 weeks).**
- **Every evening:** store one row with the day's context (sun, load, price and CO2 spread, start SoC), the knobs used, the € and CO2 result, and the regret (the loss vs the rule baseline).
- **Every morning:** show the agent the 3–5 most similar past days that went well.
- **Safeguards:** good days only, recent days weighted more, a season feature, and fall back to the rule if no past day is similar enough.
- **Honest test:** compare the agent against a plain "copy the knobs of the most similar good day". If a small model doesn't beat that, its value is the explanation, not the decision.

**Ship gate:** each step goes live only if a replay on logged weeks beats the rule baseline.

We ran this replay for the knobs (`analysis/replay.py`). This January week:
- the best setting is "no reserve, no grid charge" = the plain rule;
- a 20% reserve costs +€0.12/wk;
- a night grid charge costs +€0.13–0.22/wk and adds 5–10 kg CO2.

So a wrong knob loses money, and the gate is not optional. The LLM earns its place only on days where a different knob wins: summer surplus, price or CO2 spikes, the owner away. Test this on more weeks. If it never wins, run the rule and keep the LLM for explanations.

**Later scenarios (only if the data justifies them):**
- ML forecasts for load and CO2 (our test already cuts CO2 forecast error by 40%: FC2 = 0.40);
- an optimiser instead of the rule;
- a LoRA fine-tune once ≥ 2–5k good days are pooled across sites.

```
 13:00 daily ─┐
 prices + CO2 forecast + 3–5 similar past days ──► ONE agent (small LLM) ──► 3–4 knobs + "why"
                                                                                │
 every 15 min: live SoC, PV, load ──► rule turns knobs into kW ──► safety clamp ──► battery
                                                                                │
 every evening: log day (context, knobs, €, CO2, regret) ──► memory ◄────────────┘
 LLM down / bad output → yesterday's plan → self-consumption rule
```

## 4. Time and space: today vs proposal

| | Today (C) | Proposal |
|---|---|---|
| LLM calls per day | ~730 | 1–3 |
| Input tokens per day | ~2.7 M | ~5–15 k (**~180–540× less**) |
| Time to decide each 15 min | up to ~18 s, on the control path | < 1 ms (rule); LLM off the control path |
| LLM time per call on edge hardware | (cloud only today) | ~15–45 s on a Jetson Orin, fine once a day |
| Memory | none | 1 row/day ≈ 1 KB, **< 1 MB per site per year** |
| Retrieval | – | scan of all past days, O(days × 10 features): ~5 ms for 10 years, no database needed |
| Prompt growth | – | +~120 tokens per example; 5 examples ≈ 4.6 k tokens total |
| Model memory on device | – | ~4.5 GB weights (8B, 4-bit) + ~0.3–0.6 GB working memory |

## 5. Self-hosting: when and why
- **Cost is no longer the reason.** After the call cut, a cheap EU API costs about **€2–9 per site per year**. A Jetson edge box costs about **€90 per site per year**. A batched self-hosted GPU pays off only for fleets in the thousands.
- **Self-host when the client needs any of these:**
  - **data residency**: 15-min home load is personal data under GDPR;
  - **offline operation**;
  - **independence from model retirements**: Mistral retires models with 6 months' notice. Devstral 2 is gone, and Medium 3.5 is already deprecated.
- **Recommended path:**
  1. Run the same prompt on a cheap EU API (Mistral Small or open models on an EU host).
  2. Offer a **Jetson Orin–class gateway with a 7–8B model** for clients who need on-premise or offline operation.
  3. A Raspberry Pi 5 runs the rule and at most a 3B model.
- **Supporting evidence:** a 2026 study (arXiv 2607.04569) found a **single** LLM agent with a deterministic validator reached 97–98% of the best possible home-energy savings. It also reported made-up schedules without the validator, which supports the safety clamp.

## 6. What this means for Sense Reply
- **Fewer moving parts.** One agent, one goal, one dial. It is easy to explain to a client and easy to audit ("why did it do that?").
- **Carbon becomes a real feature.** Today the "sustainability" agent never sees CO2. With an owner-set €/kg dial it does, and commercial home batteries are still price-only, so this is a differentiator.
- **The LLM bill drops from €4.7–7.7 to cents per week**, which makes local models practical where clients need them.
- **To measure agent quality properly**, log every plan, its knobs and its outcome from day one.
