# Pitch script and speaker prep (7 minutes, demo included)

The spoken script for the deck in `docs/PRESENTATION.md`, plus what each speaker must know for questions. Titles and numbers match the deck. Every number traces to `docs/REPORT.md`, `data/ours_ministral.json` or `demo/out/`.

**How to use it.**
- Part 1 is for all three of us. Learn the case, the ten numbers and the traps before your own slides.
- Part 2 is per speaker and per slide: what the slide shows, the spoken text, what to know cold, and the questions you own.
- Pace: 130 words a minute. A figure such as "€7.31" counts as one word but takes three or four to say, so slides heavy with numbers sit under budget on purpose.

| Slides | Speaker | Time | Running total |
|---|---|---|---|
| 0–4 | Sydney | 0:10 + 0:30 + 0:50 + 0:45 + 0:35 | 2:50 |
| 5–6 | Amir | 0:45 + 0:30 + 1:00 demo | 5:05 |
| 7–8 | Francesco | 0:55 + 0:30 | 6:30 |

---

# Part 1. The case (everyone)

## The case in 60 seconds

- **Client.** Sense Reply (Reply group) runs an AI-native IoT platform, "Agentic Operations for E&U". It steers home energy assets through a central AI layer and a gateway on each site.
- **The site.** Nine PV panels, one house, one grid connection, and a 10 kWh battery: 5 kW maximum, usable between 10% and 90%, 95% efficient each way.
- **The data.** Three simulated runs over the same week, 5 Jan 11:00 to 12 Jan 10:45 2026, in 15-minute steps (672 samples).
  - **Pilot A:** orchestrator + cost agent. 2,948 LLM requests.
  - **Pilot C:** orchestrator + cost agent + sustainability agent, same panel dirt as A. 5,118 requests.
  - **Run B:** like C, but with dirtier panels (24 kWh less PV) and one missing sample. We left it out.
  - Both pilots called Devstral 2 (123B) through Mistral's API. Mistral retired it on 31 July 2026.
- **The brief.** Define KPIs with formulas, compare the two set-ups, price the cost vs sustainability trade-off, and propose a better agent framework.
- **Our answer.** One carbon-aware agent instead of two. It writes one plan a day, a rule and a safety clamp run the battery every 15 minutes, and the model is Ministral 3 8B, hosted by Reply.

## Storyline

| Part | Slides | Message |
|---|---|---|
| Governing thought | | One carbon-aware agent on a model Reply hosts beats both pilots, emits 43% less, and pays for itself once the fleet is large enough. |
| Situation | 0–2 | Sense Reply piloted two LLM set-ups on a home battery. We built the yardstick: a free rule and 20 KPIs. |
| Complication | 3–4 | Both pilots lose to the free rule, and their AI bill is 8 to 12 times the saving. The second agent buys CO2 at €4,300 a tonne. |
| Resolution | 5–7 | Two changes on Reply's platform. The demo shows them running and the 15 of 20 KPIs. Fleet size decides the AI bill; an on-site model becomes a paid option. |
| Caveat | 8 | One modelled winter week, so a summer replay gates any promise. |

**Three scenarios, one yardstick.** Pilot A, pilot C and the New framework are the scenarios. The free static rule is the yardstick: charge when the sun makes more than the house uses, discharge when the house uses more. It is not a fourth scenario.

## Numbers everyone must know

Per site, per week, unless stated.

| What | Pilot A | Pilot C | New framework | Free rule |
|---|---|---|---|---|
| Gross saving vs no battery (S) | €0.60 | €0.63 | €1.42 | |
| Saving net of wear (S_net) | €0.41 | €0.40 | €1.16 | €1.03 |
| Value over the free rule, before AI (VORB) | −€0.73 | −€0.67 | +€0.12 | 0 |
| AI cost (O5) | €4.74 | €7.71 | €0.18 | 0 |
| **Net after AI cost (N1)** | **−€4.33** | **−€7.31** | **+€0.98** | |
| Value over the rule after AI (F1) | −€5.47 | −€8.38 | −€0.06 | |
| Grid CO2 (S1) | 21.9 kg | 21.3 kg | 12.2 kg | 11.9 kg |
| LLM calls per day | ~420 | ~730 | 1 | 0 |
| KPIs rated Good | 5 | 6 | 15 of 20 | |

