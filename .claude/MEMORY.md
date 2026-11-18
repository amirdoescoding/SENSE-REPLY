# Memory: key facts & decisions

## Dataset (verified 2026-11-06)
- dataset-001 = **Orchestrator + Cost**: 2,948 LLM requests, 11,690,688 input / 418,362 output tokens, mean LLM time 2,355 ms.
- dataset-002 = **Orchestrator + Cost + Sustainability**: 5,472 requests, 20,049,658 input / 770,858 output tokens, 2,486 ms.
- Both use the same model, Devstral 2 123B (Mistral, cloud API, called from the edge gateway).
- Same window: 2026-01-05 11:00 → 2026-01-12 10:45, 15-min samples. 001 = 672 samples; **002 = 671 (one missing)**.
- Samples are ordered newest first, so sort by `datetime`. Grid `cost` and `penalty` are cumulative, so take diffs.
- BESS: 10 kWh, SoC 0.1–0.9, η_charge = η_discharge = 0.95. Site: 9 PV panels, 1 load, 1 grid connection.
- **No emissions/carbon field.** Sustainability KPIs need an external carbon-intensity series.

## Assumptions
- Site location is not stated. Assume Italy (Reply is Italian) and flag it in every deliverable.

## Decisions
- Research outputs go in `docs/research/0N-*.md`. `00-synthesis.md` is the entry point.
- Work happens on branch `research/agent-assessment`, one commit per research report.

## Data checks (2026-11-06), see docs/research/00-synthesis.md
- The `cost` field is NOT cumulative, despite DATA_MODEL.pdf (range −0.003..0.009 €). Recompute the bill as Σ(import·buyPrice − export·sellPrice).
- Prices are time-varying (134 distinct buyPrice values, €0.035–0.132) and identical in both datasets. Violations, throttling and penalty are all 0 in both.
- **The runs are not controlled.** PV is 93.1 kWh (A) vs 69.1 kWh (B), and SoC start is 0.57 (A) vs 0.15 (B). Compare via baselines on each run's own PV/load, plus a terminal-SoC correction.
- Raw bills: A ≈ €3.23, B ≈ €5.15. LLM cost at $0.40/$2.00 per M tokens: A ≈ $5.51/wk, B ≈ $9.56/wk (+73%).

## Decisions
- KPI catalogue = synthesis §2. Baselines: no-battery, rule-based self-consumption, perfect-foresight LP.

## KPI work (2026-11-08), see docs/KPIS.md, docs/FRAMEWORK.md
- `analysis/kpis.py` (stdlib) asserts it reproduces synthesis §1 before printing. Rule baseline derives power limits from its own SoC: data follows maxCharge = min(5, (0.9−SoC)·10), fits within 0.08 kW.
- Headline (robust): LLM cost ≈ 7× (A) / 11× (B) the savings vs no battery (~€0.7/wk). Gap to rule baseline is small (€0.40–0.70/wk) and flips for A once wear (c_deg €0.10) is counted, so present it as a sensitivity.
- B vs A, each vs own rule baseline: B €0.30 cheaper, 2.9 kg CO2 cleaner. Total cost of sustainability ≈ €3.3/wk, almost all LLM.
- PV gap partly soiling: `pv_dirt` 0.20 (A) vs 0.42 (B). PV profile peaks 10:00 and runs ~14 h/day: not Italian January. Flag it.
- Carbon: hourly ENTSO-E A75 actual generation for Italy (10YIT-GRTN-----B) from the API, UTC → Europe/Rome. CSVs deleted 2026-11-09 (API parity 0.0 g/kWh on 216 h). CI 214–439, mean 362 g/kWh (IPCC lifecycle EFs). Fallback static = ISPRA 2024 prelim. 198.9 g/kWh (Rapporti 413/2025 Tab. 1.3).
- Both configs import at hours ~5% dirtier than grid mean (372.5 vs 355.5 g/kWh); B no better than A, so the sustainability agent has no real carbon timing. B vs A baseline-relative: 5.5 kg CO2 less.
- ENTSO-E API token arrived 2026-11-09: `ENTSO_API` in `.env` (gitignored). No token means the static fallback, so CO2 KPIs change. Each teammate needs their own token.
- Devstral 2 retired 2026-07-31 (replacement Mistral Medium 3.5, ~10× Small 4 price). Revolut self-hosts GLM for coding; no "millions" figure found.
- Redesign decision: optimiser sets kW on the edge, 1 strategy LLM every 1–4 h, twin-scored arbiter, clamp, rule floor; sustainability = λ weight, not an agent.
- Web diagram: https://claude.ai/artifact/ENAndsWgSqt9YYqYxMuY9W

