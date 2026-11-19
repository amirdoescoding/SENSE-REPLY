# Pitch script (7 minutes, demo included)

Spoken script for the deck in `docs/PRESENTATION.md`. Titles and numbers match it exactly. Pace: 130 words per minute. Word counts include the handover line. Each figure such as "€7.31" counts as one word but takes three or four to say, so slides heavy with numbers stay well under budget.

## Storyline

- **Governing thought:** one carbon-aware agent that plans once a day, with a rule running the battery, beats both pilots and costs about a cent a week in AI.
- **Situation (slides 0–2):** Sense Reply piloted two LLM setups on a home battery, and we built a yardstick to judge them: a free static rule and 19 to 20 KPIs.
- **Complication (slides 3–4):** both pilots lose to the free rule, their AI bill is 8 to 12 times the saving, and the second agent buys CO2 at €4,300 a tonne.
- **Resolution (slides 5–7):** one agent sets three knobs a day, a rule and a clamp execute, and the framework conforms on 16 KPIs with a worst case equal to the free rule.
- **Caveat (slide 8):** it all comes from one modelled winter week, and three data gaps decide whether it holds.

## Slides

### 0. One carbon-aware agent, not two.
Sydney · 0:10 · 21 words (budget 22)

Good afternoon, we are Sydney, Amir and Francesco. We tested Sense Reply's two battery agents.

**Say aloud:** one agent (no number on this slide).
**Handover:** Our answer is one carbon-aware agent.

### 1. One agent that plans once a day turns the pilot's €7.31 weekly loss into a €1.10 gain and cuts the AI bill by 99%.
Sydney · 0:35 · 70 words (budget 76)

Pilot C runs two LLM agents on a home battery and, after its AI bill, loses €7.31 a week. One agent that plans once a day gains €1.10 in our model. The AI bill falls from €7.71 to one cent, a 99% cut, and grid CO2 from 21.3 to 13.5 kilos. All of it is modelled on one winter week.

**Say aloud:** minus €7.31 becomes plus €1.10 a week.
**Handover:** To judge any agent fairly, we first needed a yardstick.

### 2. We judge every agent against a free rule, because "saved vs no battery" alone makes the pilots look profitable.
Sydney · 0:50 · 100 words (budget 108)

Next to the same house without a battery, both pilots look profitable. That bar is too low. We score every run against twins on its own sun, load and prices: no battery, a free static rule, and a perfect-foresight optimiser. The rule charges on solar surplus and discharges when the house needs power. It costs nothing, so any AI has to beat it. We grouped 19 to 20 KPIs into five families, from value to battery health, with editable thresholds in our Excel. The pilots conform on 5 to 6.

**Say aloud:** the pilots conform on 5 to 6 KPIs out of 19 to 20.
**Handover:** Here is how the two pilots do against that rule.

### 3. Both pilots lose to a free rule, and their AI bill is 8 to 12 times what the battery saves.
Sydney · 0:50 · 101 words (budget 108)

Pilot A runs a cost agent; pilot C adds a sustainability agent. Both lose to the free rule before any AI cost, A by 73 cents and C by 67. Then the token bill: €4.74 a week for A, €7.71 for C, 8 to 12 times what the battery saves. The prompts show why. A fixed 80% target fills the battery by late morning. Export counts as zero, so midday solar sells at 9 cents and is bought back at 11 to 12. The sustainability agent never sees a price or CO2.

**Say aloud:** the AI bill is 8 to 12 times the saving.
**Handover:** That blind agent is where the carbon money goes.

### 4. The second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price; a carbon weight inside one agent costs €31–72.
Sydney · 0:45 · 92 words (budget 98)

A and C run on the same panels. The second agent adds €2.97 a week of AI bill and avoids 0.7 kilos of CO2. That is €4,300 a tonne, 48 times the EU carbon price of about €90. On hourly grid data it is still €2,000. Our carbon figures assume an Italian site. On the chart, our conservative mode sits next to the free rule and earns a little more. A carbon weight inside one agent costs 31 to 72 euros a tonne.

**Say aloud:** €4,300 a tonne, 48 times the EU carbon price.
**Handover:** Amir will show you how that one agent works.

### 5. The agent sets three knobs a day; a rule and a safety clamp run the battery every 15 minutes, behind a replay gate.
Amir · 0:45 · 94 words (budget 98)

Thanks, Sydney. Once a day, the agent reads day-ahead prices, hourly CO2 for Italy, and similar past days from memory. It returns three knobs: a battery floor, an evening reserve, and a value for stored energy. A replay gate blocks any plan that loses on past data. Every 15 minutes a rule turns the knobs into kilowatts, and a clamp keeps the battery between 10 and 90 percent. If anything fails, yesterday's plan runs, then the free rule. LLM calls drop from about 730 a day to one to three.

**Say aloud:** LLM calls drop from about 730 a day to one to three.
**Handover:** Here it is running.

### 6. Demo: one week of the framework, played at 16×.
Amir · 1:30 · 131 words (budget 195; the rest is silence while the demo plays)

