# KPI pack: how good are the agents?

For: team consolidation session. Simple words. Numbers come from `python3 analysis/kpis.py`.

## Read this first (big warnings)
- **Two runs, not a fair test.** Same week (5–12 Jan 2026) and same prices, but different sun.
  - PV: A = 93.1 kWh, B = 69.1 kWh. Likely cause: panels are dirtier in B (`pv_dirt` 0.20 vs 0.42 at the end of the week).
  - Start battery: A = 0.57, B = 0.15.
  - So **never compare raw € between A and B.** Compare each run against its own baseline (same sun, same load).
- **A** = Orchestrator + Cost agent (`dataset-001.json`). **B** = Orchestrator + Cost + Sustainability agent (`dataset-002.json`).
- **Site assumed Italy.** The data does not say where it is.
- **Carbon:** no CO2 field in the data. We use one static factor for now: **198.9 gCO2/kWh** (ISPRA 2024 preliminary, consumption factor, Rapporti 413/2025 Tab. 1.3). A static factor cannot reward charging at "clean" hours. The upgrade is the hourly ENTSO-E series (steps at the end).
- **Clock looks odd.** PV runs about 03:00–17:00 and peaks at 10:00. Real Italian January has about 9 h of sun, peaking near 12:00. The simulator clock or location may not be real Italy. Ask Sense Reply.
- **LLM price** uses Devstral 2 at $0.40 in / $2.00 out per M tokens, aggregator figure, FX 0.86 €/$. Devstral 2 was retired on 2026-07-31 (see `research/05`).
- One week, one site, one run each. Call it **pilot evidence**, not proof.

## Words and symbols
- Δt = 0.25 h (one 15-min step). N = number of steps (672 in A, 671 in B).
- E_imp, E_exp = grid import/export energy per step (kWh). Fields: `energyImportInterval`, `energyExportInterval`.
- π_buy, π_sell = grid prices €/kWh. Fields: `buyPrice`, `sellPrice`.
- E_pv = Σ panels `pv_energy_interval`. E_load = `load` × Δt.
- E_chg, E_dis = battery charge/discharge energy per step. Fields: `energyChargedInterval`, `energyDischargedInterval`.
- SoC = `soc`. Cap = `capacityKwh` (10). η = `dischargeEfficiency` (0.95). P = BESS `power` (kW; + charge, − discharge).
- CI_t = grid carbon intensity (g/kWh), from an external source.
- **Rule baseline** = simple controller on the same sun and load: charge on PV surplus, discharge when the house needs power, within live power and SoC limits. No AI.
- **No-battery baseline** = same house, battery off: import = max(load − PV, 0).
- Tag **now** = we can compute it today. Tag **logs** = needs the agent proposal logs, which are not in the JSON. Ask Sense Reply for them.

---

## 1. Cost agent
Today we only see the final battery value, not the cost agent's own proposal. So the cost agent is judged by config A, and in B we can only see the mix.

| KPI | What it measure | Formula | Why | A | B | Tag |
|---|---|---|---|---|---|---|
| C1 Energy bill, SoC-adjusted | What the house paid for grid energy this week, fair for battery level. | C = Σ(E_imp·π_buy − E_exp·π_sell) − (SoC_end − SoC_start)·Cap·η·mean(π_buy) | The raw bill lies if the battery ends fuller or emptier, so we correct for leftover energy. | €3.01 (raw €3.23) | €4.86 (raw €5.15) | now |
| C2 Savings vs no battery | How much cheaper than no battery at all. | (C_nobat − C) / C_nobat | Basic "does battery + agent help?" | 18.2% | 13.0% | now |
| **C3 Savings vs rule baseline** | Does the AI beat a dumb rule? | (C_rule − C) / C_rule | **Main money KPI.** If the AI cannot beat a free rule, the AI cost is not worth it. | **−18.6%** | **−5.5%** | now |
| C4 Price-timing spread | Does it discharge when power is expensive and charge when it is cheap? | Σ(E_dis·π_buy)/ΣE_dis − Σ(E_chg·π_buy)/ΣE_chg | Checks that the cost agent uses price signals. Bigger is better. | €0.012/kWh | €0.011/kWh | now |
| C5 Expensive import share | How much grid energy was bought at above-median price. | Σ E_imp[π_buy > median] / Σ E_imp | Low is good. Shows whether the agent avoids peak prices. | 81% | 82% | now |
| C6 Oracle capture | How close to the best possible plan (perfect foresight). | (C_nobat − C) / (C_nobat − C_oracle) | Tells how much money is left on the table. Literature LLMs get 97–98%. | – | – | needs LP (scipy) |
| C7 Cost agent win-rate | How often the cost agent's proposal was the best, scored by a simulator. | (1/T) Σ 1[J(a_cost) ≤ J(a_other)] | Says if the cost agent is actually good at its job. | – | – | logs |