## Supervised learning check (2026-11-08), see FRAMEWORK.md §7b, analysis/forecast_check.py
- Simulator fact: PV = clean PV × (1 − pv_dirt) exactly; A and B had the SAME weather. PV gap is only dirt (B starts 0.26 vs A 0.03, both +0.024/day, never cleaned; 10–30× faster than field data).
- Evening peak 17–22h is ~10.5 kWh every day (naive error 1–4%): hoarding is a decision problem. A leaves 7.3 kWh at sunrise/week = €0.79 recoverable.
- CO2 naive day-ahead error 8.7%; dirtiest hour 20:00 = price peak, cleanest 12:00: cost and CO2 aligned this week.
- Team scope for supervised learning: load, CO2, soiling/faults (not PV-from-weather). User commits themselves now.

## ENTSO-E API + CO2 forecast (2026-11-09), branch `entsoe-api`
- API quirks: errors come back as HTTP 200 `Acknowledgement_MarketDocument`. A03 curves skip repeated points (forward-fill to period end). A75 pumped/storage consumption series use `outBiddingZone_Domain` (skip them). A65 load uses `outBiddingZone_Domain`. ElementTree `iter()` ignores `{*}`, so use `iterfind`.
- CO2 forecast test (FRAMEWORK §7b): CI_{t−24} + a + b·Δ(1 − wind+solar DA / load DA), trained 1 Dec–4 Jan. Error 8.7% → 5.2%, **FC2 0.40**, ~56 g/kWh per +0.1 residual share, corr 0.89. One test week, holidays in training: indicative.

## DatasetV4 + proposal (2026-11-17), branch `dataset-v4`, see docs/PROPOSAL.md, KPIS.md, TIMESERIES.md
- V4 moved to `data/DatasetV4/`. 001/002 byte-identical to V3. **dataset-003 = C** = Orch+Cost+Sust with A's panel dirt: 5,118 req, 18.79M/0.72M tokens, 2,384 ms. Plus `Prompts/` and `Assets/` (BSS.json, PV.json).
- **C vs A is the main comparison.** SoC still differs: A 0.57→0.80, C 0.80→0.70. Use the SoC-adjusted bill and compare each run vs its own rule. Result (all SoC-adjusted, from 2026-11-17 fix): −€0.02 energy, −1.5 kg CO2, −3.8 kWh import, +€2.97 LLM, so ≈ €2,000/t CO2 incl. LLM. B vs A: −5.0 kg, €640/t.
- Replay (`analysis/replay.py`): in this January week, the plain rule beats every knob. A 20% reserve costs +€0.12/wk; a night grid charge costs +€0.13–0.22/wk and adds 5–10 kg CO2. So the replay gate is essential, and the LLM must win on other weeks to earn its place.
- Peak import: A's 4.95 kW is one sample. Use P99 (A 3.1, C 2.5 kW).
- Wear comes from BSS.json: €100/kWh × 0.005%/EFC, so C_DEG = €0.005/kWh discharged (telemetry ΔSoH/EFC = 5e-5). The old €0.10 was 20× too high; "A beats rule with wear" is dead.
- **Prompts explain the behaviour:**
  - `targetStateOfCharge` 80% causes hoarding: SoC ~0.8 for 31% of the time in A/C.
  - Both prompts value export at 0.
  - The Sust. prompt has no price and no CO2 input; it only minimises import kWh.
- Hourly habit: fills to 80% by 11:00 (partly from the grid at morning prices) → exports ~4 kWh/day at midday → dumps 18–19h with ~1.4 kWh/day exported → imports at 20–21h (dirtiest hours). Agents lose to the rule every day.
- Decision: the old FRAMEWORK.md is superseded (user: "forget it"). The new design is in PROPOSAL.md:
  - one merged agent, € + λ·CO2, with λ as an owner dial;
  - daily knobs (reserve kWh, grid-charge window, discharge priority) executed by a rule, plus a clamp;
  - k-NN memory of low-regret days, with no training;
  - LoRA, forecasts and an optimiser kept as "later".
