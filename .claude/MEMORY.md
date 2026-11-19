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
- **Gemini:**
  - Model: `gemini-3.5-flash-lite` (500 requests/day). The 3.8 and 3.6 Flash free tiers allow only 20/day, and a full run needs 42 calls.
  - The thought summary needs `thinkingBudget: 2048`.
  - 503 "high demand" is frequent: retries handle it. On a 429, the rest of the run uses memory.
  - "Live API" models (unlimited requests) are WebSocket voice/streaming models, not used.
- **With Gemini (7/7 days):** the knobs stay near the defaults (one reserve of 2 kWh). The KPIs equal the memory-fallback run. O5 = €0.0115/wk (Excel S5: 0.0113). Ours conservative λ0.1: N1 1.145, 16 Good.

## Demo API (2026-11-18), branch `demo-api`, see demo/api.py
- FastAPI over precomputed `demo/out`, no live LLM on the server (no Gemini key on Render). Agents (llm-architect) agreed: free instance sleeps, Gemini 503s, shared quota.
- Live carbon reuses `analysis/carbon.hourly_ci`; keys are Italian local hours. Only type names are logged (token is in the URL).
- 5 gate blocks across the 6 runs fell back to "previous valid plan"; every day's source is gemini.
- Open for session 4: price + comparison series missing from run rows; `kpis.json` carbon_source label wrong (see TODOS).

## Demo UI sim (2026-11-18), branch `demo-ui-sim`, see demo/web, .logs/2026-11/18/demo-ui-sim.md
- Stack: Vite + React (plain JS) + `three`, with @fontsource fonts. The dev proxy sends `/api` to :8000. `npm run build` writes `demo/web/dist`, which api.py serves.
- URL params `?mode=&lambda=&step=&play=1`. Passing `step` pauses autoplay. Use them for demo jumps and screenshots.
- The sky is a card backdrop driven by the data's PV:
  - the sun and moon arc positions come from each day's first and last PV>0 step, about 03:15–17:30 in this data;
  - dusk is about 17:15, not 18:30.
- The UI's days are plan windows (11:00 → 10:45), so the chips are labelled "Plan".
- Gate compares against the **default knobs** (plain S5 MPC), not the static rule. Label it that way.
- The regret on each similar past day is always scored at λ 0.10.
- `--mute` is now #66727E (WCAG AA). DESIGN.md is updated.
- Headless screenshots need `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader --enable-logging=stderr --v=0`. Without the logging flag the shot fires before the data loads.
- Subagents cannot load skills: run the design-skill passes in the main session.

## Demo UI KPIs (2026-11-18), branch `demo-ui-kpis`, see demo/web/src/Kpis.jsx
- `kpis.json` now has `meta` {id: name, unit, group}, from `sim.py` META (workbook "KPI Verdicts", columns B–D). Regenerating the outputs changed only `kpis.json` (Gemini cache hits).
- Mode and λ live in App, so the KPIs tab's "Ours" column is the same run as the Sim tab.
- F5/P4 are computed client-side from run `days`:
  - F5 = days with `used` ≠ plan;
  - P4 = plans with an "invalid" or "clamped" validator note, and plans with an explanation.
- Counts = Good / (Good + Improvable). Ours shows /20 because S3 is assessed (hourly CI).
- Space toggles playback unless a control has *keyboard* focus (`:focus-visible`). On the KPIs tab, Space scrolls the page.
- Pipeline label font = 14px × k, where k = clamp(1400/width, 1, 1.7). Width 0 on a hidden tab is ignored.

## Demo polish (2026-11-19), branch `demo-polish`, see demo/web/src/DayChart.jsx
- Upside grid charging has its own pylon→battery path: gc = max(0, battery_kw − PV surplus to battery); grid path = grid_kw − gc. Conservative gc ≤ 0.001 kW (below the 0.02 draw cutoff).
- Memory→Agent packet fires at plan offset 36 (20:00); at 16× it still lands 30 ms before the 11:00 decision.
- Day chart lives in the agent panel (user choice). Two panels (SoC, buy price) on one time axis, never a dual axis. Pilot C = ink, static rule = dashed mute: the DESIGN.md pilot/rule greys fail the dataviz normal-vision check (ΔE 13 < 15).
- KPI strip shows "+x vs C" (ours − pilot C) under a "Week result" heading. User declined renaming the baselines.
- Craft floor: no unicode glyphs as icons (blocked day = red ring, not ✕).
- Next session: live Gemini test; roll back to precompute + playback if it performs badly.

