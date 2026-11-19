# Pitch deck: ghost deck (7 minutes, demo included)

Speakers: Sydney (slides 0–4), Amir (5–6, platform + demo), Francesco (7–9). Script: `docs/SCRIPT.md`. Deck: `docs/deck/deck.html`, rendered by `docs/deck/render.sh`.

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
3. Both pilots lose to a free rule, and their AI bill is 8 to 12 times what the battery saves.
4. A second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price, while a carbon weight inside one agent costs about nothing.
5. We keep Reply's platform and change two things: a self-hosted Ministral 3 8B replaces the retired external LLM, and the LLM leaves the 15-minute control path.
6. Demo: Ministral 3 8B wrote every plan of this week, and the replay gate decided which ones the battery ran.
7. The framework meets 15 of 20 KPIs against 5–6 for the pilots, and draws level with the free rule after AI cost.
8. Self-hosting beats the free rule from about 1,500 sites; an on-site model is a paid option for offline sites, not a saving.
9. One modelled winter week supports a staged rollout, gated on a summer replay before any promise to a client.

The argument runs in five steps:
- the answer, then the yardstick;
- the pilots fail it, and the second agent buys carbon at a high price;
- the redesign on Reply's own platform, then the demo;
- the KPI scores, then the fleet economics and the upsell;
- the limits and the rollout.

## Timing and speakers

| # | Time | Speaker | Running total |
|---|---|---|---|
| 0–4 | 0:10 + 0:30 + 0:40 + 0:45 + 0:35 | Sydney | 2:40 |
| 5–6 | 0:45 + 1:30 | Amir | 4:55 |
| 7–9 | 0:40 + 0:45 + 0:25 | Francesco | 6:45 |

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

### 2. KPIs (0:40)
**Layout.** One layer, five category columns: Value, AI economics, Carbon, Self-use and grid, Battery and timing.

**Each of the 20 KPIs is a card with:**
- a plain question;
- its code and unit;
- the pass line;
- a tag for its yardstick: free rule (blue), no battery, perfect optimiser, or fixed target.

The thresholds come from `data/Sense_Reply_B2_KPI_Conformity.xlsx`. No results are shown on this slide.

### 3. The two pilots (0:45)
**Bars.** Saving vs no battery against AI bill, per pilot:

| Pilot | Saving | AI bill | Ratio |
|---|---|---|---|
| A | €0.60 | €4.74 | 7.8× |
| C | €0.63 | €7.71 | 12.2× |

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

### 6. Demo (1:30)
**Slide.** A screenshot of the blocked Tuesday plus four "what to watch" items: Agent, Memory, Validator, KPIs.

**Click path:**
1. Plan for Mon at 11:00: knobs and reason. (0:20)
2. The similar past days and the memory arc. (0:20)
3. Tue: the gate blocks, and the previous valid plan runs. (0:20)
4. One day at 16×. (0:15)
5. KPIs tab. (0:15)

### 7. Results on our KPIs (0:40)
**Grid.** The same as slide 2. Each card gets three verdict dots (A · C · New): blue for Good, red for Improvable.

**Totals:** A 5/19, C 6/20, New 15/20.

**Money line:**
- N1 +€0.98, against +€1.03 for the free rule;
- VORB +€0.12 before AI cost;
- F1 −€0.06 after AI cost.

**Callout.** Most of the gain comes from design (no 80% target, export valued at its price), not from intelligence.

Source: report §6, workbook.

### 8. Business case (0:45)
**Chart.** Log-log: AI cost per site per week against fleet size, 100–10,000 sites. Points come from `model_cost.OPTIONS`.
- **Lines:** on-prem 8B, the same model on an EU API, and the on-site 3B box (flat €1.86–8.12/wk).
- **Thresholds:**
  - S_net €1.16: above it, AI eats the whole saving;
  - VORB €0.12: below it, the agent beats the free rule after AI.
- **Crossings:** the EU API from ~580 sites; on-prem from ~1,500.

**Upsell.** Every site already runs on without internet: rule, clamp and yesterday's plan. The 3B box adds daily replanning offline and keeps data on site. Price it at or above its cost of €97–422 per site per year.

Source: report §8.

### 9. Limits and rollout (0:25)
**Limits:**
- one modelled winter week, with PV that is not real weather;
- no CO2 field and no logs of agent proposals;
- the self-hosting cost is an estimate (€4k node, 0.1 FTE).

**Rollout,** report §9 phases 0–4:
- fix the baseline;
- prove decision value on other seasons;
- carbon desk;
- pilot sites on an EU API;
- in-house at ~1,000 sites.

### Appendix (Q&A only)
- **A1.** The decision pipeline, using the demo's stage names (report §3.2).
- **A2.** Trade-off matrix, three scenarios (report §7.1).
- **A3.** KPI formulas (report §4).
- **A4.** CO2 method (report §4 step 7).
- **A5.** Data corrections (report §10).
- **A6.** Ministral bench (report §3.3):
  - 8B: 21/21 valid JSON, ~27 s per call on an 8 GB laptop;
  - 3B: 14/14 valid JSON, 12–14 s per call.