**Why C3 is negative (seen in the data):** the agents hold energy for the 18–21h evening peak. Mean SoC is 0.47 (A) and 0.36 (B), and A ends the week 80% full. So they export PV at €0.09 instead of storing it, then buy at night. The simple rule imports 34 kWh (A) where the agent imports 64 kWh.

## 2. Sustainability agent
Only in B. It has no carbon signal in the data, so it probably chases a proxy (more self-use of PV). Same limit as above: we only see the mixed result.

| KPI | What it measure | Formula | Why | A | B | Tag |
|---|---|---|---|---|---|---|
| S1 Grid CO2 | How much CO2 the grid energy caused. | Σ E_imp,t · CI_t / 1000 (kg) | Main green KPI. Exports not credited (conservative). | 12.7 kg | 12.0 kg | now (static CI) |
| S2a CO2 avoided vs no battery | CO2 saved versus battery off. | S1_nobat − S1 | Shows the green value of the battery plus agent. | 4.1 kg | 4.7 kg | now (static CI) |
| **S2b CO2 avoided vs rule** | CO2 saved versus the dumb rule. | S1_rule − S1 | **Main green KPI.** Negative means the rule is greener. | **−5.9 kg** | **−3.3 kg** | now (static CI) |
| S3 Import carbon intensity | How dirty the bought power was, on average. | 1000·S1 / Σ E_imp (g/kWh) | Only means something with hourly CI. Lower than the grid average means it buys at clean hours. | 198.9 | 198.9 | needs ENTSO-E |
| S4 Self-consumption | Share of own PV used at home (directly or via battery). | (ΣE_pv − ΣE_exp) / ΣE_pv | Classic green KPI (Luthander 2015). Probably what the sustainability agent optimises. | 51.6% | 74.6% | now |
| S5 Self-sufficiency | Share of house need covered without the grid. | 1 − ΣE_imp / ΣE_load | Independence from the grid. | 39.3% | 42.0% | now |
| S6 Green charging share | Share of battery charge that came from PV surplus. | Σ min(E_chg, max(E_pv − E_load, 0)) / ΣE_chg | Battery filled by sun = green. Filled by grid = not. | 82.6% | 84.8% | now |
| S7 Sustainability agent win-rate | How often its proposal was picked and was best on CO2. | (1/T) Σ 1[a_t = a_sust] | Tells if the agent changes anything at all. | – | – | logs |
| S8 Value of second agent | Extra KPI gain per extra € of LLM. | ΔKPI(B vs A, baseline-relative) / ΔLLM€ | Is the second agent worth its tokens? | – | see T2 | now (rough) |

Note: S4 jumps a lot in B, but part of that is less sun (less surplus to export), not the agent.

## 3. Orchestrator
Its outputs (which proposal won, the scores) are not logged. Its cost is visible, though.

| KPI | What it measure | Formula | Why | A | B | Tag |
|---|---|---|---|---|---|---|
| O1 LLM calls per decision | How many model calls one 15-min decision needs. | requests / N | More calls = more cost, delay and failure points. | 4.39 | 8.15 | now |
| O2 Input tokens per decision | How much text is sent per decision. | tokens_in / N | Main cost driver. Shows prompt bloat. | 17.4k | 29.9k | now |
| O3 Decision latency (upper bound) | How long one decision takes. | mean LLM ms × calls / N | Must fit well inside 15 min. It also matters for fast events. | 10.3 s | 20.3 s | now |
| O4 LLM cost per decision | Money per decision. | (tok_in·p_in + tok_out·p_out) / N | Unit economics. | €0.0071 | €0.0123 | now |
| O5 LLM cost per week | Money per site per week. | tok_in·p_in + tok_out·p_out | Compare with the energy bill (€3–5/week!). | €4.74 | €8.22 | now |
| O6 Selection share | How often each agent's proposal gets picked. | (1/T) Σ 1[a_t = a_i] | If one agent always wins, the other is dead weight. | – | – | logs |
| O7 Agreement rate | How often the agents propose almost the same kW. | (1/T) Σ 1[abs(a_cost − a_sust) ≤ ε] | High agreement means the second agent adds little. | – | – | logs |
| O8 Orchestrator regret | How much worse the pick was than the best proposal. | (1/T) Σ [J(a_t) − min_i J(a_i)], J = simulator cost | Says if the orchestrator chooses well. | – | – | logs |
| O9 Self-score calibration | Do the agents' own scores match reality? | Spearman ρ(self-score, simulator score) | Agents grade their own homework; LLMs favour their own output. Low ρ = arbitration is random. | – | – | logs |
| O10 Judge robustness | Does the pick change if you swap proposal order? | share of picks unchanged after order swap | Catches position bias in the LLM judge. | – | – | logs (test) |

## 4. Whole framework

