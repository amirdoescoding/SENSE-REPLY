# Demo TODOs: framework simulation

One session = one feature = one branch, split into commits. Mockups come before any front-end code.
Close each session with: memory files + `graphify update .`.

## Agreed decisions (2026-11-18, aligned with the final KPI docs)
- **Source of truth for KPIs:**
  - `data/Sense_Reply_B2_KPI_Conformity.xlsx` (IDs, formulas, thresholds, verdicts);
  - `docs/Sense Reply BDD B2 – Full Analysis Report.docx` (§4 formulas, §6 scenarios, §11 Scenario Lab + JSON schema).
- **Inputs:**
  - run C's sun, load and prices, start SoC 0.80 (the report's S5 basis). This supersedes "A's week".
  - Carbon = constant 0.356 kg/kWh (workbook basis) for the KPIs. Hourly ENTSO-E is shown as a check and as the live card, with fallback to the constant and the source shown on screen.
- **Modes:** conservative (no grid charging) and upside (grid charging, "shadow"). λ ∈ {0, 0.10, 0.50} €/kg, precomputed; MAC uses 0 → 0.10.
- **Comparison columns** (Excel): A, C, Static rule, S5 conservative, S5 upside, plus **Ours, Gemini replay**. B is omitted (dirty panels). No battery = the twin behind S.
- **Agent output** = report §11.2 JSON: knobs `soc_floor`, `export_hold_eur`, `evening_reserve_kwh` (+ grid-charge window), a 15-min schedule, KPIs, an explanation, and `carbon_source`. Downloadable.
- **Guardrails** (§11.3): schema check → clamp (SoC 0.1–0.9, 5 kW) → replay gate vs the static rule → fallback chain (previous valid plan, then the static rule).
- **Memory:** seeded with the 14 logged days of A + C, scored by regret vs the rule.
- **Cost basis:** wear €0.005/kWh discharged. Token price = Devstral 2 list $0.40/$2.00 per M at 0.86 €/$ (assumed). Ours also shows the actual Gemini token counts.
- **Model:** Ministral 3 8B (the proposed model), run locally via llama.cpp; the server only replays the committed plans. (Gemini Flash was the stand-in until session 10.)
- **Stack:** FastAPI + Vite/React, one Render service; three.js isometric site.
- **Look:** `docs/DESIGN.md`. Chosen layout = `mock-1` + `mock-kpi`, after the de-slop pass.

## Sessions
- [x] **1 `demo-design`**: DESIGN.md, canvas-design philosophy, PNG mockups in `docs/mockups/`. The user picks one.
- [x] **2 `demo-sim-engine`**:
  - `demo/sim.py` (rolling LP, HiGHS) + `demo/agent.py` (Gemini 3.5 Flash-Lite REST, validator, cache, k-NN memory).
  - Outputs: 6 run JSONs + `kpis.json` + `memory.json` + the committed `gemini_cache.json`; 7/7 Gemini days per run.
  - `--check` passes:
    - reproduces the Excel A/C/rule;
    - S* 2.1844;
    - plain S5 upside +0.7%, conservative +5.2% (soft miss);
    - the gate blocks bad knobs;
    - no key in the outputs.
- [x] **3 `demo-api`**: `demo/api.py` (FastAPI) + `demo/test_api.py` + `render.yaml`. The free instance sleeps, so warm it up before the demo.
  - `/api/run?mode=&lambda=` returns 422 off the 3×2 grid.
  - Responses are gzipped (120 KB → 16 KB).
  - `/api/live/carbon`: last 24 h of ENTSO-E A75 Italy hours (Europe/Rome), cached 1 h. The fallback is 356 g/kWh with no points, cached 5 min.
  - Serves only allowlisted files, never `gemini_cache.json` or `memory.json`. Deploy waits for session 5.
  - **Session 4 inputs from the agent reviews:**
    - Run rows have no price per step and no A/C/no-battery series. Add price (and the comparison series) to `sim.py`, or the UI can't draw the comparisons.
    - `kpis.json` `carbon_source` says `entsoe-hourly`, but the KPIs use the constant 0.356. Fix the label.
    - Gate-blocked days: `explanation` and `thoughts` describe the *rejected* plan. Show `used` + `gate.passed` next to them.
    - `tok_out` includes thinking tokens.
    - No path routes: use tab/hash state, because StaticFiles has no SPA fallback.
    - Prefetch all 6 runs. Append `cd demo/web && npm ci && npm run build` to render.yaml's build command.
- [x] **4 `demo-ui-sim`**: `demo/web/` Vite/React + three.js. Sky mockups (backdrop chosen over dome), engine data (price, `compare.json` + `/api/compare`, neighbour regret, carbon label `constant-0.356` + `s3_basis`), KPI strip, agent panel (blocked day: struck-through proposals, labelled rejected explanation, collapsible reasoning), pipeline packets (WAAPI, seek-cancel), playback, data-driven sun/moon/stars. Reviewed by code-reviewer, ui-ux-tester and impeccable finish review; fixes applied.
  - **Session 5 inputs:**
    - Pipeline labels shrink to ~9 px below ~1600 px wide (fine at 1920): size the SVG viewBox to the container.
    - `compare.json`, step prices and `s3_basis` are not drawn yet (KPIs tab / charts).
    - Upside grid charging is drawn as reverse battery flow (green), not a grid→battery path.
    - Outcome packet (Memory → Agent) lands after the 11:00 decision sweep; consider firing it earlier.
    - Space is swallowed on focused buttons; autoplay ignores prefers-reduced-motion; `test_api.py` can pass vacuously if `web/dist` is missing.
    - Render: confirm Node exists in the Python build image (else NODE_VERSION or commit dist).
