# KPI pack and dashboard: how good are the agents?

Written in simple words. The numbers come from `python3 analysis/kpis.py` (weekly) and `python3 analysis/timeseries.py` (per day and per hour). Data: `data/DatasetV4/`.

## Read this first
- **Three runs, one week (5–12 Jan 2026), same prices, same weather:**
  - **A** = Orchestrator + Cost agent (`dataset-001.json`).
  - **B** = Orchestrator + Cost + Sustainability (`dataset-002.json`). Its panels start much dirtier (`pv_dirt` 0.26 vs 0.03), so PV is 69 vs 93 kWh.
  - **C** = same agents as B (`dataset-003.json`), but **same dirt as A**. PV is 93.06 vs 93.13 kWh and load 104.5 vs 105.1 kWh. **C vs A is the main comparison.**
- **C vs A is still not a perfect A/B test.** The battery starts at a different level: A goes 0.57 → 0.80, C goes 0.80 → 0.70.
  - About €0.25 of the €0.34 raw bill gap is only this SoC swing.
  - So we always compare the **SoC-adjusted** bill, and each run against **its own rule baseline** (same sun, same load).
- **Site assumed Italy.** The data does not say where it is.
  - The brief says "industrial site", but `DATA_MODEL.pdf` says residential building. We follow the data.
  - The PV clock looks odd: it peaks at 10:00 and runs ~14 h in January.
- **Carbon:** there is no CO2 field. We use the hourly ENTSO-E generation mix for Italy × IPCC lifecycle factors: 214–439 g/kWh, mean 356 over the samples.
  - This is an **estimate under the Italy assumption**, not a measured site value.
  - Without an API token, `carbon.py` falls back to static ISPRA 198.9 g/kWh, so the CO2 numbers change.
- **Battery wear now comes from the client's asset file**, not our guess.
  - `Assets/BSS.json`: replacement €100/kWh, degradation 0.005% per equivalent full cycle.
  - The telemetry agrees: SoH falls 5.0e-5 per cycle in all 3 runs.
  - That means **€0.005 per kWh discharged**, 20× less than the €0.10 we assumed before. Wear is about €0.2 a week and changes no conclusion.
- **LLM price:** Devstral 2 at $0.40 in / $2.00 out per M tokens, FX 0.86. Token counts come from `DataIndex.xlsx`.
- One week, one site, one run per setup: this is **pilot evidence**, not proof.

## Words and symbols
- Δt = 0.25 h. E_imp and E_exp = `energyImportInterval` and `energyExportInterval`. π_buy and π_sell = `buyPrice` and `sellPrice`.
- E_pv = Σ panels `pv_energy_interval`. E_load = `load` × Δt. E_chg and E_dis = `energyChargedInterval` and `energyDischargedInterval`.
- Cap = `capacityKwh` (10). η = `dischargeEfficiency` (0.95). CI_t = grid carbon intensity (g/kWh, ENTSO-E).
- **Rule baseline** = charge on PV surplus, discharge when the house needs power, within live limits. No AI.
- **No-battery baseline:** import = max(load − PV, 0).
- "logs" = needs each agent's proposal and score per decision, which are not in the data.

---

## 1. Dashboard: the main numbers