Plus:
- **€4,300 a tonne:** what the second agent pays per tonne of CO2 avoided, 48 times the EU carbon price (~€90/t).
- **~1,500 sites:** where self-hosting beats the free rule after AI cost. ~580 on an EU API.
- **€9,160 a year:** two GPU servers, power, and 0.1 of an engineer.
- **€97–422 per site per year:** the 3B box on the gateway, sold as a paid option.
- **−98% AI bill, −43% grid CO2:** New framework vs pilot C.

## KPI glossary (20 scored KPIs)

| Code | Plain question | Pass line |
|---|---|---|
| S_net | What does the battery save vs no battery, after wear? | ≥ €1.03 (the rule) |
| VCR | What share of the best possible saving do we capture? | ≥ 0.6 |
| VORB | Do we beat the free rule before AI cost? | > 0 |
| N1 | Are we in profit after AI cost? | > 0 |
| N2 | How many euros of AI per euro saved? | < 0.2 |
| F1 | Do we beat the free rule after AI cost? | > 0 |
| O5 | What does the AI cost a week? | < €0.50 |
| O1 | LLM calls per 15-minute decision | < 0.3 |
| O3 | Share of the 15-minute slot spent waiting on the LLM | < 0.1 |
| S2b | CO2 avoided vs the rule | > 0 |
| S3 | How dirty is the grid power we buy (g/kWh)? | < 356 (week mean) |
| MAC | What does a kg of CO2 avoided cost via the carbon dial? | < €0.09/kg (EU price) |
| SCR | Share of our solar we use ourselves | ≥ 0.7 |
| SSR | Share of the house's need met without the grid | ≥ 0.6 |
| PSR | How much do we shave the grid peak? | ≥ 0.25 |
| G2 | Grid violations or penalties | 0 |
| B1 | Storage efficiency | ≥ 0.88 |
| B2 | Full cycles per week | ≤ 7 |
| B4 | Time at the charge limits | ≤ 25% |
| C5 | Share of imports bought at expensive hours | ≤ 0.5 |

Shown as context, not scored: S1 grid CO2, G1 peak import, B3 wear cost, B6 time near 80%, C4 price spread.

**The New framework fails 5:** F1 (−€0.06), S2b (−0.3 kg vs the rule), S3 (373 g/kWh), B4 (29% at limits), C5 (0.77).
**The four rule-based KPIs** (blue edge on slide 2): S_net, VORB, F1, S2b.
**Not assessable:** win rate, agent agreement and regret, because the pilots' proposals are not logged.

## Traps (the questions that catch people out)

1. **"Slide 3 says €1.42, the report says €1.16."** €1.42 is the gross saving S. €1.16 is S_net, after €0.005 of wear per kWh discharged. Slide 3 compares gross saving with AI bill for all three, so the pilots also show gross (€0.60, €0.63). The free rule's €1.03 is net of wear.
2. **"F1 is negative, so why not ship the rule?"** Before AI cost we beat the rule by 12 cents. At 1,000 sites the model costs 18 cents, so after AI cost we trail by 6 cents. From ~1,500 sites, or on an EU API from ~580, we clear it. The agent also adds a CO2 dial, a daily plan with a reason, and memory.
3. **"The pilots are measured, yours is modelled."** True, and we say it. We modelled the framework on run C's own sun, load and prices, starting at 80% charge like C, with a "tomorrow looks like today" forecast. The pilots saw 24 hours of simulated data ahead and still lost.
4. **"Which CO2 figure?"** KPIs use a constant 0.356 kg/kWh: the mean of ENTSO-E hourly generation for Italy with IPCC lifecycle factors. The hourly series (214–439 g/kWh) is a check. It moves absolute CO2 by ~8% and does not change the ranking.
5. **"A rule or an optimiser?"** In the modelled results a rolling optimiser with a 24-hour persistence forecast turns the knobs into kW every 15 minutes. The plain rule is the fallback and the simplest version to ship. The LLM stays off the 15-minute loop either way.
6. **"The gate kept only 2 of 7 plans."** On the other 5 days the model's plan cost a fraction of a cent more than the default on the replay, so the previous valid plan ran. This week the model adds a plan, a reason and a dial, not better decisions. Decision value has to show on other seasons.
7. **"You ran it on a laptop."** The 8B ran 3-bit quantised on an 8 GB laptop, 21 of 21 valid plans. The costed set-up serves it at full quality on Reply's servers. Re-run the week there before go-live.
8. **"Is this one site or a fleet?"** One site, one week. The fleet numbers (1,000 sites, ~1,500 break-even) are cost arithmetic, not observed fleet behaviour.

