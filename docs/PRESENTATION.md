# Pitch deck: ghost deck (7 minutes, demo included)

Speakers: Sydney (slides 0–4), Amir (5–6, platform, pipeline + demo), Francesco (7–8). Script: `docs/SCRIPT.md`. Deck: `docs/deck/deck.html`, rendered by `docs/deck/render.sh`.

**Three scenarios only:** Pilot A (cost), Pilot C (cost + sustainability), New framework (self-hosted single agent, Ministral 3 8B). The free static rule is the yardstick, not a scenario.

**Numbers** follow `docs/REPORT.md` and `data/ours_ministral.json`:
- the new framework is modelled on run C's sun, load and prices, with start SoC 0.80 and λ = €0.10/kg;
- carbon uses a constant 0.356 kg/kWh, and the site is assumed to be in Italy;
- pilot AI cost uses the Devstral 2 list price at 0.86 €/$;
- the framework's AI cost is Ministral 3 8B on a €4k node at 1,000 sites, ops included (`analysis/model_cost.py`).

## Title-only read
0. One carbon-aware agent, on a model Reply owns.
1. One self-hosted agent that plans once a day turns pilot C's €7.31 weekly loss into a €0.98 gain and cuts the AI bill by 98%.
2. We judge every agent against a free rule, because "saved vs no battery" alone makes the pilots look profitable.
3. Both pilots lose to a free rule with an AI bill 8 to 12 times their saving; one daily agent's bill is an eighth of what it saves.
4. A second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price, while a carbon weight inside one agent costs about nothing.
5. We change two things on Reply's platform: a self-hosted Ministral 3 8B replaces the retired LLM, and the LLM leaves the 15-minute loop.
6. The agent writes three numbers a day; a validator, a rule and a clamp decide what the battery actually does. (Then the live demo.)
7. Self-hosting beats the free rule from about 1,500 sites; an on-site model is a paid option for offline sites, not a saving.
8. One modelled winter week supports a staged rollout, gated on a summer replay before any promise to a client.