| KPI | Formula | A | B | C |
|---|---|---|---|---|
| **Energy bill, raw** | Σ(E_imp·π_buy − E_exp·π_sell) | €3.23 | €5.15 | €2.89 |
| **Energy bill, SoC-adjusted (C1)** | raw − (SoC_end − SoC_start)·Cap·η·mean(π_buy) | €3.01 | €4.86 | €2.98 |
| Rule baseline bill (same sun/load) | same formula, rule dispatch | €2.32 | €4.46 | €2.30 |
| **C2 Savings vs no battery** | (C_nobat − C)/C_nobat | 18.2% (€0.67) | 13.0% (€0.72) | 18.2% (€0.66) |
| **C3 Savings vs rule** | (C_rule − C)/C_rule | −30% (−€0.70) | −9% (−€0.40) | −30% (−€0.68) |
| C3w Same, wear included | (C_rule + c_deg·E_dis,rule) − (C + c_deg·E_dis) | −€0.63 | −€0.40 | −€0.64 |
| Grid import | ΣE_imp | 63.8 kWh | 60.5 kWh | 58.7 kWh |
| Grid export | ΣE_exp | 45.1 kWh | 17.6 kWh | 42.9 kWh |
| **S4 Self-consumption** | (ΣE_pv − ΣE_exp)/ΣE_pv | 51.6% | 74.6% | 53.9% |
| S5 Self-sufficiency | 1 − ΣE_imp/ΣE_load | 39.3% | 42.0% | 43.8% |
| **S1 Grid CO2** | ΣE_imp·CI_t/1000 | 23.8 kg | 22.5 kg | 21.8 kg |
| S2b CO2 vs rule | S1_rule − S1 | −12.2 kg | −6.7 kg | −10.4 kg |
| S3 Import carbon intensity | 1000·S1/ΣE_imp (grid mean 356) | 373 | 373 | 372 |
| **G2 Grid penalty exposure** | Σ`violation`, Σ`penalty` | 0 / €0 | 0 / €0 | 0 / €0 |
| G1 Peak import (single max) | max grid `power` | 4.95 kW | 3.93 kW | 2.83 kW |
| G6 P99 import | 99th percentile of grid `power` | 3.12 kW | 2.95 kW | 2.52 kW |
| **B1 Apparent storage efficiency** | (ΣE_dis + ΔSoC·Cap·η)/ΣE_chg (device 0.95² = 0.90) | 0.90 | 0.89 | 0.90 |
| B2 Equivalent full cycles | (ΣE_chg + ΣE_dis)/(2·Cap) | 4.3 | 4.5 | 4.7 |
| B3 Wear cost | c_deg·ΣE_dis, c_deg €0.005/kWh (BSS.json) | €0.20 | €0.20 | €0.23 |
| **B6 Time near target SoC 0.8** | share of t with abs(SoC − 0.8) < 0.03 | 32% | 14% | 31% |
| O1 LLM calls per decision | requests/N | 4.4 | 8.2 | 7.6 |
| O3 Decision latency (upper bound) | mean ms × calls/N | 10 s | 20 s | 18 s |
| **O5 LLM cost per week** | tok_in·p_in + tok_out·p_out | €4.74 | €8.22 | €7.71 |
| **F1 Net value vs rule** | (C_rule − C) − LLM€ | −€5.44 | −€8.62 | −€8.39 |
| **F2 AI cost / savings vs no battery** | LLM€/(C_nobat − C) | 7.1× | 11.4× | 11.7× |
| F3 Mode switches per day | sign changes of P / days | 2.0 | 2.0 | 2.0 |
| F4 Smoothness | mean abs(P_t − P_t−1) | 0.15 kW | 0.11 kW | 0.12 kW |

**Notes on these numbers:**
- **B1 note:** this is not true round-trip efficiency. It only checks that the weekly flows match the device's 0.95 × 0.95. Our teammate is right about this.
- **Data check:** the energy balance closes within 0.05 (A), 0.35 (B) and 0.62 (C) kWh over the week, under 0.6% of load. `load` is a spot kW × 0.25 h, not a true interval energy.

## 2. Trade-off matrix

**C vs A. Each run is measured against its own rule baseline, which removes the sun and load differences.**