---

# Part 2. Per speaker, per slide

## Sydney: slides 0–4 (2:50)

You own the problem: the yardstick, the pilots' failure and the price of carbon. Questions on KPIs, data, the pilots and CO2 come to you.

### Slide 0. One carbon-aware agent, on a model Reply owns
0:10 · 25 words (budget 22; the names go fast)

**What it shows.** Title and our names. No exhibit.

**Job in the story.** State the answer before anything else.

**Spoken text.**
> Good afternoon. We are Sydney, Amir and Francesco. We tested Sense Reply's two battery agents. Our answer is one agent, on a model Reply owns.

**Say aloud:** one agent.

**If you get lost:** "One agent, on a model Reply owns."

### Slide 1. One self-hosted agent that plans once a day turns pilot C's €7.31 weekly loss into a €0.98 gain and cuts the AI bill by 98%
0:30 · 61 words (budget 65)

**What it shows.** Three before → after figures, pilot C → New framework: net value, AI cost, grid CO2.

**Job in the story.** The whole result in three numbers. Every later slide explains one of them.

**Spoken text.**
> Pilot C runs two LLM agents on a home battery. After its AI bill, it loses €7.31 a week. Our agent plans once a day, on a model Reply hosts, and gains 98 cents. The AI bill drops from €7.71 to 18 cents. Grid CO2 drops from 21.3 to 12.2 kilos. To judge any agent fairly, we first needed a yardstick.

**Say aloud:** minus €7.31 becomes plus 98 cents a week.

**Know cold.**
- N1 = S_net − AI cost. C: 0.40 − 7.71 = −7.31. Ours: 1.16 − 0.18 = +0.98.
- 0.18 ÷ 7.71 = 2.3%, so the bill falls 98%.
- 12.2 ÷ 21.3 = 0.57, so CO2 falls 43%.
- About €51 a year per site (0.98 × 52). Small in euros; the case rests on the fleet.
- Why compare with C and not A: C is the full pilot (cost + sustainability), and it shares A's panel dirt.

**Likely questions.**
- *"98 cents a week is nothing. Why would a client care?"*
  - Per site it is small: ~€51 a year on a 10 kWh battery.
  - The point is the sign. Each pilot site loses €225–380 a year, so every new customer adds a loss. Ours adds a gain.
  - The larger value is fleet orchestration, grid services and CO2 reporting, which one site's data cannot test (report §8.2).
- *"Your agent is modelled and the pilots are observed. Is that fair?"* See trap 3. Same sun, load, prices and starting charge as C. The pilots even had 24 hours of data ahead.
- *"Where does 18 cents come from?"* Francesco covers it on slide 7: €9,160 a year ÷ 52 ÷ 1,000 sites.

**If you get lost:** "Minus €7.31 becomes plus 98 cents, and the AI bill falls 98%."

### Slide 2. We judge every agent against a free rule, because "saved vs no battery" alone makes the pilots look profitable
0:50 · 104 words (budget 108)

**What it shows.**
- Left panel: the free rule in two lines, and "€1.03 a week".
- Right: 20 KPI cards in five family columns. Each card has a plain question, a code and a pass line.
- A blue edge marks the four KPIs that compare with the rule: S_net, VORB, F1, S2b.

**Job in the story.** Set the bar before showing the pilots fail it.

**Spoken text.**
> Compared with the same house without a battery, both pilots look profitable. So we built a tougher yardstick: the free rule, on the left. It is two lines of code. When the sun makes more than the house uses, charge. When the house uses more, discharge. No AI, no forecast, and on this week it saves €1.03. Any AI has to beat it, or Reply should ship the rule. On the right are our 20 KPIs in five families. Each card asks one plain question and shows its pass line. The blue ones compare against the rule. Now, the two pilots against that rule.

**Say aloud:** two lines of code save €1.03 a week.

**Know cold.**
- The five families: value and AI economics, carbon, self-use and grid, battery, orchestration and price timing. Point to the columns as you name them.
- Three counterfactual twins, each built on the run's own sun, load and prices: no battery, the free rule, and a perfect-foresight optimiser (a ceiling no one can reach; VCR uses it, S* = €2.18).
- How we made the runs fair:
  - the runs start and end at different charge levels, so we credit the energy left in the battery;
  - the data's `cost` field is not a running total, so we rebuild the bill as import × buy price − export × sell price;
  - we rebuild load from the energy balance, which closes within 0.5%.