The argument runs in five steps:
- the answer, then the yardstick;
- the pilots fail it, and the second agent buys carbon at a high price;
- the redesign on Reply's own platform, then the demo;
- the fleet economics and the upsell (the KPI scores live in the demo's KPI tab);
- the limits and the rollout.

## Timing and speakers

| # | Time | Speaker | Running total |
|---|---|---|---|
| 0–4 | 0:10 + 0:30 + 0:50 + 0:45 + 0:35 | Sydney | 2:50 |
| 5–6 | 0:45 + 1:30 | Amir | 5:05 |
| 7–8 | 0:55 + 0:30 | Francesco | 6:30 |

**Demo.** It replays the committed Ministral 3 8B plans; nothing runs live. Keep a 60 s screen recording as a backup.

## Slides

### 0. Title (0:10)
"One carbon-aware agent, on a model Reply owns", with the names. No exhibit.

### 1. Answer (0:30)
Three before → after figures, pilot C → New framework:
- N1: −€7.31 → +€0.98/wk;
- AI cost: €7.71 → €0.18/wk;
- grid CO2: 21.3 → 12.2 kg/wk.

Source: report §1.

### 2. KPIs (0:50)
**Left panel: the free rule, our yardstick.**
- Two lines: if the sun makes more than the house uses, charge; if the house uses more, discharge. No AI, no forecast, no cost.
- It saves €1.03 a week on the pilot week. Any AI must beat it, or Reply should ship the rule.

**Right: the 20 KPIs in five category columns.** Each card shows a plain question, its code and the pass line. A blue edge marks the four KPIs compared with the rule: S net, VORB, F1, S2b.

The thresholds come from `data/Sense_Reply_B2_KPI_Conformity.xlsx`. No results appear here; the verdicts per scenario are in the demo's KPI tab.

### 3. The two pilots (0:45)
**Bars.** Saving vs no battery against AI bill, per pilot:

| Pilot | Saving | AI bill | Ratio |
|---|---|---|---|
| A | €0.60 | €4.74 | 7.8× |
| C | €0.63 | €7.71 | 12.2× |

| New framework | €1.42 | €0.18 | 0.12× |

The new framework's pair, in blue, sits under the pilots: it previews the answer from slide 1.

**Three causes, from the prompts:**
- a fixed 80% target;
- export valued at zero;
- a blind second agent.

Source: report §4 step 9, §5.

### 4. Cost vs sustainability (0:35)
**Scatter.** x = grid CO2, y = N1.

| Point | CO2 (kg/wk) | N1 (€/wk) |
|---|---|---|
| A | 21.9 | −4.33 |
| C | 21.3 | −7.31 |
| Free rule (hollow) | 11.9 | +1.03 |
| New framework | 12.2 | +0.98 |

An arrow runs from A to C: "+€2.97 AI cost, −0.7 kg".

**Stats:**
- €4,300/t for the second agent;
- €90/t EU ETS;
- ≈ €0/t for a carbon weight (MAC −€0.011/kg, within the gate's noise).

Source: report §7.2.

### 5. Platform (0:45)
Reply's "Agentic Operations for E&U" platform, redrawn in deck style. Blue marks our change; a dashed outline marks the paid option; red marks what we removed.
- **Edge:** a rule and a clamp every 15 min, with fallback to yesterday's plan, then the static rule.
- **Central:** Ministral 3 8B self-hosted, a validator with a replay gate, and the Data Lake as memory.
- **Paid option:** Ministral 3 3B on the gateway.
- **Removed:** the external LLM (Devstral 2, retired 31 Jul 2026).

Source: report §3.1, `docs/diagrams/reply-platform.html`.

### 6. Pipeline, then the demo (0:30 + 1:00)
**Slide.** The original left-to-right pipeline, using the demo's stage names. Each stage has a one-phrase role:
- **Inputs:** what the agent knows (prices, hourly CO2, similar past days);
- **Agent:** Ministral 3 8B, once a day, writes 3 knobs and a reason;
- **Validator:** checks the plan and replays it on yesterday before it may run;
- **Rule:** turns the knobs into kW every 15 minutes;
- **Clamp:** safety limits that always have the last word;
- **Site.**

Under the boxes:
- the memory loop;
- the fallback chain: agent plan → previous valid plan → static rule;
- one line of next inputs, not built yet;
- the strip of three changes: calls ~730 → 1, export €0 → sell price, 80% target → evening load.

Amir explains the validator and the rule aloud; details are in `demo/agent.py` and `demo/sim.py`.

**Demo click path,** from this slide to the site:
1. Mon 11:00: knobs and reason. (0:15)
2. Similar past days and the memory arc. (0:15)
3. Tue: the gate blocks the plan and the previous valid plan runs. (0:15)
4. KPIs tab: 15 of 20 KPIs Good, against 5 and 6 for the pilots. (0:15)

### 7. Business case (0:55)
**Chart.** Log-log: AI cost per site per week against fleet size, 100–10,000 sites. Points come from `model_cost.OPTIONS`.
- **Lines:**
  - pilots A and C, flat at €4.74 and €7.71, because they pay per token and scale never lowers the bill;
  - on-prem 8B and the same model on an EU API, both falling with fleet size;
  - the on-site 3B box, flat from €1.86/wk.
- **Thresholds:**
  - S_net €1.16: above it, AI eats the whole saving;
  - VORB €0.12: below it, the agent beats the free rule after AI.
- **Crossings:** the EU API from ~580 sites; on-prem from ~1,500.

**Right panel: where ~1,500 comes from** (model_cost.py `central()`, 1,000–25,000 sites):

| Step | Value |
|---|---|
| Servers, power and people per year: 2 GPU nodes × (€4,000 / 5 yr + 100 W × 8,760 h × €0.32) + 0.1 FTE ops €7,000 | €9,160 |
| AI cost per site per week: €9,160 ÷ 52 ÷ sites | €176 ÷ sites |
| Our lead over the free rule before AI cost (VORB) | €0.12 |
| AI cost falls below the lead when | sites > 1,480 |

The EU API reaches the same point at ~580 sites.

**Upsell.** Every site already runs on without internet: rule, clamp and yesterday's plan. The 3B box adds daily replanning offline and keeps data on site. Price it at or above its cost of €97–422 per site per year.

Source: report §8.

### 8. Limits and rollout (0:30)
**Limits:**
- one modelled winter week, with PV that is not real weather;
- no CO2 field and no logs of agent proposals;
- the runs start with different panel dirt: A 3%, B 26%, so B makes 26% less solar (69.1 vs 93.1 kWh) and is left out; C has A's dirt;
- the self-hosting cost is an estimate (€4k node, 0.1 FTE).

**Rollout,** report §9 phases 0–4:
- fix the baseline;
- prove decision value on other seasons;
- carbon desk;
- pilot sites on an EU API;
- in-house at ~1,000 sites.

### Appendix (Q&A only)
- **A1.** Trade-off matrix, three scenarios (report §7.1).
- **A2.** KPI formulas (report §4).
- **A3.** CO2 method (report §4 step 7).
- **A4.** Data corrections (report §10).
- **A5.** Ministral bench (report §3.3):
  - 8B: 21/21 valid JSON, ~27 s per call on an 8 GB laptop;
  - 3B: 14/14 valid JSON, 12–14 s per call.