| KPI | What it measure | Formula | Why | A | B | Tag |
|---|---|---|---|---|---|---|
| **F1 Net value vs rule** | Money gained versus the free rule, after paying for the AI. | (C_rule − C) − LLM€_week | **The one number for the boss.** Negative = the AI loses money. | **−€5.21/wk** | **−€8.48/wk** | now |
| F2 AI cost vs savings | LLM cost divided by savings versus no battery. | LLM€ / (C_nobat − C) | Above 1 = the AI costs more than it saves. | 7.1× | 11.4× | now |
| T1 Abatement cost | € paid per kg of CO2 saved, B vs A. | (ΔC_B − ΔC_A) / (ΔCO2_A − ΔCO2_B), Δ = vs own rule baseline | Standard climate-economics measure. | – | n/a: B is cheaper **and** greener on energy | now |
| T2 Total cost of sustainability | Extra € per week for adding the sustainability agent. | (ΔC_B − ΔC_A) + (Deg_B − Deg_A) + (LLM_B − LLM_A) | Puts energy, wear and AI cost in one number. | – | **€3.39/wk** (energy −0.22, wear +0.12, LLM +3.48) | now |
| B1 Round-trip efficiency | Energy out of the battery versus energy in. | (ΣE_dis + ΔSoC·Cap·η) / ΣE_chg | Nominal value is 0.90. Lower means waste. | 0.90 | 0.89 | now |
| B2 Equivalent full cycles | How hard the battery works. | (ΣE_chg + ΣE_dis) / (2·Cap) | Cycles = battery ageing. | 4.3 | 4.5 | now |
| B3 Degradation cost | Battery wear in €. | c_deg · ΣE_dis, with c_deg = €0.10/kWh (assumed, range 0.06–0.15) | Wear is a real cost. Here it is as big as the bill, so the c_deg value matters a lot. | €3.96 | €4.08 | now (assumed c_deg) |
| B4 Time at SoC limit | Share of time the battery sits at empty or full. | share of t with SoC ≤ 0.11 or ≥ 0.89 | Sitting at the limits stresses the cells and leaves no headroom. | 0% | 4.5% | now |
| B5 Health | SoH loss and maximum temperature. | SoH_start − SoH_end; max `temperature` | Safety and ageing. | 0.023% / 24 °C | 0.024% / 19 °C | now |
| G1 Peak import | Biggest grid draw. | max grid `power` | Peaks cost grid capacity. | 4.95 kW | 3.93 kW | now |
| G2 Violations / penalty | Broken grid rules. | Σ `violation`; Σ `penalty` | Must be 0. | 0 / €0 | 0 / €0 | now |
| F3 Mode switches per day | How often it flips between charge and discharge. | count of sign changes of P (idle skipped) / days | Calm control = less wear. 2/day = one cycle per day. | 2.0 | 2.0 | now |
| F4 Smoothness | Average power jump between steps. | mean abs(P_t − P_t−1) | Jumpy control = wear and noise. | 0.15 kW | 0.11 kW | now |
| F5 Fallback rate / uptime | Share of steps decided by fallback (no cloud). | steps_fallback / N | Resilience when the internet drops. | – | – | logs |

**Data check:** the energy balance (import − export = load − PV + charge − discharge) closes to within 0.05 kWh (A) and 0.35 kWh (B) over the week. The B gap is likely the missing sample.

---

## What the numbers say (5 lines)
1. **Both AI setups lose to a free rule.** A is 18.6% dearer than the rule and B is 5.5% dearer. Cause: they hoard battery energy for the evening and export sun cheaply.
2. **The AI costs more than it saves.** LLM €4.7–8.2 per week, versus only about €0.7 per week of savings vs no battery (A €0.67, B €0.72).
3. **Adding the sustainability agent is not bad for energy.** Against its own rule baseline, B is €0.22 cheaper and 2.6 kg CO2 cleaner than A. Its only real price is the extra LLM spend: +€3.5 per week, from 8.2 vs 4.4 calls per decision.
4. **Agent-level and orchestrator-level quality cannot be judged yet.** The proposals and scores are not logged. That is the first fix to ask for.
5. With a static CO2 factor, "green" = "import less". Hourly CI is needed to reward clean timing.

## Upgrade: hourly carbon from ENTSO-E (you do this by hand)
1. Go to transparency.entsoe.eu and log in (free account, no API token needed for the CSV export).
2. Generation → **Actual Generation per Production Type**.
3. Area: **Italy** (country / bidding zone IT). Dates: **05.01.2026 – 13.01.2026**. Time zone: **CET**.
4. Export → **CSV**. Save as `data/external/entsoe_IT_gen_2026-01.csv`.
5. Run `python3 analysis/kpis.py`. It picks up the file automatically:
   - CI_t = Σ_k gen_k,t·EF_k / Σ_k gen_k,t
   - EF_k = IPCC AR5 lifecycle medians: gas 490, coal 820, hydro 24, solar 48, wind 11 g/kWh. Oil 650 and other 700 are assumed.
   - Imports are ignored.

To unlock the "logs" KPIs, ask Sense Reply for:
- per decision: each agent's proposed kW and self-scores, the orchestrator's pick, and the prompt version
- per call: token counts
