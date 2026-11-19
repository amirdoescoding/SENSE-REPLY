# demo-ministral-replay (2026-11-19)

**Goal:** a replay-only demo on real Ministral 3 8B plans, with the KPIs tab cut to Pilot A / Pilot C / New framework, no Gemini, no live mode. Report synced to the new run.

**Done (branch `demo-ministral-replay`, one commit per step):**
- engine: `agent.ask` → llama-server; upside, S5, check_lp, run_perfect, live/emit code removed; O5 = model_cost central @ 1,000 sites.
- replay: Ministral 3 8B Q3_K_S on the M1 8 GB (`-c 3072 -np 1 -ctk q8_0 -ctv q8_0 -fa on`, Dia closed, watchdog at pressure level 4). 21/21 valid JSON, 0 clamps, ~27 s/call. Pressure stayed at level 2.
- api: `/api/live` removed, `/api/run?lambda=`; render.yaml drops GEMINI_API_KEY / LIVE_CAP.
- ui: no live button or mode toggle; KPIs tab A / C / New framework (+F1, honesty note); header "Ministral 3 8B, self-hosted (Q3 on a laptop)".
- report sync: VORB +0.12, peak 2.2 kW (now best of three), PSR 0.54, MAC ≈ 0 (−€0.011/kg), F1 > 0 from ~1,500 sites. N1 +0.98, F1 −0.06, 12.2 kg and 15/20 Good are unchanged. REPORT.md, FINAL.docx (pandoc), workbook col K, ours_ministral.json, charts.
- review fixes (code-reviewer): crash on λ 0 day 1 (`knobs: null` after a blocked first day → static rule), orphan `import time`; plus pipeline line now says which fallback ran, and `**` stripped from model explanations.

**QA:** `sim.py --check` (1a/1b, 5), `test_api.py` → api ok, `npm run build`, Playwright screenshots (Sim λ 0.1 / λ 0 day 1, KPIs). The `/qa` skill was not run; these checks covered it.

Screenshot recipe (the swiftshader shell no longer works): Playwright from `~/.npm/_npx/e41f203b7505f1fb/node_modules/playwright`, `chromium.launch({args: ['--use-gl=angle', '--use-angle=metal']})`, `waitForSelector('.panel')` / `.kt`.

**Not done:** push/PR/Render switch (needs user), deck (next session), full-precision 8B re-run (optional).

**Self-rating 7/10.** The plan held and the 8B ran without a crash. Two of my own slips: the KPIs note used `run` inside `Table` (blank page, caught by the screenshot), and I missed the null-knobs day that the new run introduced (caught by review). Also, the `useLive.js` deletion landed in the "replay" commit instead of the "ui" commit.