[Click 1: Simulation tab, plan day 1, 11:00. 0:20]
This is the site at 11:00 on the first plan day. The agent has just set its knobs for the next 24 hours, with its reason in plain words. Gemini Flash stands in for Devstral 2, and the week is precomputed.

[Click 2: similar past days, memory arc fires. 0:20]
Before deciding, it looked at these similar past days. Each shows its regret, the cents that day left on the table. This arc is memory feeding the agent.

[Click 3: gate-blocked day. 0:20]
Here the gate blocked a plan. The knobs are struck through, so the battery kept the previous valid plan. Nobody had to step in.

[Click 4: play one day at 16×. 0:15]
One day at 16 times. Solar fills the battery, and the battery covers the evening.
(Stay silent and let it run.)

[Click 5: KPIs tab. 0:15]
Our column sits next to pilots A and C and the free rule.

**Say aloud:** one LLM call a day runs the whole week.
**Handover:** Francesco will tell you what the week adds up to.

### 7. On our own KPIs, the framework goes from 5–6 to 16 conforming KPIs, and its worst case is the free rule.
Francesco · 0:45 · 90 words (budget 98)

The pilots conform on 5 to 6 KPIs; the conservative framework on 16. Net value after AI goes from minus €7.31 to plus €1.10 a week, and CO2 from 21.3 to 13.5 kilos. Two plain fixes carry most of that gain: dropping the 80% target and pricing export. Against the free rule we gain 8 cents a week, and if the agent or the data fails, the system falls back to that rule. The upside mode earns €1.78 but raises CO2, so it stays in shadow mode.

**Say aloud:** 16 conforming KPIs, against 5 to 6 for the pilots.
**Handover:** Now the limits.

### 8. These results come from one modelled winter week; three data gaps decide whether they hold.
Francesco · 0:35 · 72 words (budget 76)

All of this comes from one modelled winter week, and three gaps decide whether it holds. The data has no CO2 field and no logs of agent proposals. The runs start from different charge levels and panel dirt. And the simulated sun does not match January weather. Next, we would replay a summer week, log every proposal, add a weather forecast, and shadow-test the upside mode.

**Say aloud:** one modelled winter week.
**Handover:** Thank you, we welcome your questions.

## Word counts

| Speaker | Slides | Words | Budget at 130 wpm |
|---|---|---|---|
| Sydney | 0–4 | 384 | 412 (3:10) |
| Amir | 5–6 | 225 | 293 (2:15) |
| Francesco | 7–8 | 162 | 173 (1:20) |
| Total | | 771 | 878 (6:45) |

## Q&A prep

1. **Why not ship the free static rule?** (Francesco) It is our fallback, and you could ship it tomorrow. For one cent a week, the agent adds what a rule cannot: it prices CO2 through the λ dial and explains each plan. It beats the rule by only €0.08 a week here, and the fallback chain means it can never end up below the rule.
2. **The upside mode raises CO2 and the peak. Why show it?** (Francesco) It charges from the grid at night, so CO2 rises to 22.2 kg and the peak to 5.11 kW. That is why it runs in shadow mode with a peak cap, and the client picks the mode through the carbon weight.
3. **One winter week only?** (Francesco) Yes, and we say so on the last slide. Pilot C loses to the rule on all six full days, so the direction looks solid, but summer brings more PV and a smaller evening need, so the ranking must be rerun on a summer week before any promise to a client.
4. **Where does the token price come from?** (Sydney) It is assumed: the Devstral 2 list price, $0.40 in and $2.00 out per million tokens at 0.86 €/$, and that model was retired on 31 July 2026. The pilots break even only if the AI costs under about €0.40 a week, so they lose at any plausible price, and the framework makes one call a day, so its result barely moves.
5. **Why Gemini in the demo?** (Amir) Devstral 2 is retired, and Gemini Flash has a free tier that let us run the demo at no cost. The framework only needs one call a day, so the client can swap in any model, including a self-hosted one.
6. **Does the agent use a weather forecast?** (Amir) We have not built it. The agent uses a "tomorrow looks like today" forecast, and the simulator's PV is not real weather (it peaks at 10:00 with about 14 hours of sun in January), so a real forecast would not match it. It is a next step for runs on real dates.
7. **The demo shows N1 ≈ €1.15, the report €1.10. Which is right?** (Amir) Both come from the same model. The demo is a rerun with the knobs the live agent chose, and the gap is 5 cents a week; the report figure is our reference.
8. **Why is run B left out?** (Sydney) B's panels start dirtier, so it gets 24 kWh less PV (69 against 93 kWh) and one sample is missing. Any gap would reflect the panels. C has A's panel dirt, so A against C isolates the second agent.
9. **Slide 5 says "a rule", but the model uses an optimiser. Which one runs the battery?** (Amir) In the modelled results, a rolling optimiser with a 24-hour "tomorrow looks like today" forecast turns the knobs into kW every 15 minutes. The plain rule is the fallback and the simplest version to ship. Either way, the LLM stays off the 15-minute loop.