| | Energy € | CO2 | Grid import | LLM € | **Total** |
|---|---|---|---|---|---|
| Adding the Sustainability agent (C − A) | −€0.02/wk (no change) | **−1.5 kg/wk** (−6% of A's grid CO2) | −3.8 kWh | **+€2.97/wk** | **+€2.98/wk** |

Every column in this row is SoC-adjusted, and each run is measured against its own rule baseline.

- **Abatement cost incl. LLM: ≈ €2,000 per tonne of CO2.** The EU ETS carbon price is under €100/t.
- The B − A comparison is less clean (dirt differs). It gives −€0.30, −5.0 kg and +€3.19/wk total (€640/t).
- **Reading:** the second agent does not cost energy money, as Sense Reply expected it might. It saves a little CO2 because it imports less. But its LLM bill makes that CO2 about 20–25× dearer than the EU carbon price.

**All options side by side (per week, A's sun and load):**

| Option | Energy € (SoC-adj) | Grid CO2 | Import | Wear | LLM € | Latency/decision | Status |
|---|---|---|---|---|---|---|---|
| A: Cost agent | 3.01 | 23.8 kg | 63.8 kWh | 0.20 | 4.74 | ~10 s | measured |
| C: Cost + Sust. agents | 2.98 | 21.8 kg | 58.7 kWh | 0.23 | 7.71 | ~18 s | measured |
| Rule baseline (no AI) | 2.32 | 11.5 kg | 30.9 kWh | 0.27 | 0 | < 1 ms | replayed on same data |
| Rule + 20% reserve knob | 2.44 | 13.7 kg | 36.5 kWh | ~0.25 | 0 | < 1 ms | replayed (`replay.py`) |
| Rule + night grid charge to 30% | 2.45 | 16.2 kg | 43.7 kWh | ~0.3 | 0 | < 1 ms | replayed |
| Proposal (1 agent, daily knobs, rule executes) | target ≤ rule; enforced by replay gate | target ≤ rule | target ≤ rule | ~0.27 | ~€0.01–0.05 | < 1 ms (LLM off the control path) | **knob values replayed; LLM choice not yet tested** |

CO2 and import in the table above are SoC-adjusted (A's measured run: 23.0 kg, 61.7 kWh).

**Replay lesson (`analysis/replay.py`):** this January week, every knob that holds energy back loses to the plain rule. A 20% reserve costs +€0.12/wk; a night grid charge costs +€0.13–0.22/wk and adds 5–10 kg CO2, because grid energy pushes out free morning PV. A wrongly set knob loses money, so the replay gate is essential, and in this week the best plan is "no reserve, no grid charge".

**By day type:** agent minus its own rule, summed over 3 full days each (`timeseries.py`).

| Day type | Run | Excess € | Excess CO2 | Excess import |
|---|---|---|---|---|
| Sunnier (PV ≥ 13.8 kWh/day) | A | +0.33 | +5.8 kg | +14.8 kWh |
| | C | +0.31 | +4.7 kg | +12.0 kWh |
| Duller | A | +0.23 | +4.5 kg | +13.4 kWh |
| | C | +0.23 | +4.0 kg | +12.1 kWh |

- **Small spread:** the week is uniform (12.5–14.1 kWh PV per full day), so the day-type split shows little.
- **Direction:** the agents lose most to the rule on sunnier days. On those days there is more surplus to store, and they export it instead.
- **Next step:** a summer week is needed to test "different generation conditions" properly.

## 3. KPIs that need logs (cannot be computed from the JSON)

| KPI | Formula | Why |
|---|---|---|
| Agent win-rate | share of decisions where an agent's proposal was picked | Is the second agent dead weight? |
| Agreement rate | share with abs(kW_cost − kW_sust) ≤ ε | High = the second agent adds little |
| Orchestrator regret | J(picked) − min_i J(proposal_i), J = simulated cost | Does the orchestrator choose well? |
| Self-score calibration | Spearman ρ(self-score, simulated score) | Agents grade their own homework |

## 4. Reconciliation with the teammate's "Method & Context"
Same frame as theirs: what the source says, what the telemetry proves, and what needs an experiment.

| Topic | Source says | Telemetry proves | Our handling |
|---|---|---|---|
| Site type | Brief: industrial | DATA_MODEL: residential | Follow the data; flag it |
| A/B validity | "Two configurations" | B differs in dirt and SoC; C differs only in SoC | C vs A, SoC-adjusted, each vs own rule |
| `cost` field | "Cumulative" | Per-sample: equals power × price / 60 exactly (checked, max diff ~1e-18) | Recompute the bill from energy × price (agree) |
| Telemetry scope | Brief lists voltage, current, temperature | Only BESS temperature; no voltage or current fields | KPIs use power/energy only |
| Carbon | Sust. agent "avoids emissions" | No CO2 field; Sust. prompt has no CO2 or price input | ENTSO-E hourly estimate, labelled Italy assumption. "No verified CO2" holds for the site itself |
| Efficiency | Device 95% / 95% | Weekly ratio ≈ 0.90 | Renamed B1 "apparent storage efficiency" (agree) |
| Self-consumption | – | Export can be battery discharge (A: 10.5 kWh exported while discharging) | S4 is an upper bound on true PV self-use |
| Missing sample | – | B lacks 2026-01-09 20:00 | Cumulative-diff recovery possible; we leave B at 671 samples (B is secondary) |
| Agent motives | Agents discuss and self-score | No decision logs | Behaviour inferred from prompts + telemetry only |
| Resilience | – | 0 violations, 0 outages, 0 throttling | Needs stress tests; not comparable here |

## 5. What the numbers say
1. **The AI costs 7–12× what the battery saves** (€4.7–7.7 LLM vs ~€0.7/wk saved vs no battery). This is the most robust finding.
2. **A free rule beats all three runs on energy** by €0.40–0.70/wk, now also with wear counted, since wear is small.
   - **Cause:** the battery fills to the 80% target by 11:00 and sits there. Midday sun is then exported at €0.09.
   - The battery empties fast at 18–19h and partly exports while doing so. It then stops at ~20% SoC while the house imports at 20–21h.
3. **The second agent changes almost nothing.** C vs A on the same panels: same € (−€0.02), 1.8 kg less CO2, +€3/wk LLM.
   - (SoC-adjusted: −1.5 kg, −3.8 kWh.) Its prompt gets no price and no CO2, so it can only push "import less". Imports are still at hours 5% dirtier than average (S3).
4. **No grid penalties in any run.** C's peak import is lower (2.8 vs 5.0 kW), but A's peak is one sample. At P99 the gap is small (2.5 vs 3.1 kW).
5. **Agent and orchestrator quality cannot be judged** without the proposal logs.

## Carbon data: how to repeat it
1. Get a free ENTSO-E Transparency API token and put it in `.env` as `ENTSO_API=<token>` (gitignored).
2. Run `python3 analysis/kpis.py`. `carbon.py` pulls A75 actual generation for Italy (`10YIT-GRTN-----B`), converts UTC to Europe/Rome, and computes CI_t = Σ gen·EF / Σ gen with IPCC AR5 lifecycle factors. It stops if coverage is under 90%.
3. `python3 analysis/forecast_check.py` adds the day-ahead CO2 forecast test (skill FC2 = 0.40 vs "same as yesterday").