## Session 7 (2026-11-19): pipeline cue + live week, branches `demo-pipeline-cue` (PR #11) and `demo-live`
- **Cue** (mockup `docs/mockups/mock-cue.png`, the user picked c2):
  - The working stage is enlarged 1.18× (rect + icon; the label stays put) and filled.
  - Agent, Validator and Memory cues ride the packet WAAPI.
  - The executor is a WAAPI loop Rule → Clamp → Site every 1.8 s. It is not per step, since a step is ~50 ms at 4×.
  - Reduced motion: fill only.
  - Gotcha: the class `.tick` already exists (panel checkmarks). A CSS loop removed at packet boundaries snaps nodes back.
- **Live** (`/api/live`, SSE):
  - `agent.ask(live=True)` bypasses `gemini_cache.json`. Otherwise every "live" answer is replayed from the cache, because the prompts are deterministic.
  - The week streams day by day over the precomputed run (same inputs), and playback waits at the frontier.
- **Decision reversed:** `GEMINI_API_KEY` now goes on Render (live mode). Guards:
  - `DEMO_PASSCODE` Basic auth on the whole site except `/healthz`;
  - one run at a time (owner token + 10-min event heartbeat);
  - `LIVE_CAP` = 10 runs/day;
  - Sec-Fetch-Site check.
- **SSE gotcha:** a sync generator in `StreamingResponse` is never closed when the client leaves, so the worker kept calling Gemini. Use an async generator plus `anyio.to_thread.run_sync(q.get, abandon_on_cancel=True)`.
- **Local measurement:** a live week takes 51–68 s.
  - Gemini 5–16 s/day; the gate + MPC ~1.2 s/day.
  - 7/7 plans from Gemini; one 503 retried.
  - The live KPIs equal the precomputed ones (same knobs).
- **Render free measurement (2026-11-19, upside λ0.1, run 1 of 3):** a live week took 2 min 44 s, 7/7 from Gemini. Passes (< 3 min, ≥ 5/7).
  - Per day: Gemini 0.7–6.7 s, gate ~8.5 s (15.6 cold), sim ~7 s. The CPU is ~12× slower than the laptop, so compute is the bottleneck, not Gemini.
  - Starter would cut it to ~1 min if needed.
  - An existing Render service kept the old health check path (`/api/kpis` → 401 behind the passcode): set it to `/healthz` in Settings or Sync the Blueprint.
- **ENTSO-E** API timed out on 2026-11-19, so `demo/out` was not regenerated. Equivalence was checked old vs new `run_ours` instead.
- **Live memory (2026-11-19):** in live runs, finished days join the k-NN pool (14 A/C days + this run). Regret is scored like the seed: day-alone MPC at λ 0.10. Slicing the continuous run gave a +0.07 € bias.
  - Prompt tag: "earlier day of this run". Costs +1 day-MPC per day (~7 s on Render).
  - Second Render run (conservative): 4 min 31 s, 7/7 Gemini, one 503 (77 s day). The user accepted this time.
  - Weather API: deferred. The sim's PV isn't real weather; it belongs in the deck/proposal or a future real-dates "plan tomorrow" mode.
- Third Render run (conservative, with memory): 5 min 23 s, 7/7 Gemini, 3 × 503. The user accepted the free tier and wants to merge `demo-live` after PR #11. The live URL is behind the passcode.
- ENTSO-E returned HTTP 599 all of 2026-11-19, so `sim.py --check` stops after check 1. That needs a static fallback (backlog).

