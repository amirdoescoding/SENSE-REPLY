# Demo TODOs: framework simulation

One session = one feature = one branch, split into commits. Mockups come before any front-end code.
Close each session with: memory files + `graphify update .`.

## Agreed decisions (2026-11-18)
- Precompute + playback: a Python replay writes JSON, and the UI animates it.
- Memory seeded with the 14 logged days of runs A + C, scored by regret.
- Data: A's sun/load/prices + ENTSO-E hourly carbon (Italy, assumed). Plus a live ENTSO-E pull for today.
- λ ∈ {0, 0.10, 0.50} €/kg, precomputed; the slider snaps between them.
- KPI comparison: ours vs run A vs run C vs no battery.
- Model: Gemini Flash free tier (`GEMINI_API_KEY` in `.env`), a stand-in for Devstral 2, not a proposal.
- Stack: FastAPI + Vite/React, served from one Render service. three.js isometric site.
- Look: MAGO / Sense Reply light (see `docs/DESIGN.md`). Audience: a technical but relaxed jury, live demo with window switching.

## Sessions
- [x] **1 `demo-design`**: DESIGN.md, canvas-design philosophy, PNG mockups in `docs/mockups/`. The user picks one.
- [ ] **2 `demo-sim-engine`**: `demo/sim.py`.
  - Reuses kpis/replay/carbon/timeseries.
  - Gemini daily knobs → validator → fallback → knob rule + clamp → memory.
  - JSON per λ (15-min states, plans with reasons, verdicts, retrievals, calls/tokens/spend).
  - Self-check: equals `rule_baseline` with the knobs off.
- [ ] **3 `demo-api`**: FastAPI `/api/run?lambda=`, `/api/kpis`, `/api/live/carbon` (cached), serving the built frontend, plus `render.yaml`. The free instance sleeps, so warm it up before the demo.
- [ ] **4 `demo-ui-sim`**: three.js site (PV, battery, house, pylon) with energy particles. The agent-flow pipeline with moving packets, playback, a day scrubber and the λ slider.
- [ ] **5 `demo-ui-kpis`**: KPI/compare tab (requests, tokens, LLM spend, bill, CO2, import, P99 peak) plus the live carbon card.

## Honesty flags (show them in the demo)
- The plain rule won this January week (`analysis/replay.py`), so ours may only tie it. The gate and fallback are part of the story.
- Site = Italy is assumed. Gemini ≠ Devstral: it's a capability stand-in.