- Four kinds of threshold:
  - benchmark: what the rule achieves (S_net ≥ €1.03);
  - break-even: N1 > 0, F1 > 0;
  - design target: N2 < 0.2, O1 < 0.3;
  - team-defined, to confirm with the client: SCR, SSR, PSR, B4.
- Wear: €0.005 per kWh discharged, from BSS.json (€100/kWh replacement × 0.005% health per full cycle).

**Likely questions.**
- *"Who set the thresholds?"* We did, by those four kinds. They sit in `Sense_Reply_B2_KPI_Conformity.xlsx` and anyone can edit them; the verdicts update.
- *"Why is the rule so strong?"* Winter, a regular week, and prices that peak in the evening. Storing midday sun for the evening is close to optimal here. In summer or with price spikes, planning can matter more.
- *"Why 20? Some KPIs look redundant."* Each answers a different client question: does it save, does the AI pay for itself, is it cleaner, does it stress the battery, does it load the grid. Three more (win rate, agreement, regret) need agent proposal logs, which the pilots don't keep.
- *"Why not just use the optimiser as the yardstick?"* It knows the whole week in advance, so nothing real can match it. We use it only to scale VCR.

**If you get lost:** "If an AI cannot beat two lines of code, ship the two lines."

### Slide 3. Both pilots lose to a free rule with an AI bill 8 to 12 times their saving; one daily agent's bill is an eighth of what it saves
0:45 · 98 words (budget 98)

**What it shows.**
- Bars per pilot: gross saving vs AI bill. A: €0.60 vs €4.74. C: €0.63 vs €7.71.
- The New framework pair in blue underneath: €1.42 vs €0.18.
- Three causes, taken from the prompts.

**Job in the story.** The complication in money, and why it happens.

**Spoken text.**
> Both pilots lose to the free rule before any AI cost. Then comes the token bill: €4.74 a week for A, €7.71 for C. That is 8 to 12 times what the battery saves. Our agent, in blue, saves €1.42 and spends 18 cents. Three lines in the prompts explain the loss. A fixed 80% target fills the battery by late morning. Export counts as zero, so midday solar sells at 9 cents and comes back at 11 to 12. The sustainability agent never sees a price or CO2. That blind agent is where the carbon money goes.

**Say aloud:** the AI bill is 8 to 12 times the saving.

**Know cold.**
- Ratios (N2): A 4.74 ÷ 0.60 = 7.8. C 7.71 ÷ 0.63 = 12.2. Ours 0.18 ÷ 1.42 = 0.12, about an eighth.
- These bars use the gross saving S (trap 1).
- Pilot AI cost = token counts × Devstral 2 list price ($0.40 in, $2.00 out per million) × 0.86 €/$. A: 11.7M in, 0.42M out.
- Calls: A makes 4.4 LLM calls per 15-minute decision, C makes 7.6. That is 18–29k tokens and 10–18 seconds per decision.
- The daily habit: charge from 05:00, sit at 80% from ~11:00 to 17:00, export at midday, buy back at 20–21h, the dirtiest and dearest hours.
- The pilots export 43–45 kWh a week. We export 17.
- Day by day: C is below the rule on all six full days. A beats it once (9 Jan).

**Likely questions.**
- *"Isn't the 80% target a battery-health choice?"* It is a fixed number in the prompt, `targetStateOfCharge`. The battery's own limits are 10–90%. We size the reserve on tonight's load instead. The cost: our battery sits at its limits 29% of the time (B4 fails), still under 7 cycles a week.
- *"Did the pilots have a forecast?"* They saw 24 hours of simulated data ahead, more than a real forecast gives. They lost anyway, so the issue is the prompts, not foresight.
- *"Would a cheaper model fix the pilots?"* It cuts the bill, not the loss: they lose to the rule before any AI cost. ~730 calls a day also means 730 chances to fail on the control path.
- *"Latency? 10–18 seconds is fine for a 15-minute step."* Agreed. Latency isn't the problem. Cost and failure points are.

**If you get lost:** "They lose before the AI bill, and the bill is 8 to 12 times the saving."

### Slide 4. A second agent buys CO2 at €4,300 a tonne, 48 times the EU carbon price, while a carbon weight inside one agent costs about nothing
0:35 · 76 words (budget 76)