## Report + KPIs on Ministral, 3 scenarios (2026-11-19), branch `report-ministral`
- **User decision: only three scenarios everywhere:** Pilot A (cost), Pilot C (cost + sust.), **New framework** (= "self-hosted single agent"; user renamed it from "Ours" 2026-11-19, use this label in demo and deck too).
  - Removed: conservative/upside/shadow/S5 wording, Pilot B (one footnote), and the static-rule column. The rule stays only as the yardstick in VORB/F1/S2b and the threshold notes.
- **Ours basis:** our sim's conservative run, λ 0.10 (`demo/out`, S_net 1.1561), with AI cost from Ministral 3 8B self-hosted centrally at 1,000 sites: O5 €0.1762 (`analysis/model_cost.py`). Gives N1 +0.98, N2 0.12, **F1 −0.06** (loses to the free rule after AI cost; positive at 10k sites or on an EU API), grid CO2 12.16 kg, peak 3.38 kW. 15 Good / 5 Improvable (F1, S2b, S3, B4, C5); A 5, C 6. Values in `data/ours_ministral.json`.
- **Ministral 3 3B on the gateway = paid option** (offline / data stays on site), not in the headline (€1.86/site/wk → N1 −0.71).
- **Carbon weight MAC** (λ 0 → 0.10) ≈ €17/t (was €31–72 on Sofia's S5).
- **Report source** is now `docs/REPORT.md`; the docx is built with pandoc, using the old docx as `--reference-doc`. Charts: `analysis/report_charts.py` → `docs/report/`. Diagram: `docs/diagrams/reply-platform.html` + `render.sh`.
- LibreOffice is NOT installed (the `/opt/homebrew/bin/soffice` shim points to a missing app). openpyxl lives only in `/opt/anaconda3/bin/python`.
- The deck, PRESENTATION.md and the demo still show the old S5 numbers (N1 1.10/1.15, AI €0.01). Fix them in the next sessions.

## Demo on Ministral 3 8B, replay only (2026-11-19), branch `demo-ministral-replay`
- **Live mode and Gemini are gone** (user: "forget about the live"). The server only replays committed plans: `run_{0.0,0.1,0.5}.json` + `model_cache.json`. `/api/run?lambda=` (no mode). Render secrets: ENTSO_API, DEMO_PASSCODE only.
- `agent.ask` calls llama-server (`LLAMA_URL`, default :8080), cache keyed by sha256(MODEL + prompt). `python demo/sim.py` regenerates everything; `local_bench.py` reuses `agent.ask` with its own `bench_cache.json` (gitignored).
- **The 8B ran on the M1 8 GB:** unsloth `Ministral-3-8B-Instruct-2512-Q3_K_S.gguf` (3.9 GB, ~/models), `-c 3072 -np 1 -ctk q8_0 -ctv q8_0 -fa on`, with Dia closed and VS Code open. Pressure stayed at "warning" (level 2), never critical. ~27 s/call (prefill 90 tok/s, decode 9 tok/s), prompts ~850–1,700 tokens. 21/21 valid JSON, 0 clamps.
- New framework (λ 0.10): S_net 1.1586, VORB +0.119, N1 +0.98, F1 −0.057, S1 12.16 kg, peak G1 2.20 kW (was 3.38, now below pilot C), PSR 0.54, 15/20 Good. The gate kept only 2/7 plans (λ 0: 1/7, λ 0.5: 4/7). MAC λ0→0.10 = −€0.011/kg (cheaper AND cleaner; within gate noise, report says "≈ free"). F1 > 0 from ~1,500 sites (central option).
- KPI columns: A, C, `New framework λ=x`. The static rule stays in sim.EXCEL only as the yardstick and for check 1b; S5 columns, `check_lp` and `run_perfect` are deleted.
- Report FINAL.docx is a pure pandoc build of REPORT.md (verified identical text), so rebuild it: `cd docs && pandoc REPORT.md --resource-path=. --reference-doc="…FINAL.docx" -o "…FINAL.docx"`. Charts need `/opt/anaconda3/bin/python analysis/report_charts.py` (matplotlib).
- Headless screenshots: the old swiftshader recipe now fails (WebGL off, shot before data). Use Playwright from the npx cache with `--use-angle=metal` and `waitForSelector('.panel')` (script in the session log).
