# Pitch deck: ghost deck (7 minutes, demo included)

Speakers: Sydney (slides 0–4), Amir (5–6, framework + demo), Francesco (7–8). Script: `docs/SCRIPT.md`.
Numbers follow the report basis (`docs/Sense Reply BDD B2 – Full Analysis Report.docx`):
- carbon at a constant 0.356 kg/kWh;
- token price assumed, 0.86 €/$;
- S5 modelled on run C inputs, start SoC 0.80;
- site assumed to be in Italy.

## Title-only read
0. One carbon-aware agent, not two.
1. One agent that plans once a day turns the pilot's €7.31 weekly loss into a €1.10 gain and cuts the AI bill by 99%.
2. We judge every agent against a free rule, because "saved vs no battery" alone makes the pilots look profitable.
3. Both pilots lose to a free rule, and their AI bill is 8 to 12 times what the battery saves.
4. The second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price; a carbon weight inside one agent costs €31–72.
5. The agent sets three knobs a day; a rule and a safety clamp run the battery every 15 minutes, behind a replay gate.
6. Demo: one week of the framework, played at 16×.
7. On our own KPIs, the framework goes from 5–6 to 16 conforming KPIs, and its worst case is the free rule.
8. These results come from one modelled winter week; three data gaps decide whether they hold.

The argument runs: the answer, then the yardstick. The pilots fail it. The second agent buys carbon at a high price. Then the redesign, the demo of it running, its KPI scores and what could break it.

## Timing and speakers

| # | Time | Speaker | Running total |
|---|---|---|---|
| 0–4 | 0:10 + 0:35 + 0:50 + 0:50 + 0:45 | Sydney | 3:10 |
| 5–6 | 0:45 + 1:30 | Amir | 5:25 |
| 7–8 | 0:45 + 0:35 | Francesco | 6:45 |

That leaves 15 s of buffer. The demo plays the **precomputed** week. A live Gemini week takes 2:44–5:23 on Render free, so never run it live on stage. Keep a 60 s screen recording as a backup.

## Slides

### 0. Title (0:10)
- "One carbon-aware agent, not two". Subtitle: Sense Reply B2, Albert School BDD, Nov 2026. Names of the speakers.
- Exhibit: none.

### 1. Answer (0:35)
**One agent that plans once a day turns the pilot's €7.31 weekly loss into a €1.10 gain and cuts the AI bill by 99%.**
- Exhibit: three before → after figures, pilot C → S5 conservative:

| KPI | Pilot C | S5 conservative |
|---|---|---|
| N1 net value after AI cost | −€7.31/wk | +€1.10/wk |
| AI cost | €7.71/wk | €0.01/wk |
| Grid CO2 | 21.3 kg/wk | 13.5 kg/wk |

- Footer: modelled on one winter week, run C inputs. Source: report §1, §8.2.

### 2. KPIs (0:50)
**We judge every agent against a free rule, because "saved vs no battery" alone makes the pilots look profitable.**
- Exhibit: KPI tree, five groups. Show the ID and a plain name only, no formulas:
  - Value: S_net, VCR, VORB
  - AI economics: N1, N2, O1, O5
  - Carbon: S2b, MAC
  - Self-use and grid: SCR, SSR, PSR
  - Battery and orchestration: B4, C5
- Side note: there are three twins for every run (no battery, static rule, perfect-foresight optimiser). Thresholds can be edited in the Excel.
- Callout: the pilots conform on 5–6 of 19–20 KPIs.
- Source: report §4 step 3, §5; `data/Sense_Reply_B2_KPI_Conformity.xlsx`.

### 3. The two pilots (0:50)
**Both pilots lose to a free rule, and their AI bill is 8 to 12 times what the battery saves.**
- Exhibit: comparison table, highlighted on N1:

| | Pilot A (cost) | Pilot C (cost + sust.) | Static rule |
|---|---|---|---|
| N1 net after AI (€/wk) | −4.33 | −7.31 | +1.03 |
| VORB vs rule (€/wk) | −0.73 | −0.67 | 0 |
| AI cost (€/wk) | 4.74 | 7.71 | 0 |
| LLM calls per decision | 4.4 | 7.6 | 0 |
| Grid CO2 (kg/wk) | 21.9 | 21.3 | 11.9 |

- Three callouts on the causes, taken from the prompts and BSS.json:
  - a fixed 80% target fills the battery by late morning;
  - export is valued at zero, so midday PV goes out at €0.09 and comes back at €0.11–0.12 in the evening;
  - the sustainability agent gets no price and no CO2.
- Source: report §4 step 9, §5.2.

### 4. Cost vs sustainability (0:45)
**The second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price; a carbon weight inside one agent costs €31–72.**
- Exhibit: scatter. x = grid CO2 (kg/wk, lower is better), y = N1 (€/wk). Points:

| Scenario | CO2 (kg/wk) | N1 (€/wk) |
|---|---|---|
| A | 21.9 | −4.33 |
| C | 21.3 | −7.31 |
| Static rule | 11.9 | +1.03 |
| S5 conservative | 13.5 | +1.10 |
| S5 upside | 22.2 | +1.78 |

- Callouts:
  - A → C: +€2.97/wk for −0.7 kg, which is €4,300/t (€2,000/t on hourly carbon), against an EU ETS price of about €90/t;
  - S5 upside earns the most but emits like the pilots, so it runs in shadow mode.
- The full trade-off matrix goes to the appendix. Source: report §6.2, §7.

### 5. Framework (0:45)
**The agent sets three knobs a day; a rule and a safety clamp run the battery every 15 minutes, behind a replay gate.**
- Exhibit: a left-to-right diagram. Use the same stage names as the demo's pipeline strip, so the audience recognises them on the next slide.
  - Inputs: day-ahead prices, hourly ENTSO-E CO2 for Italy, and memory of the 3–5 most similar past days.
  - Agent: one call a day, goal € + λ·CO2.
  - Validator: schema check, then the replay gate.
  - Rule: every 15 min.
  - Clamp: SoC 10–90%, 5 kW.
  - Site, then back to memory: one row a day.
- Fallback line under the diagram: agent plan → previous valid plan → static rule.
- Today vs framework, in small type: LLM calls ~730/day → 1–3/day; LLM leaves the control path; export valued at sellPrice; the 80% target becomes an evening reserve.
- Source: report §3, `docs/PROPOSAL.md`.

### 6. Demo (1:30)
**Demo: one week of the framework, played at 16×.**
- Slide: a full-bleed cue with the site URL and "precomputed run, Gemini Flash standing in for Devstral 2".
- Click path:
  1. Simulation tab at 11:00 on plan day 1: the agent's knobs and its reason. (0:20)
  2. Similar past days and their regret; the memory → agent arc fires. (0:20)
  3. A gate-blocked day: knobs struck through, fallback to the previous plan. (0:20)
  4. Play at 16× for one day: energy flows and the day chart. (0:15)
  5. KPIs tab: the "Ours" column next to A, C and the rule. (0:15)
- Number check: the demo shows N1 ≈ 1.15 for conservative at λ 0.10; the report says 1.10. Say "rerun of the same model". Better: align the demo before the talk.

### 7. Results on our KPIs (0:45)
**On our own KPIs, the framework goes from 5–6 to 16 conforming KPIs, and its worst case is the free rule.**
- Exhibit: before/after table; the upside column is greyed and tagged "shadow mode":

| KPI | Pilot A | Pilot C | S5 cons. | S5 upside |
|---|---|---|---|---|
| N1 net after AI (€/wk) | −4.33 | −7.31 | +1.10 | +1.78 |
| VORB vs rule (€/wk) | −0.73 | −0.67 | +0.08 | +0.79 |
| AI cost (€/wk) | 4.74 | 7.71 | 0.01 | 0.01 |
| Grid CO2 (kg/wk) | 21.9 | 21.3 | 13.5 | 22.2 |
| Self-consumption | 0.52 | 0.54 | 0.78 | 0.53 |
| Peak import (kW) | 4.81 | 2.93 | 2.24 | 5.11 |
| KPIs Good | 5–6 | 5–6 | 16 | 14 |

- Callout: most of the conservative gain comes from dropping the 80% target and valuing export, not from intelligence. Say so before the jury does.
- Source: report §6.2, §8.2.

### 8. Limits and next steps (0:35)
**These results come from one modelled winter week; three data gaps decide whether they hold.**
- Left, the gaps:
  1. The data has no CO2 field and no agent proposal logs, so win rate and regret can't be measured on the pilots.
  2. The runs are not controlled: start SoC differs (A 0.57, C 0.80) and so does panel dirt. Only A vs C, scored against twins, is usable.
  3. There is one winter week, and the simulated PV is not real weather (peak at 10:00, ~14 h of sun in January).
- Right, next steps:
  - replay a summer week;
  - log the agents' proposals;
  - feed a weather forecast to the agent;
  - run the upside mode in shadow mode before going live.
- Source: report §10.3, §9.3.

### Appendix (Q&A only)
- A1. Full trade-off matrix (report §7.1)
- A2. KPI formulas: C_adj, S, S_net, N1, N2 (report §4 step 4)
- A3. CO2 method: ENTSO-E A75 → IPCC lifecycle factors → hourly CI (report §4 step 7)
- A4. Data corrections: cost field, missing sample in B, wear €0.005/kWh (report §10.2)
