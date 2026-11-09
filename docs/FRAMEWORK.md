# New agent framework: proposal

For: team consolidation session. Simple words.
Built from: the KPI results (`docs/KPIS.md`), research reports `docs/research/00`, `05`, `06`, and two independent redesigns (agent-organizer and multi-agent-coordinator). Where they disagree, both views are shown.
Diagram: `docs/diagrams/framework.png` (source: `framework.mmd`; the `.excalidraw` opens as one image, not box by box). Web version: https://claude.ai/artifact/ENAndsWgSqt9YYqYxMuY9W

## 1. What is wrong today (from the data)
- **The LLM is both the brain and the hands.** It picks the kW every 15 min. That is expensive and slow, and it is not better than a simple rule.
- **The AI costs about 10× what the battery earns.** LLM €4.7 (A) / €8.2 (B) per week, against about €0.7 per week of savings vs no battery.
- **Bad habit:** the agents keep the battery half full for the evening peak, so they export sunny-hour power at €0.09 instead of storing it.
- **The second agent doubles calls** (4.4 → 8.2 per decision) and latency (10 → 20 s). On energy it is not worse: B is a bit cheaper and greener than A against its own baseline.
- **Agents grade their own homework.** Self-scores are not checked, and LLMs favour their own answers (research `06` §3).
- **No learning.** The orchestrator forgets every decision.
- **No carbon signal.** The sustainability agent is probably guessing.
- **No logs of proposals.** We cannot measure agent or orchestrator quality.
- **No forecasts used well.** The evening peak is almost identical every day, yet agent A still had 7.3 kWh left at sunrise each week, worth €0.79 (§7b).
- **Devstral 2 was retired on 2026-07-31.** Hosting needs a plan anyway.

## 2. Core idea (both redesigns agree)
> **The optimiser sets the kW. The LLM sets the strategy a few times a day. A simulator checks. A safety clamp has the last word. The simple rule is the floor.**

- **Optimiser** = an LP/MPC (linear program / model predictive control). This is maths that plans the battery for the next 24 h using forecasts and prices, recomputed every 15 min. It runs on the gateway in under 1 s with no internet.
- **Strategy LLM** = one agent that picks weights (cost vs CO2), the reserve SoC and the mode ("hold for peak" or not), and explains why. It is called every 1–4 h, or when something changes.
- **Simulator (digital twin)** = Sense Reply's existing twin. It scores each candidate plan with real numbers: €, kg CO2, min SoC, unmet load. Self-scores are no longer used.
- **Safety clamp** = hard limits (power, SoC, ramp, grid). It is plain code and always last.
- **Rule floor** = the simple rule is always one candidate, so the pick is never worse than the rule *on forecast*.

## 3. How many agents? 1 vs 2 vs N
Scores are 1 (bad) to 5 (good). They are the organizer's estimates, not measured.

| Option | Energy | LLM calls / decision | Speed | Robust | Explainable | Easy to build |
|---|---|---|---|---|---|---|
| **(a) 1 strategy LLM + optimiser** ✅ | 4 | about 0.1–0.3 | 5 (<1 s) | 5 | 4 | 4 |
| (b) Today: 2 agents + orchestrator | 2 (below rule) | 4.4 / 8.2 | 1 (10–20 s) | 2 | 2 | 5 (exists) |
| (c) N specialist agents | 3 | 10+ | 1 | 2 | 3 | 1 |

**Pick (a).** Why:
- The problem is the decision rule, not missing opinions. More agents add calls, not skill.
- Research: at the same token budget, debate rarely beats one agent (research `06` §2).
- Our two agents don't check each other. They just argue.
- Forecasting, tariff and battery health are better as **code or small models**, not LLM agents.
- **Sustainability becomes a weight (λ) in the optimiser, not an agent.** No extra LLM calls. The LLM gets a "carbon trigger" only when the grid CO2 swing is big.