- [x] **5 `demo-ui-kpis`**: KPIs tab (`Kpis.jsx`): conformity table (16 headline rows, "Show all 30"), Ours column follows the Sim mode/λ, Good counts, live ENTSO-E card (fallback shown), F5/P4 computed from run `days`. `kpis.json` gains `meta`. Carry-overs done: pipeline labels keep real px (+ 2-line wrap), Space toggles unless a control has keyboard focus, no autoplay under reduced motion, `test_api.py` needs `web/dist`, NODE_VERSION 22. Reviewed by code-reviewer, ui-ux-tester, impeccable finish pass; fixes applied.
  - **Left:** push + PR; connect the Render Blueprint and set `ENTSO_API`; warm up before the demo. Backlog: grid→battery path for upside charging, earlier outcome packet, `compare.json` and step prices still not drawn.

- [x] **6 `demo-polish`** (2026-11-19): grid→battery particle path (upside), Memory→Agent packet at 20:00, plan-day chart in the agent panel (`DayChart.jsx`: SoC ours / pilot C / static rule over the buy price, two panels, no dual axis), KPI strip "Week result" + signed gap to C, blocked-day ring chips, new Agent/Clamp icons, 15 px labels ≥1600, phone fixes. Reviewed by ui-ux-tester, impeccable critique (A+B), code-reviewer (no bugs), impeccable finish pass.
- [x] **7a `demo-pipeline-cue`** (2026-11-19, PR #11): the working stage enlarges 1.18× and fills (mockup `mock-cue.png`, variant c2). Agent, Validator and Memory ride the packet WAAPI; Rule → Clamp → Site run as a 1.8 s executor loop; reduced motion = fill only.
- [x] **7b `demo-live`** (2026-11-19, not merged):
  - "Run the agent live" streams `/api/live` (SSE): real Gemini (cache bypassed), gate, MPC, day by day.
  - Playback waits at the live frontier; the pipeline follows the server stage with a status line.
  - Guards: site passcode (Basic auth), 1 run at a time, `LIVE_CAP`/day.
  - Locally: 51–68 s per week, 7/7 Gemini, one 503 retried.
- [x] **7c Render measurement** (2026-11-19): free tier, 3 runs: 2:44 / 4:31 / 5:23, all 7/7 Gemini. Variance comes from 503s. The user accepted the free tier.
- [x] **7d live memory pool:** live runs add their finished days to the k-NN memory, scored like the seed. The agent's reasoning cites earlier days.
- [ ] **8 (next):** merge PR #11 + the `demo-live` PR; regenerate the replay when ENTSO-E is back.
  - Original criteria:
  - Blueprint on `demo-live`, set the secrets, warm up, run 2 live weeks.
  - Pass: < ~3 min and ≥ 5/7 days from Gemini, then merge.
  - Slow: Starter ($7).
  - Bad: don't merge; main stays playback + cue.

## Honesty flags (show them in the demo)
- The plain rule won this January week (`analysis/replay.py`), so ours may only tie it. The gate and fallback are part of the story.
- Site = Italy is assumed. The replay's 8B ran at 3-bit on a laptop; the costed set-up serves it at full quality.
- [x] **9 `report-ministral`** (2026-11-19): diagram (Reply's E&U platform + our changes, `docs/diagrams/reply-platform.*`), KPI workbook and report cut to 3 scenarios (A, C, Ours). Ours = sim conservative λ0.10 + Ministral 3 8B central at 1,000 sites: N1 +0.98, F1 −0.06, 15/20 Good.
- [x] **10 `demo-ministral-replay`** (2026-11-19): replay only (live mode and Gemini removed). The 3 λ runs were regenerated with **Ministral 3 8B Q3_K_S** on the M1 laptop (llama-server, -c 3072, q8 KV): 21/21 valid JSON, 0 clamps, ~27 s/call; the gate kept 2/7 plans at λ 0.10. KPIs tab = Pilot A, Pilot C, New framework (+ F1 row, honesty note). O5 = model_cost central 1,000 sites. Report, workbook and ours_ministral.json synced.
- [ ] **11 deck:** update `docs/PRESENTATION.md`, `docs/SCRIPT.md` and `docs/deck/deck.pdf` to the 3-scenario, Ministral basis (N1 +0.98, AI €0.18, CO2 12.2 kg, F1 −0.06 caveat, new diagram on the framework slide).
- [x] **11 `demo-gate-reason`** (2026-11-19): validator tooltip on blocked days (replay day, plan vs default score, which plan ran). Mockup `docs/mockups/mock-gate-tip.png`. Passes: ui-designer, frontend-developer, Emil, no-slop, impeccable (type → 14 px), design-taste. Open: push + PR; per-knob attribution when ENTSO-E is back (optional).
