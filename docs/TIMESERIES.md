# Time-series analysis: how the agents behave hour by hour

Numbers come from `python3 analysis/timeseries.py`. A = Cost agent. B and C = Cost + Sustainability agents. C has the same panels as A. Week: 5–12 Jan 2026.

## 1. A typical day (mean of each hour over the week, A and C are almost identical)

| Time | What happens | Price €/kWh | Grid CO2 g/kWh |
|---|---|---|---|
| 22:00–04:00 | Battery idle at its floor (A ~20%, C ~12%). House imports a little. | 0.074–0.105 | 358–371 |
| 05:00–10:00 | Battery charges at +0.5 to +1.7 kW from early sun **and some grid** (0.04–0.08 kWh imported per 15 min) | **0.084–0.113 (morning high)** | 356–377 |
| 10:00–11:00 | Battery reaches **80%**, the `targetStateOfCharge` in `BSS.json` | 0.10 | 313–321 |
| 11:00–15:00 | Battery **sits full at 80%**. All midday sun is exported, about 4 kWh a day at ~€0.09. | 0.097–0.104 | **308–326 (cleanest)** |
| 18:00–19:00 | Battery dumps fast (−1.3 then −2.8 kW), more than the house needs, so **~1.4 kWh a day goes to the grid** | **0.119–0.120 (peak)** | 373 |
| 20:00–21:00 | Battery is back near its floor. House **imports 0.5–0.6 kWh per 15 min** | 0.109–0.113 | **376–378 (dirtiest)** |

**Three habits cost money and CO2:**
1. **It fills too early, and from the grid.** The morning charge reaches 80% by 11:00, so the bigger midday surplus has nowhere to go. The Sustainability prompt even says "avoid filling the BESS early if a larger PV surplus is expected later", yet C still does it.
2. **It hoards at 80% and exports the surplus.** The battery spends ~31% of the week near 0.8 (A and C), and only 14% in B, whose dirtier panels rarely reach it.
   - Both prompts call leftover surplus "not valued", so the agents see no loss in exporting it.
   - Meanwhile the evening is fed from the grid.
3. **It discharges too fast at 18–19h, then runs dry at 20–21h.** About 10.5 kWh a week leaves the battery as export (A 10.5, B 10.1, C 10.8). That energy could have covered the 20–21h imports, at the dirtiest hours.
   - A also stops at ~20% SoC instead of the 10% minimum, leaving ~1 kWh unused each night.

**Price and CO2 point the same way this week.** The cheap and clean hour is midday, and the dear and dirty hours are 18–21h. So a cost-only agent that fixed these habits would cut CO2 too. That is why adding a sustainability agent changes so little.

## 2. Day by day
Agent minus its own rule baseline, € corrected for the battery-level gap:

| Day | A excess € | C excess € | A excess CO2 | C excess CO2 |
|---|---|---|---|---|
| Mon 5 (from 11:00) | +0.09 | +0.10 | +1.5 kg | +1.2 kg |
| Tue 6 | +0.10 | +0.09 | +1.9 kg | +1.5 kg |
| Wed 7 | +0.09 | +0.10 | +1.7 kg | +1.7 kg |
| Thu 8 | +0.14 | +0.12 | +2.2 kg | +1.5 kg |
| Fri 9 | +0.10 | +0.06 | +1.5 kg | +1.4 kg |
| Sat 10 | +0.06 | +0.09 | +1.3 kg | +1.2 kg |
| Sun 11 | +0.07 | +0.08 | +1.6 kg | +1.3 kg |
| Mon 12 (to 10:45) | +0.04 | +0.04 | +0.4 kg | +0.5 kg |

- **Both agents lose to the rule every single day.** The loss is steady at about €0.06–0.14 and 1.2–2.2 kg CO2 a day, so this is a habit, not bad luck.
- **Weekday vs weekend:** no clear difference. The simulated load is about 15 kWh every full day.
- **Sunnier vs duller days:** PV ranges only 12.5–14.1 kWh per full day, so the split is weak. Agents lose a bit more on sunnier days (more surplus exported). See the trade-off matrix in `KPIS.md` §2.

## 3. Grid interaction

| | A | B | C |
|---|---|---|---|
| Import | 63.8 kWh | 60.5 kWh | 58.7 kWh |
| Export | 45.1 kWh | 17.6 kWh | 42.9 kWh |
| Peak import | 4.95 kW | 3.93 kW | **2.83 kW** |
| Violations / penalties / grid outages / BESS throttling or faults | 0 | 0 | 0 |

- The grid contract is never stressed, so penalty exposure and resilience cannot be told apart this week.
- C's lower peak is the one grid benefit we can see from the two-agent setup.

## 4. Coordination patterns (what we can infer without logs)

| | A | B | C |
|---|---|---|---|
| LLM calls per 15-min decision | 4.4 | 8.2 | 7.6 |
| Input tokens per decision | 17k | 30k | 28k |
| Decision time (upper bound) | 10 s | 20 s | 18 s |
| Charge/discharge switches per day | 2.0 | 2.0 | 2.0 |
| Mean power change between steps | 0.15 kW | 0.11 kW | 0.12 kW |

- **The second agent almost doubles the calls but not the behaviour.** The daily pattern (§1) is the same shape in A and C.
- **Its only visible effects are slightly smoother power and a softer evening peak.**
- We cannot see who proposed what or why the orchestrator picked it. The proposal logs are not in the data.

## 5. Anomalies and data notes
- **B is missing one sample** (2026-01-09 20:00). It can be recovered from the cumulative totals. B is secondary now, so we leave it at 671 samples.
- **The energy balance closes to within 0.05 / 0.35 / 0.62 kWh a week (A / B / C).** `load` is a spot kW reading × 0.25 h, so small gaps are expected.
- **Asset file quirks** (`Assets/BSS.json`):
  - `dischargeEfficiency` is written as "0.95 %", while charge is "95 %".
  - Battery health starts lower in each run (A 0.9998, B 0.9995, C 0.9992). The runs look sequential on the same simulated battery.
- **The simulator dirt rate is very high.** `Assets/PV.json` sets a base dirt rate of 0.001 per hour (2.4%/day), with no rain this week. That is 10–30× faster than field data.
- **The PV clock is odd.** It peaks at 10:00 and runs ~14 h a day in January, which is not an Italian winter. Hourly CO2 alignment is approximate.