**Disagreement to discuss (coordinator's warning):** if a learned tuner sets λ well, the LLM may add almost nothing. **Test a "no LLM" version too.** Sense Reply's agent story gets weaker, but the numbers decide. Our answer: the LLM still adds value for events (storm warning, user away, tariff change), for explanations to users, and for talking with the human.

## 4. Who does what
| Part | Decides | How often | Inputs | Runs where |
|---|---|---|---|---|
| Strategy LLM | weights (€, CO2, reserve, comfort), reserve SoC, mode, plus a short "why" | daily plan + every 1–4 h + on events | price, PV/load/CO2 forecasts, SoC, similar past cases | cloud (EU API) |
| Forecasters (code) | PV, load and CO2 for the next 24 h | 15 min | weather, history, ENTSO-E | edge |
| Optimiser (LP/MPC) | 3–5 candidate kW plans, one per weight set | 15 min | strategy + forecasts + battery limits | edge |
| Digital twin (verifier) | real scores for each candidate | 15 min | same | edge |
| Arbiter (code) | the final pick, by fixed rules (§5) | 15 min | twin scores | edge |
| Safety clamp | cut the kW to safe limits; write the setpoint | 15 min | kW, SoC, limits | edge |
| Rule fallback | backup kW; always a candidate | 15 min | PV, load, SoC | edge |
| Local small LLM | strategy when the cloud is down | only on cloud loss | same as strategy | edge (Jetson) |
| Logger | writes everything + regret 24 h later | 15 min | all | edge → cloud |
| Twin trainer | tunes λ / reserve, tests prompts, builds the policy set | nightly | logs | cloud |
| Human | approves risky actions | on alert | escalations | cloud console |

**Shared state ("blackboard", from the coordinator).** This is one shared table of facts. Each part writes only its own keys, every key has a timestamp, and old data expires.
- **Expiry times:** telemetry 1 slot, forecast 6 h, price 24 h, CO2 24 h (if missing, λ = 0 and flagged), strategy 4 h.

**Timing inside each 15-min slot:**
- T−120 s: snapshot.
- T−110 s: optimiser.
- Then: twin scores, arbiter picks, clamp.
- T−30 s: setpoint written.

The LLM is **never** on this path. It runs on the side and only updates the strategy.

## 5. How the final kW is chosen (arbitration)
1. **Candidates:** optimiser plan(s) under the current strategy + last valid plan + rule plan (+ carbon plan if the trigger fired).
2. **Feasibility filter:** drop anything that breaks SoC, power, reserve or unmet-load limits.
3. **Cheapest within ε:** keep plans within 2% (or €0.02/day) of the best cost.
4. **Lowest CO2** among those.
5. **Tie-break:** smallest change from the last kW (less wear).
6. **Clamp**, then write.

This is a fixed sort order, so it cannot deadlock and it is easy to audit. An LLM only writes the explanation, never the choice.

**Call the human when:**
- a reserve override is needed;
- the best plan costs more than the rule by more than €0.10/day;
- 3 or more clamps happen in 1 h;
- the strategy flips more than 2 times in 6 h.

If the human doesn't answer, keep the safe default. Never wait.

## 6. When things break
| Failure | Action |
|---|---|
| Cloud down | Keep the last strategy until it expires → local small LLM → default strategy. **The optimiser never needs the cloud.** |
| LLM gives bad output | Check against the schema and ranges, retry once, then keep the old strategy and count the error. |
| Old data | Telemetry: re-read, else use the rule. Forecast: assume tomorrow = today. CO2: λ = 0, flagged. |
| Unsafe kW | The clamp cuts it and logs the proposed vs applied value. Repeats raise an alarm. |
| Late or double write | Idempotent setpoint: key = (site, slot, version), so applying it twice = once. No setpoint means the inverter does local self-consumption. |
| Gateway restart | Resume from the last logged decision. |

## 7. The learning loop ("loop engineering")
**What the word means:** "loop engineering" is a new, informal term (June 2026, from coding agents). It is not an academic term. The proper name for what we want is **closed-loop control with learning from outcomes**: act → measure result → learn → act better. The gateway already loops every 15 min. What is missing is the **learn** step. (research `06` §1)

**Key signal: regret.** Regret = what we really paid − what the best hindsight plan would have paid. It is computed 24 h later, for every slot. Every learning step below uses regret, not self-scores.

| Stage | Weeks | What | Go-live gate |
|---|---|---|---|
| **S0 Log** | 0–2 | Log every candidate, score, pick, applied kW, prompt version, tokens and regret. Use OpenTelemetry → Langfuse (self-hosted, EU). | 100% of slots logged; agent KPIs computable |
| **S1 Hybrid** | 2–5 | Optimiser + twin scoring + arbiter + clamp + rule floor + one strategy LLM. | Beats the rule on twin replay of the same week |
| **S1.5 Forecasts** | 4–8 | Supervised load + CO2 forecasts (P50/P90) feed the optimiser; soiling/fault model on PV (§7b). | Skill vs naive > 0; over-reserve (FC5) falls; P90 covers ≥ 90% of evenings |
| **S2 Memory** | 5–8 | Store low-regret past cases. Give the LLM the k most similar as examples. Prune bad ones. Reflect on regret. (Reflexion / ExpeL pattern) | Regret falls on held-out days |
| **S3 Prompt tuning** | 8–12 | Test prompt versions on the twin and keep the one with the lowest regret (DSPy-style). | Lower regret, no new violations |
| **S4 Self-tuning weights** | 12–20 | A **contextual bandit** picks λ and the reserve. A bandit is a learner that tries settings and keeps what works. Context: price spread, PV forecast, CO2 spread, SoC. Reward: −(€ + λ_user·CO2). Train in the twin, then shadow mode, then live. Needs the carbon series. | Beats fixed λ in shadow mode |
| **S5 Many policies (MODRL)** | later | Precompute a set of plans for many cost-vs-CO2 weights, so the user moves a slider and the system switches at once with no retraining (MODRL briefing). | More than 2 Pareto points; RL must beat the optimiser on the twin |

**Rules for learning:**
- **Learn in the digital twin, not on the house.** 672 real samples are far too few for RL.
- Every learned part runs in **shadow mode** first (it decides but does not act). It goes live only if it beats the current version on the twin.
- The clamp is always last. Weights stay inside fixed ranges.
- RL warning: one study found naive RL did **worse than no battery**, while MPC got 99% of the optimum (research `06` §5).

**Disagreement on S5:**
- **Organizer:** train a true MODRL policy set in the cloud and run a small policy on the edge.
- **Coordinator:** just sweep the optimiser over λ (cheap, same result), and use RL only if it beats the optimiser.
- **Our view:** start with the λ sweep. Go to RL only if the twin shows a gain.

## 7b. Supervised learning: forecasts and panel health
**What it is:** a model learns from past examples where the answer arrives later ("what was the load at 19:00?"). It suits **predictions**. RL (§7 S4–S5) suits **decisions**. Different jobs, different places.

**Where it sits:** the **Forecasters** box on the gateway runs the small models every 15 min. The **Twin trainer** in the cloud retrains them every night from the **Logger** data. No LLM is needed.

**Scope (team choice):** three targets.
1. **House load**, next 24 h.
2. **Grid CO2**, next 24 h.
3. **Panel soiling and faults**: estimate how dirty the panels are, flag faults, suggest when to clean.

PV forecast from weather is out of scope for now.

### What our week says (`python3 analysis/forecast_check.py`)
| Check | A | B | What it means |
|---|---|---|---|
| Load error, "same as yesterday", per 15 min | 18% | 19% | Single steps are noisy |
| Evening peak 17–22h, kWh per day | 10.4–10.6 | 9.8–10.7 | **The peak is almost the same every day** |
| Evening peak error, "same as yesterday" | 0.8% | 4.2% | Even the dumbest forecast nails the peak |
| Battery energy still left at sunrise (could have replaced night imports) | 7.3 kWh | 1.6 kWh | The agent kept too much |
| € a perfect plan would recover from that | **€0.79/wk** | €0.16/wk | For A, this is more than the whole gap to the rule (€0.70) |
| PV lost to dirt | 12 kWh (€1.0–1.2) | 36 kWh (€2.9–3.7) | **Bigger than what the battery saves** (about €0.7) |
| Dirt growth | +0.024/day | +0.024/day | Linear, all 9 panels equal, never cleaned |
| CO2 error, "same as yesterday", hourly | 8.7% of mean | same | CO2 is fairly predictable |
| CO2 error, yesterday + ENTSO-E day-ahead wind/solar/load correction | **5.2% of mean** | same | **FC2 skill 0.40**: the public forecasts cut the error by 40% |
| Cleanest / dirtiest hour | 12:00 (314 g) / 20:00 (384 g) | same | Daily swing is only 19% of the mean |

**New fact:** in this simulator, PV = clean PV × (1 − dirt), exactly. The B/A PV ratio equals the dirt ratio at every daytime step. So **both runs had the same weather**, and the whole PV gap (93 vs 69 kWh) is dirt.

### What it means, target by target
- **Load: a decision problem, not a forecast problem (in this simulator).** The peak is easy to predict, but the agent still keeps too much energy overnight. The fix is to *give the forecast to the optimiser* and let maths size the reserve:
  - Needed reserve = forecast evening + night load − what PV will refill, plus a safety margin.
  - The margin comes from the forecast error. Use a high-end forecast (the 90th percentile) instead of the average. This is **quantile forecasting**: predict a range, not one number.
  - Real homes are much noisier than this simulated house (holidays, guests, EVs), so in the field the model matters more than it does here.
- **CO2: cheap win, and the day-ahead data makes it better.** "Same as yesterday" is already 91% right. Adding ENTSO-E's free day-ahead wind/solar and load forecasts brings it to about 95% (error 8.7% → 5.2%, FC2 = 0.40).
  - Model: CI_t = CI_{t−24} + a + b·Δx, where x = 1 − (wind+solar forecast)/(load forecast), the share of load left for thermal plants. One slope, stdlib only, trained 1 Dec–4 Jan and tested on the dataset week (`analysis/forecast_check.py`). Each +0.1 of residual-load share adds about 56 g/kWh (correlation 0.89).
  - Caveat: one test week. Training covers Christmas/New Year, and the test week has 6 Jan (Epiphany). Treat 0.40 as indicative and re-run on more weeks.
  - This week the dirtiest hour (20:00) is also the price peak, and the cleanest (12:00) is the PV peak. **Cost and CO2 point the same way.** That explains why adding the sustainability agent barely changed the energy result.
  - A CO2 forecast still matters on windy or sunny days, when CO2 and price separate. It also gives the sustainability side a real signal; today it buys at hours 5% dirtier than average (KPIS.md S3).
- **Soiling: biggest € in the simulator, but the simulator exaggerates it.**
  - The simulator dirties panels at 2.4% per day with no cleaning.
  - Real dry spells run about 0.1–0.3% per day, and in Italy rain keeps the yearly loss near 0.4–1% (Fernández Solas et al. 2025, Renewable Energy; PV-KLIMA Ancona site).
  - So for an Italian home, soiling alone is worth a few € per year. The bigger value is **fault and underperformance detection** (broken string, inverter faults, shading), plus soiling for dusty southern sites, C&I roofs and solar farms.
  - Real sites have **no dirt sensor**. The model has to infer dirt: expected clean PV (from weather/irradiance and neighbouring sites) vs measured PV. The gap, trend and sudden drops become "dirty", "fault" or "check" alerts.

### Design
| Part | Simple first | Then | Why |
|---|---|---|---|
| Load model | "Same as yesterday" / mean of the last 7 days | LightGBM (gradient-boosted trees) on hour, weekday, holiday, temperature, last days. **Quantile output** (P50 and P90). | Trees win on small tabular data and run on Raspberry-class hardware |
| CO2 model | Same as yesterday + day-ahead correction (tested: FC2 0.40) | Trees on hour, weekday, ENTSO-E day-ahead load and wind/solar forecasts | ENTSO-E already publishes day-ahead inputs |
| Soiling / fault model | Performance ratio: measured PV ÷ expected PV, trend per day | Regression for expected PV (irradiance, temperature, sun angle), then trend + change-point alerts | Explainable alerts a technician trusts |
| Training | Cloud, nightly, per site + fleet model | Fleet model warm-starts new sites (cold start) | One week per site is too little alone |
| Running | Gateway, every 15 min | Same | Works offline, no LLM cost |
| Watching | Forecast error per day | Drift alarm if error > 2× normal for 3 days → retrain | Models age when the house changes |

### Forecast KPIs
| KPI | What it measure | Formula | Why |
|---|---|---|---|
| FC1 Load MAE | Average forecast miss | mean abs(forecast − actual), kWh | Basic accuracy |
| FC2 Skill vs naive | Better than "same as yesterday"? | 1 − MAE_model / MAE_naive | Below 0 = the model is useless |
| FC3 Peak coverage | Did the P90 forecast cover the evening? | share of days with actual 17–22h kWh ≤ P90 | Reserve safety |
| FC4 Value of forecast | € lost to imperfect forecasts | cost(plan with forecast) − cost(plan with perfect forecast), on the twin | The KPI that matters: accuracy only counts where it changes money |
| FC5 Over-reserve | Energy left at sunrise that could have replaced night imports | Σ_days min(usable SoC at first PV surplus, night imports) | Today: 7.3 kWh (A), 1.6 kWh (B) per week |
| FC6 Soiling loss | PV lost to dirt | Σ PV·d/(1−d), in kWh and € | Today 12 / 36 kWh (simulator) |
| FC7 Alert quality | Are maintenance alerts right? | precision = true alerts / all alerts; lead time = days between alert and big loss | False alarms cost truck rolls |

### Business angle: forecasting and panel health as platform features
- **No LLM needed, so they work for every client** and keep working offline. Sense Reply sells a *platform*, a base clients build on (transcript), and forecasts plus health checks are features that every vertical reuses: homes, energy communities, EV charging, C&I.
- **It turns their biggest problem into an asset.** In the lecture, managing terabytes of grid data was named the biggest unsolved problem. That data is exactly the training set for fleet forecast and health models. More sites mean better models, which a single-site competitor cannot copy.
- **It speaks to both buyers in a client** (from the lecture):
  - **Business:** "€ saved per site per year, cleaning trips avoided, faults found earlier".
  - **IT:** "small models, on the gateway, EU data stays local".
- **It is what the market already pays for.** Utility optimisers (Fluence, Stem, Kraken) sell *ML forecasting + optimisation*, not LLMs (research `03`). This puts Sense Reply on a proven footing, with the LLM as the extra layer for events and explanations.
- **Packaging idea:**
  1. **Monitor tier:** health alerts and soiling/fault detection.
  2. **Optimise tier:** forecasts + optimiser control the battery.
  3. **Agent tier:** strategy LLM, explanations, human chat.

  Each tier makes the next one better.
- **Honest limits:**
  - For a single Italian home, soiling is worth only a few € per year, so the value case is **faults + forecasts across a fleet**, or sunnier, dustier and larger sites.
  - Price per site is unknown. We found no reliable public price list. Ask Sense Reply, and test willingness to pay in the year-1 interviews.
- **What they need to start:** at least 3–6 months of 15-min data per site (to see weekdays, holidays and seasons), fleet data for cold start, weather or irradiance per site, and a cleaning or maintenance log (to label alerts as true or false).

## 8. Hosting: which model, where?
**Revolut check:** Revolut self-hosts open models (GLM) on 56 B200 GPUs for **coding help** for about 2,000 engineers. They report about $0.30 per M tokens, about 1/10 of frontier APIs. No "millions saved" figure was found (research `05` §1).
- **Transfers to us:** at big, steady volume, owning GPUs is cheaper; keep an API for hard cases.
- **Does not transfer:** cheap EU APIs (Mistral Small 4 ≈ $0.17/M blended) are **already below** Revolut's self-host cost. We are a few sites, not 2,000 heavy users.

**Cost per site per week, today's B call volume (research `05` §5):**

| Option | $/site/wk | Note |
|---|---|---|
| Devstral 2 (what was used) | 9.56 | retired |
| Mistral Medium 3.5 (official replacement) | 35.9 | 10× dearer, so don't default to it |
| Mistral Small 4 (EU API) | 3.47 | about $1.3 with prompt caching |
| Claude Haiku 5.5 on Bedrock EU | 2.63 | EU endpoints in Milan, Frankfurt, Paris…; regional = +10% |
| Self-host 24B on 1 H100 (EU cloud) | 504 at 1 site → 2.0 at 1,000 | break-even about 150–600 sites |
| Edge Jetson + 3–8B model | about 2.5 flat | quality untested |
| **New design (0.1–0.3 calls/decision)** | **about 0.1–0.5** | the call cut matters more than hosting |

**Recommendation:**
- **Under about 300 sites:** EU API. Benchmark Mistral Small 4 vs Haiku 5.5 (Bedrock EU) on the twin. Pick on regret per €.
- **Above about 300–1,000 sites:** test self-hosting a 24B model in an EU cloud, with the API kept for hard cases.
- **On the gateway:** a 3–8B model on a Jetson as the offline strategist only. A Pi 5 is too slow.
- **Always:** put one interface in front of the model so swapping it is a config change (models get retired, and the EU Data Act favours portability).
- **The real driver for self-hosting at small scale is data residency, not cost.** 15-min home data is probably personal data under GDPR, so you need EU-only processing and a DPA (Data Processing Agreement) with the provider. Home battery optimisation is probably not "high-risk" under the AI Act, but fleet grid services could be. Check with legal.

## 9. KPIs that prove the new design works
Every KPI is defined in `docs/KPIS.md`. Targets:

| Level | KPI | Today | Target |
|---|---|---|---|
| System | F1 net value vs rule (€/wk) | −5.4 / −8.6 | > 0 |
| System | F2 LLM cost / savings | 7× / 11× | < 0.2× |
| System | C3 savings vs rule | −30% / −9% | ≥ 0 by design (rule is a candidate) |
| System | S2b CO2 vs rule (hourly CI) | −12.2 / −6.7 kg | ≥ 0 |
| System | S3 import CI vs grid mean | +4.8% / +4.8% (dirty hours) | below the grid mean |
| System | Pareto points (cost vs CO2) | 2 | slider, many points |
| Strategy LLM | O1 calls / decision | 4.4 / 8.2 | < 0.3 |
| Strategy LLM | Regret per day | unknown | falling each stage |
| Strategy LLM | Invalid-output rate, timeout rate | unknown | < 1% |
| Arbiter | Arbiter regret, selection share | unknown | logged from S0 |
| Ops | Fallback rate, deadline misses, clamp rate | unknown | 0 missed slots |
| Forecasts | FC5 over-reserve at sunrise | 7.3 / 1.6 kWh/wk | near 0 without unmet load |
| Forecasts | FC2 skill vs naive; FC3 P90 peak coverage | n/a | > 0; ≥ 90% |
| Panel health | FC6 soiling loss; FC7 alert precision | 12 / 36 kWh/wk (simulator) | alert before loss > 3%; precision ≥ 80% |

**Fair test:** replay the old configs A and B and the new design on the **same** sun and load in the twin. That fixes the "not a controlled experiment" problem.

## 10. Diagram
- Repo: `docs/diagrams/framework.png` (+ `.svg`, `.excalidraw`)
- Web: https://claude.ai/artifact/ENAndsWgSqt9YYqYxMuY9W (private claude.ai page; use Share to give teammates access)

## 11. Top risks
1. **Bad forecasts drive bad plans.** Fix: replan every 15 min, event calls on forecast error, rule fallback.
2. **Twin ≠ real house.** Learned parts may overfit. Fix: validate the twin on logged data first, use shadow mode and held-out days.
3. **One bug hits every site.** The optimiser is shared code. Fix: tests, staged rollout, rule floor.
4. **Learning drifts** (bad memories, weight drift). Fix: regret-based pruning, bounded weights, human review of prompt changes.
5. **The LLM adds little.** Fix: measure it honestly against "no LLM" and keep the LLM where it adds value (events, explanations, human chat).

## 12. Questions for Sense Reply
- Can you log each agent's proposal, scores and the orchestrator's pick? (This unlocks all agent KPIs.)
- Where is the site, and why does PV peak at 10:00 and run 14 h in January?
- How accurate is the digital twin against real data?
- Is sustainability a weight or a hard rule for the client?
- What is your target fleet size? (This decides API vs self-hosting.)
- Which inputs does the sustainability agent get today?
- Do the agents receive any load, PV or CO2 forecast today?
- Can we get 3–6 months of 15-min site data (more sites = better), plus weather and any cleaning/maintenance log?
- Is `pv_dirt` a real sensor or only a simulator value? Its 2.4%/day with no cleaning is 10–30× faster than field data.
- What would a client pay per site for health alerts or forecasts?
