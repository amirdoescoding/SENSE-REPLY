# demo-gate-reason (2026-11-19)
**Done:** tooltip on the Validator node explains why the replay gate blocked the plan. Commits 8cbe490 (lib + App), 3efb95b (Pipeline + CSS + mockup).
**Process:** plan → ui-designer copy → mockup (user: status line just "blocked") → frontend-developer → fixes (reset effect fired every render; tap opened then closed; phone offset) → Emil / no-slop (shadow 8 px) / impeccable (14 px type) / design-taste.
**QA:** `npm run build`; Playwright checks: λ0.1 day 2 hover, λ0 day 1 (static rule), passed day (no tabindex), keyboard + Esc, phone tap. Numbers match run_0.1.json (0.6268/0.6215). `/qa` skill not run; these checks covered it.
**Self-rating 7/10:** the subagent shipped two real bugs, which I caught in review and the screenshots.