**What it shows.**
- Scatter: x = grid CO2, y = net value after AI (N1).
- Points: A (21.9 kg, −€4.33), C (21.3, −€7.31), free rule hollow (11.9, +€1.03), New framework (12.2, +€0.98).
- Arrow A → C: "+€2.97 AI cost, −0.7 kg".
- Stats: €4,300/t, €90/t EU ETS, ≈ €0/t for a carbon weight.

**Job in the story.** Price the trade-off the brief asks about, then hand to the fix.

**Spoken text.**
> A and C run on the same panels. The second agent adds €2.97 a week of AI bill and avoids 0.7 kilos of CO2. That is €4,300 a tonne, 48 times the EU carbon price. Top left, our framework sits next to the free rule. Inside one agent, a carbon weight cut 0.85 kilos this week at no extra cost. Our carbon figures assume an Italian site. Amir will show you where that one agent lives.

**Say aloud:** €4,300 a tonne, 48 times the EU carbon price.

**Know cold.**
- €2.97 ÷ 0.7 kg = €4.24/kg ≈ €4,300/t. 48 × €90 = €4,320.
- On hourly carbon the second agent still costs about €2,000/t.
- The carbon weight λ: the agent minimises € + λ × kg CO2. Default λ = €0.10/kg (€100/t), a dial the owner sets.
- MAC: λ 0 → 0.10 avoided 0.85 kg and saved about a cent (−€0.011/kg). That is within the gate's noise, so we say "about nothing".
- The framework emits 0.3 kg more than the rule (S2b fails) and earns €0.12 more before AI.
- Italy is our assumption: the data has no location and no CO2 field. Reply is Italian.

**Likely questions.**
- *"Why compare with the EU ETS price?"* It is the market price of a tonne of CO2 in Europe. If avoiding a tonne costs 48 times that, a company does better buying allowances or offsets.
- *"C emits less than A but loses more. How?"* The sustainability agent has no price and no CO2 input. It can only push "import less", which saves 0.7 kg and doubles the calls.
- *"Why does your agent emit more than the rule?"* By 0.3 kg a week, because it keeps some energy for price reasons. Raise λ and it moves closer; λ 0.5 is in the demo.
- *"Average or marginal carbon?"* Average intensity of Italian generation. Imports aren't in the mix. Marginal factors would be a next step (report §10).
- *"Does hourly CO2 change anything?"* It shifts absolute CO2 by ~8%, not the ranking. It shows the pilots buy at hours ~5% dirtier than average.

**If you get lost:** "A second agent pays 48 times the carbon price. A weight inside one agent costs nothing."

## Amir: slides 5–6 and the demo (2:15)

You own the design: the platform, the model choice, the pipeline and the demo. Questions on architecture, Ministral, the validator, fallback and offline go to you.

### Slide 5. We change two things on Reply's platform: a self-hosted Ministral 3 8B replaces the retired LLM, and the LLM leaves the 15-minute loop
0:45 · 96 words (budget 98)

**What it shows.**
- Reply's "Agentic Operations for E&U" platform, redrawn. Blue = our change, dashed = paid option, red = removed.
- Edge: rule + clamp every 15 minutes, fallback to yesterday's plan, then the static rule.
- Central: Ministral 3 8B self-hosted, the validator with a replay gate, the Data Lake as memory.
- Dashed: Ministral 3 3B on the gateway. Red: the external LLM (Devstral 2, retired 31 Jul 2026).

**Job in the story.** Show the fix fits Reply's existing platform. Two boxes change, nothing new to buy.

**Spoken text.**
> Thanks, Sydney. We kept the shape of Reply's platform and changed the blue boxes.
>
> Change one. The pilots called Devstral 2 through an external API, and Mistral retired it in July. We replace it with Ministral 3 8B: open weights, hosted on Reply's servers.
>
> Change two. The model now writes one plan a day. On the gateway, a rule and a safety clamp run the battery every 15 minutes. If the internet drops, the site keeps running on yesterday's plan. Clients who need offline replanning can buy the 3B on the gateway. Here it is running.

**Say aloud:** one call a day instead of about 730.

**Know cold.**
- Unchanged parts: the Data Lake stores telemetry and the memory of past days; the Edge Apps Store ships the edge agent and, for the paid option, the signed 3B weights; the business app shows the owner the plan and reason.
- Why Ministral 3: Apache 2.0 open weights (commercial use allowed), EU origin, same vendor family as Devstral, so porting is easy.
- The bench: 8B wrote 21 of 21 valid plans (3 λ values × 7 days), no clamped knobs, ~27 s a call on an 8 GB laptop at 3-bit. 3B wrote 14 of 14 valid, 12–14 s a call.
- Plans from the 8B, the 3B, a cloud model and "copy the best similar day" land within half a cent this week.
- Devstral's named successor (Mistral Medium 3.5) is itself deprecated, and costs about 10 times Small 4.

