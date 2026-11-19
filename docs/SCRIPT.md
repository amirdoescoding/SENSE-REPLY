# Pitch script (7 minutes, demo included)

This is the spoken script for the deck in `docs/PRESENTATION.md`. Titles and numbers match the deck exactly.

**Pace:** 130 words per minute. Counts include the handover line. A figure such as "€7.31" counts as one word but takes three or four to say, so slides heavy with numbers sit under budget on purpose.

## Storyline

| Part | Slides | Message |
|---|---|---|
| Governing thought | | One carbon-aware agent on a model Reply hosts beats both pilots, emits 43% less, and pays for itself once the fleet is large enough. |
| Situation | 0–2 | Sense Reply piloted two LLM setups on a home battery. We built the yardstick: a free rule and 20 KPIs. |
| Complication | 3–4 | Both pilots lose to the free rule, and their AI bill is 8 to 12 times the saving. The second agent buys CO2 at €4,300 a tonne. |
| Resolution | 5–7 | Two changes on Reply's platform. The demo shows them running and the 15 of 20 KPIs. Fleet size decides the AI bill, and an on-site model becomes a paid option. |
| Caveat | 8 | One modelled winter week, so a summer replay gates any promise. |

## Slides

### 0. One carbon-aware agent, on a model Reply owns
Sydney · 0:10 · 25 words (budget 22; the names are said fast)

Good afternoon, we are Sydney, Amir and Francesco. We tested Sense Reply's two battery agents.

**Say aloud:** one agent (no number on this slide).
**Handover:** Our answer is one agent, on a model Reply owns.

### 1. One self-hosted agent that plans once a day turns pilot C's €7.31 weekly loss into a €0.98 gain and cuts the AI bill by 98%
Sydney · 0:30 · 61 words (budget 65)

Pilot C runs two LLM agents on a home battery. After its AI bill, it loses €7.31 a week. Our agent plans once a day on a model Reply hosts, and gains 98 cents. The AI bill falls from €7.71 to 18 cents, and grid CO2 from 21.3 to 12.2 kilos.

**Say aloud:** minus €7.31 becomes plus 98 cents a week.
**Handover:** To judge any agent fairly, we first needed a yardstick.

### 2. We judge every agent against a free rule, because "saved vs no battery" alone makes the pilots look profitable
Sydney · 0:50 · 107 words (budget 108)

Next to the same house without a battery, both pilots look profitable. So we built a tougher yardstick: the free rule on the left. It is two lines of code. When the sun makes more than the house uses, charge. When the house uses more, discharge. No AI, no forecast, and on this week it saves €1.03. Any AI has to beat it, or Reply should ship the rule. On the right are our 20 KPIs in five families. Each card asks one plain question and gives its pass line. The blue ones compare against the rule.

**Say aloud:** two lines of code save €1.03 a week.
**Handover:** Here is how the two pilots do against that rule.

### 3. Both pilots lose to a free rule, and their AI bill is 8 to 12 times what the battery saves
Sydney · 0:45 · 91 words (budget 98)

Both lose to the free rule before any AI cost, A by 73 cents and C by 67. Then comes the token bill: €4.74 a week for A, €7.71 for C. That is 8 to 12 times what the battery saves. The prompts show why. A fixed 80% target fills the battery by late morning. Export counts as zero, so midday solar sells at 9 cents and comes back at 11 to 12. The sustainability agent never sees a price or CO2.

**Say aloud:** the AI bill is 8 to 12 times the saving.
**Handover:** That blind agent is where the carbon money goes.

### 4. A second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price, while a carbon weight inside one agent costs about nothing
Sydney · 0:35 · 76 words (budget 76)

A and C run on the same panels. The second agent adds €2.97 a week of AI bill and avoids 0.7 kilos of CO2. That is €4,300 a tonne, 48 times the EU carbon price. Top left, our framework sits next to the free rule. Inside one agent, a carbon weight cut 0.85 kilos this week at no extra cost. Our carbon figures assume an Italian site.

**Say aloud:** €4,300 a tonne, 48 times the EU carbon price.
**Handover:** Amir will show you where that one agent lives.

### 5. We change two things on Reply's platform: a self-hosted Ministral 3 8B replaces the retired LLM, and the LLM leaves the 15-minute loop
Amir · 0:45 · 92 words (budget 98)

Thanks, Sydney. We kept the shape of Reply's platform and changed the blue boxes.

**Change one.** The pilots called Devstral 2 through an external API, and Mistral retired it in July. We replace it with Ministral 3 8B: open weights, hosted on Reply's servers.

**Change two.** The model now writes one plan a day. On the gateway, a rule and a safety clamp run the battery every 15 minutes. If the internet drops, the site keeps running on yesterday's plan. Clients who need offline replanning can buy the 3B on the gateway.

**Say aloud:** one call a day instead of about 730.
**Handover:** Here it is running.

### 6. Demo: Ministral 3 8B wrote every plan of this week, and the replay gate decided which ones the battery ran
Amir · 1:30 · 127 words (budget 195; the rest is silence while the demo plays)

