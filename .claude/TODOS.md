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
- **Model:** Gemini Flash free tier (`GEMINI_API_KEY` in `.env`), a stand-in for Devstral 2, not a proposal.
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
- [ ] **4 `demo-ui-sim`**: three.js site (PV, battery, house, pylon) with energy particles. The agent-flow pipeline with moving packets, playback, a day scrubber and the λ slider.
- [ ] **5 `demo-ui-kpis`**: Excel-aligned conformity table with verdicts, Good counts, live ENTSO-E card, and the F5/P4 KPIs now measurable.

## Honesty flags (show them in the demo)
- The plain rule won this January week (`analysis/replay.py`), so ours may only tie it. The gate and fallback are part of the story.
- Site = Italy is assumed. Gemini ≠ Devstral: it's a capability stand-in.