**Likely questions.**
- *"Why not Devstral's successor on the API?"* Mistral retired one model mid-project and has already deprecated the successor. With open weights Reply holds the file and decides when to update, through the replay gate.
- *"Does a site need the 3B box to work offline?"*
  - No. Every gateway already runs the rule, the clamp and yesterday's plan.
  - The box adds daily replanning without internet and keeps data on site.
  - It costs €97–422 a site a year, so Reply sells it as a premium.
- *"What if the central model is down for a week?"* Yesterday's valid plan keeps running, then the static rule. The battery is never unmanaged; the worst case is the free rule.
- *"AI Act?"* The model sets three bounded numbers, a validator and a clamp sit between it and the hardware, and every plan comes with a logged reason. EU origin and self-hosting make data residency simple. We have not done a legal classification.
- *"Why an LLM at all, if a rule does the work?"* It writes a plan with a reason the owner can read, reads prices and CO2 for tomorrow, and learns from similar past days without training. If it never beats the memory-only baseline on other seasons, ship the rule and keep the LLM for the explanation.

**If you get lost:** "Two changes: a model Reply owns, and the LLM off the 15-minute loop."

### Slide 6. The agent writes three numbers a day; a validator, a rule and a clamp decide what the battery actually does
0:30 + 1:00 demo · 143 words (budget 195; the rest is silence while the demo plays)

**What it shows.**
- Left to right: Inputs → Agent → Validator → Rule → Clamp → Site, each with a one-phrase role.
- Below: the memory loop, the fallback chain (agent plan → previous valid plan → static rule), and a dashed line of next inputs not built yet.
- The strip of three changes: calls ~730 → 1, export €0 → sell price, 80% target → evening load.

**Job in the story.** Prove the model cannot hurt the battery, then show it working.

**Spoken text.**
> Every morning the agent reads prices, hourly CO2, yesterday's sun and load, and similar past days. It returns three numbers and a reason. The validator checks the format and the ranges, then replays the plan on yesterday. If it costs more than the default plan, we drop it. Every 15 minutes, the rule turns the numbers into kilowatts, and the clamp has the last word. The dashed box lists inputs we would add next.

**[Click 1: switch to the demo, Monday 11:00. 0:15]**
> Here is Monday's plan, with the model's reason.

**[Click 2: similar past days. 0:15]**
> These are the similar days it saw, and what each one left on the table.

**[Click 3: Tuesday, blocked. 0:15]**
> On Tuesday the plan cost half a cent more than the default on the replay. The gate blocked it, and Monday's plan ran.

**[Click 4: KPIs tab. 0:15]**
> On our KPIs, 15 of 20 pass, against 5 and 6 for the pilots. Francesco will tell you what it costs to run.

**Say aloud:** the gate decides, not the model.

**Know cold.**
- The three knobs:
  - `soc_floor`: the lowest charge the rule may use (clamped 10–90%);
  - `evening_reserve_kwh`: energy kept for tonight's evening load, from 17:00;
  - `export_hold_eur`: the price above which the battery keeps energy instead of exporting it.
  - Plus a two-sentence reason. The agent never sets kW.
- The clamp: charge between 10% and 90%, power within ±5 kW.
- The gate on Tuesday (day 2, λ 0.10): plan €0.627 vs default €0.622 on yesterday's replay. Lower is better, so it failed by half a cent.
- At λ 0.10 the gate kept 2 of 7 plans (λ 0: 1 of 7, λ 0.5: 4 of 7).
- Memory: each evening one row is stored (context, knobs, result, regret against the rule). Each morning the agent sees the 3–5 most similar days. The seed is the 14 days of A and C. No training.
- The demo replays committed Ministral 3 8B plans. Nothing runs live. A 60-second recording is the backup.
- KPI tab: the pilots pass 5 (A) and 6 (C); the New framework passes 15 of 20 and fails F1, S2b, S3, B4, C5.