**[Click 1: Monday plan at 11:00. 0:20]**
This is the site at 11:00 on Monday. Ministral 3 8B has just set three knobs for the next 24 hours, and it explains why in plain words. We ran these plans on a laptop; the demo replays them.

**[Click 2: similar past days, memory arc. 0:20]**
Before deciding, the model saw these similar past days and the cents each one left on the table. No training: just memory.

**[Click 3: Tuesday, blocked. 0:20]**
On Tuesday the replay gate blocked the plan. It lost on recent days, so yesterday's plan ran. Nobody had to step in.

**[Click 4: play one day at 16×. 0:15]**
One day at 16 times. Solar fills the battery, and the battery covers the evening.
(Stay silent and let it run.)

**[Click 5: KPIs tab. 0:15]**
Our column sits next to pilots A and C: 15 KPIs out of 20 pass, against 5 and 6.

**Say aloud:** the gate decides, not the model.
**Handover:** Francesco will tell you what the week adds up to.

### 7. Self-hosting beats the free rule from about 1,500 sites; an on-site model is a paid option for offline sites, not a saving
Francesco · 0:55 · 114 words (budget 119)

Before AI cost, our agent beats the free rule by 12 cents a week per site. The question is whether the AI costs less than that. On the right is the math. Two GPU servers, their power, and a tenth of an engineer cost about €9,160 a year. Divide by 52 weeks and by the number of sites. At 1,000 sites that is 18 cents, more than our 12-cent lead. From about 1,500 sites it drops below. On an EU API, with the same weights, it happens at 580. The grey band is a box on every site: €97 to €422 a year. Sell it to clients who need offline replanning.

**Say aloud:** €9,160 a year, divided by sites, below 12 cents from 1,500.
**Handover:** Now the limits.

### 8. One modelled winter week supports a staged rollout, gated on a summer replay before any promise to a client
Francesco · 0:30 · 50 words (budget 65)

All of this rests on one modelled winter week, with no real weather and no agent logs. Our hosting cost is an estimate. So we roll out in steps: fix the baseline, replay summer, then pilot sites on an API, then in-house at scale.

**Say aloud:** a summer replay comes first.
**Handover:** Thank you, we welcome your questions.

## Word counts

| Speaker | Slides | Words | Budget at 130 wpm |
|---|---|---|---|
| Sydney | 0–4 | 360 | 368 (2:50) |
| Amir | 5–6 | 219 | 293 (2:15) |
| Francesco | 7–8 | 164 | 184 (1:25) |
| Total | | 743 | 845 (6:30) |

## Q&A prep

1. **F1 is negative. Why not ship the free rule?** (Francesco)
   - The rule is our fallback, and Reply could ship it tomorrow.
   - The agent adds what a rule cannot: a CO2 dial, a daily plan with a reason for the owner, and memory.
   - The gap is 6 cents a week, and it closes from about 1,500 sites.
   - If the model never beats the rule on a summer week, ship the rule with the plan logic and keep the LLM for explanations.
2. **The EU API is cheaper. Why self-host?** (Francesco)
   - At 1,000 sites the API costs about 11 cents less a week.
   - Self-hosting buys control: Reply holds the weights, no vendor can retire the model, as happened with Devstral 2, and data stays on Reply's platform.
   - Start on the API and move in-house; it is the same model and prompt, so the switch is a config change.
3. **Does a site need the 3B box to work offline?** (Amir)
   - No. Every gateway already runs the rule, the clamp and yesterday's plan.
   - The box adds daily replanning without internet and keeps data on site.
   - It costs €97 to €422 a site a year, so Reply sells it as a premium.
4. **Why Ministral 3?** (Amir)
   - Open weights under Apache 2.0, EU origin, and the same vendor family as Devstral.
   - The 8B wrote 21 of 21 valid plans on an 8 GB laptop; the 3B wrote 14 of 14.
5. **Where does the self-hosting cost come from?** (Sydney)
   - It is our estimate: a €4,000 GPU node pair, 100 W, 0.1 FTE of operations, 5 years of life, at 1,000 sites.
   - Operations make up three quarters of it. If Reply already runs the compute, the cost falls to about 4 cents a site a week.
6. **The gate kept only 2 of 7 plans. Does the model add anything?** (Amir)
   - This week, no: plans from the 8B, the 3B, a cloud model and "copy the best similar day" land within half a cent.
   - The gate stops a bad plan from costing money.
   - Decision value has to show on other seasons, and that is roadmap step two.
7. **One winter week only?** (Francesco)
   - Yes, and the last slide says so.
   - Pilot C loses to the rule on all six full days, so the direction looks solid.
   - Summer brings more PV and a smaller evening need, so we rerun before any promise.
8. **Why is run B left out?** (Sydney)
   - B's panels start dirtier, so it gets 24 kWh less PV, and one sample is missing.
   - C has A's panel dirt, so A against C isolates the second agent.
9. **The platform slide says "a rule", but the model uses an optimiser. Which runs the battery?** (Amir)
   - In the modelled results, a rolling optimiser with a 24-hour "tomorrow looks like today" forecast turns the knobs into kW every 15 minutes.
   - The plain rule is the fallback and the simplest version to ship.
   - Either way, the LLM stays off the 15-minute loop.