- Client feedback: they like the carbon data; they want self-hosting plus learning; they are sceptical of anything slow to build (they chose 2 prompt agents for speed).
- Self-hosting: after the call cut (~180–540× fewer tokens), an EU API costs ~€2–9/site/yr vs a Jetson at ~€90/site/yr. Argue for self-hosting on residency, offline operation and model churn, not cost. Medium 3.5 is deprecated (→ Large 4). See research/07.
- User wants work split into commits (one per logical step).

## Demo (2026-11-18), see .claude/TODOS.md, docs/DESIGN.md
- Building a hosted demo of the PROPOSAL framework. Plan: 5 sessions, one branch each (design → sim-engine → api → ui-sim → ui-kpis). The user wants **one session at a time**, never all at once.
- Decisions:
  - precompute + playback;
  - memory seeded with A + C days;
  - A's week + ENTSO-E, plus a live ENTSO-E pull;
  - λ {0, 0.10, 0.50};
  - compare against A, C, no battery (rule baseline not shown);
  - Gemini Flash free tier as the Devstral stand-in (`GEMINI_API_KEY`);
  - FastAPI + Vite/React on Render;
  - three.js isometric site.
- Brand: Reply CSS palette (ink #151F27, blue #3A7DDA), fonts Instrument Sans + JetBrains Mono. The look follows MAGO (Reply's energy platform, see the photos in assets/images).
- Mockups render via `docs/mockups/render.sh` (Playwright's cached headless Chromium; no PIL).
- Chosen layout: mock-1 (MAGO classic) + KPI tab, after the de-slop pass (no eyebrow caps, no pills, no glow, one KPI strip). Skills impeccable + design-taste-frontend are installed in the project; impeccable adds hooks in settings.local.json.
- **Final KPI source of truth:** `data/Sense_Reply_B2_KPI_Conformity.xlsx` + `docs/Sense Reply BDD B2 – Full Analysis Report.docx` (teammate Sofia, 2026-11-18). Headline KPIs: S_net, VCR, VORB, N1, N2, F1, O5, S2b, MAC, SCR, SSR, PSR, B4, C5, O1, with verdicts vs editable thresholds.
- Report basis differs from our older docs:
  - S5 on **run C inputs, start SoC 0.80**;
  - carbon constant **0.356 kg/kWh** (hourly is only a check);
  - token price 0.86 €/$;
  - S5 conservative N1 +1.10 €/wk, upside +1.78 (grid charging, CO2 22.2 kg, peak 5.1 kW → shadow mode).
  The demo follows the report.
- Report §11 "Scenario Lab" = our demo: JSON plan schema, guardrails, download.

## Sim engine (2026-11-18), branch `demo-sim-engine`, see demo/sim.py, demo/agent.py
- **Workbook alignment:** load = PV + I − X + E_dis − E_chg (balance) reproduces the Excel exactly; the raw `load` field is ~2% off.
  - Pilot VORB uses the pilot's own rule twin (A: own inputs, SoC 0.572).
  - S2b uses the run-C rule CO2 for every column (a workbook quirk, mirrored).
  - S* = S/VCR = 2.184. A whole-week perfect-foresight LP with grid charging gives 2.1844.
- **Executor:** rolling LP every 15 min, 24 h persistence forecast, known prices.
  - Knobs (§11.2): soc_floor, evening_reserve_kwh at 17:00 (soft), export_hold_eur (terminal €/kWh), grid_charge (upside only).
  - Default knobs = plain S5: export_hold = mean_buy, with no extra η, since C_adj already has it.
- **Perfect-foresight LPs can't value knobs** (constraints only hurt). So the memory seed and the replay gate use the rolling MPC.
- Results (memory fallback, no Gemini):
  - Ours conservative λ0.1: S_net 1.156, VORB +0.114, 16 Good (= S5 conservative).
  - Upside λ0.1: S_net 1.568, VORB +0.53, 14 Good.
  - Knob regret vs the rule is only ±1 cent/day in this week.
- **Gemini:** model `gemini-3.8-flash`, with frequent 503 "high demand". The free-tier quota was exhausted on 2026-11-18 (429), so `agent.ask` stops calling for the rest of the run once it sees a 429.
