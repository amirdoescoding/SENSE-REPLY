# demo-ui-kpis (session 5)

- Planned in plan mode. Two Explore agents mapped the web UI and the API/data/deploy.
- User choices:
  - pin NODE_VERSION;
  - compute F5/P4 from the runs;
  - the Ours column follows the toggles.
  The carry-over question went unanswered; my default was the small a11y/test fixes plus the pipeline labels.
- Commits:
  - `a8be6f3` KPI meta;
  - `49c5c6b` KPIs tab;
  - `4f42781` pipeline labels, test_api, Node pin;
  - `9c2d0b5` review fixes;
  - `c8c1b96` UX fixes.
- Bugs the reviews caught:
  - clamp rate counted notes rather than plans;
  - "−0.00";
  - k = Infinity on the hidden tab;
  - 2-line labels clipped at k > 1.8;
  - Space re-clicked a mouse-focused button instead of pausing;
  - phone table showed no values (now a sticky KPI column);
  - axis labels without day names.
- Skipped on purpose: bar colours stay on the DESIGN.md series palette; verdicts stay icon-only in cells (legend + aria), as in the approved mockup.
- QA: the ui-ux-tester run counts as /qa (5 widths, keyboard, reduced motion, mode sync). `sim.py --check` and `test_api.py` pass.
- Self-rating: 8/10.
  - Good: a small diff, reused the existing kpis.json, no new deps.
  - Weak: the Space handler needed two passes, and the deploy is still unverified on Render.