**Likely questions.**
- *"The gate kept only 2 of 7. Does the model add anything?"* See trap 6. This week, no: every plan lands within half a cent. The gate stops a bad plan from costing money. Decision value has to show on other seasons, roadmap step two.
- *"What if the model writes nonsense?"* The validator checks the JSON schema and the ranges first, then the replay. A failed plan never reaches the battery. The 8B wrote 21 of 21 valid plans with no clamped knobs.
- *"Is this live?"* No, it replays the 8B's real plans from our run, so it can't fail on stage. The live model runs once a day and takes ~27 seconds on a laptop.
- *"The slide says rule, the model uses an optimiser."* See trap 5.
- *"Why replay on yesterday and not tomorrow?"* At 11:00 tomorrow hasn't happened. Yesterday is the latest real day we can score both plans on.

**If you get lost:** "The model writes three numbers. The gate, the rule and the clamp decide."

## Francesco: slides 7–8 (1:25)

You own the money and the limits: fleet economics, hosting cost, the upsell, the rollout. Questions on cost, scale, the EU API, the free rule and the roadmap go to you.

### Slide 7. Self-hosting beats the free rule from about 1,500 sites; an on-site model is a paid option for offline sites, not a saving
0:55 · 114 words (budget 119)

**What it shows.**
- Log-log chart: AI cost per site per week against fleet size, 100 to 10,000 sites.
- Red flat lines: pilots A (€4.74) and C (€7.71). Blue falling lines: on-prem 8B and the same model on an EU API. Grey band: the 3B box, flat from €1.86.
- Thresholds: S_net €1.16 (above it AI eats the whole saving) and VORB €0.12 (below it we beat the rule after AI).
- Right panel: the arithmetic behind ~1,500.

**Job in the story.** Turn "self-hosted" into a fleet-size decision and name the upsell.

**Spoken text.**
> The red lines are the pilots: they pay per token, so their bill never falls. Ours does. Before AI cost, we beat the free rule by 12 cents a week per site. On the right is the math. Two GPU servers, their power, and a tenth of an engineer cost about €9,160 a year. Divide by 52 weeks and by the number of sites. At 1,000 sites that is 18 cents, more than our 12-cent lead. From about 1,500 sites it drops below. On an EU API, with the same weights, it happens at 580. The grey band is a box on every site: €97 to €422 a year. Sell it for offline replanning.

**Say aloud:** €9,160 a year, divided by sites, below 12 cents from 1,500.

**Know cold.**
- €9,160 = 2 nodes × (€4,000 ÷ 5 years + 100 W × 8,760 h × €0.32/kWh) + 0.1 FTE at €7,000 = 2 × €1,080 + €7,000.
- €9,160 ÷ 52 = €176 a week. €176 ÷ sites < €0.12 → sites > 1,480.
- Per-site cost at 100 / 1,000 / 10,000 sites: €1.76 / €0.18 / €0.018 on-prem; €0.67 / €0.07 / €0.008 on the EU API.
- N1 > 0 from ~155 sites on-prem. F1 > 0 from ~1,500.
- Operations are three quarters of the cost. If Reply already runs the GPUs and an MLOps team, the cost falls to ~€0.04 a site a week.
- Tokens: ~12k in and 1.1–1.3k out per site per week, at one call a day.
- The 3B box: €1.86–8.12 a week = €97–422 a year, against a gain of ~€51 a year. So it is a paid option, priced at or above cost.

**Likely questions.**
- *"The EU API is cheaper. Why self-host?"*
  - At 1,000 sites the API costs about 11 cents less a week.
  - Self-hosting buys control: Reply holds the weights, no vendor can retire the model as happened with Devstral 2, and data stays on Reply's platform.
  - Start on the API and move in-house. Same model, same prompt, so the switch is a config change.
- *"Where does the hosting cost come from?"*
  - Our estimate: a €4,000 GPU node pair, 100 W, 0.1 FTE of operations, 5 years of life.
  - Operations are three quarters of it. Sense Reply should confirm the FTE and power price.
- *"Does Sense Reply have 1,500 sites?"* We don't know their fleet. Below ~1,000 sites, the EU API clears the rule from ~580. That's why the rollout starts on the API.
- *"Why would a client pay for the box?"* Sites that must replan without internet, or must keep data on site. Every other site already runs offline on rule, clamp and yesterday's plan.
- *"Why log-log?"* Fleet size spans two orders of magnitude and cost falls as 1/sites, so the falling lines show as straight lines.

**If you get lost:** "The pilots' bill is flat. Ours divides by the fleet and drops below 12 cents from 1,500 sites."

### Slide 8. One modelled winter week supports a staged rollout, gated on a summer replay before any promise to a client
0:30 · 61 words (budget 65)

**What it shows.**
- Limits: one modelled winter week with PV that is not real weather; no CO2 field and no agent proposal logs; runs that start with different panel dirt; the hosting cost is an estimate.
- Rollout in five phases, each with a gate.

**Job in the story.** Say the limits before the jury does, and end on a plan.

**Spoken text.**
> All of this rests on one modelled winter week, with no real weather and no agent logs. Run B started with dustier panels, so we left it out. Our hosting cost is an estimate. So we roll out in steps: fix the baseline, replay summer, then pilot sites on an API, then in-house at scale. Thank you, we welcome your questions.

**Say aloud:** a summer replay comes first.

**Know cold.** The five phases and their gates (report §9):

| Phase | When | Gate to pass |
|---|---|---|
| 0. Fix the baseline: rule and no-battery twins as standard KPIs, log proposals, drop the 80% target | Weeks 1–2 | Rule reproduced within 1% |
| 1. Prove decision value: replay summer, spring, price and CO2 spikes | Weeks 3–6 | Beats the memory-only baseline and the rule on one season; N2 < 0.2 |
| 2. Carbon desk: hourly ENTSO-E feed in production, calibrate λ with the client | Weeks 5–8 | Carbon cost per tonne below the EU price |
| 3. Pilot sites on an EU API, owner sees plan and reason | Months 3–5 | Clamp and override rates below agreed limits |
| 4. In-house at ~1,000 sites, offer the 3B option | Month 6 on | Unit economics confirmed on a full year |

- The simulated PV peaks at 10:00 with ~14 hours of sun in January. Real Italian January weather looks nothing like that.
- The modelled week uses a persistence forecast, so it is probably optimistic.
- Panel dirt (`pv_dirt`): A starts at 3%, B at 26%. Both grow about 2.4 points a day and nobody cleans them. B makes 69.1 kWh of solar against A's 93.1, 25.8% less. The sun is the same in every run: PV = clean PV × (1 − dirt), so the gap is only dust. C copies A's dirt (93.06 vs 93.13 kWh), which is why A vs C is the fair test.

**Likely questions.**
- *"One winter week only?"*
  - Yes, and this slide says so.
  - C loses to the rule on all six full days, so the direction looks solid.
  - Summer brings more PV and a smaller evening need, so we rerun before any promise.
- *"What would change your recommendation?"* If the model never beats the memory-only baseline on another season, ship the rule with the daily plan logic and keep the LLM for the owner's explanation.
- *"F1 is negative. Why not ship the free rule today?"*
  - The rule is our fallback, and Reply could ship it tomorrow.
  - The agent adds a CO2 dial, a daily plan with a reason, and memory.
  - The gap is 6 cents a week, and it closes from ~1,500 sites.
- *"Why is run B left out?"* B's panels start dirtier, so it gets 24 kWh less PV, and one sample is missing. C has A's panel dirt, so A against C isolates the second agent. (Sydney can take this one.)

**If you get lost:** "One winter week, so summer comes before any promise."

---

## Word counts

| Speaker | Slides | Words | Budget at 130 wpm |
|---|---|---|---|
| Sydney | 0–4 | 364 | 369 (2:50) |
| Amir | 5–6 | 239 | 293 (2:15) |
| Francesco | 7–8 | 175 | 184 (1:25) |
| Total | | 778 | 846 (6:30) |

## Questions for any of us

Whoever is closest answers; the owner adds detail.

- **"Why Italy?"** (Sydney) The data has no location. Reply is Italian, so we assumed Italy and used Italian ENTSO-E data. Every CO2 figure carries that flag.
- **"How good is the data?"** (Sydney) The `cost` field is not a running total despite the data model, the `load` field is ~2% off the energy balance, and there is no CO2 field. We rebuilt bill and load from energy flows and checked each correction (report §4, §10).
- **"Why not fine-tune or use reinforcement learning?"** (Amir) The client chose prompt agents for speed and wants learning. Memory of similar days gives learning with no training. Fine-tuning (LoRA) is on the list for later, once there are logs to train on.
- **"What did you get wrong along the way?"** (Francesco) We dropped a grid-charging mode that raised CO2 and the peak, cut a wear cost 20 times too high, and repriced the AI after Devstral 2 was retired (report §10).
- **"What would you do with another month?"** (Francesco) Phase 1: replay a summer and a spike week, and run the 8B at full quality on a server.
