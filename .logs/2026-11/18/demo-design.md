# Session: demo-design (2026-11-18)

## Done
- Q&A on the demo (4 rounds). Decisions are recorded in `.claude/TODOS.md`.
- Branch `demo-design`, 4 commits: TODOS.md, the CLAUDE.md demo section, DESIGN.md, mockups.
- Palette taken from the live reply.com/sense-reply CSS: ink #151F27, paper #F4F8FC, line #D6E0EA, brand blue #3A7DDA, green #02D34A, red #EB0037, yellow #FFD138. Brand font Alaska (proprietary) → Instrument Sans + JetBrains Mono.
- Mockups: HTML (`docs/mockups/mock.html`) → PNG via Playwright's cached headless Chromium (`render.sh`). PIL is not installed, so this was the simplest path.

## QA
- /qa skipped: there is no running app in this session (design only). The PNGs were checked visually at 1920×1080. Overlaps were fixed in 2 passes.

## Self-rating: 7/10
- Good: real brand tokens, honest "mock" labels, and every layout shows the framework pipeline.
- Weak: the isometric SVG is only a stand-in for the three.js scene, and the logo renders small (whitespace in the avif). The mock numbers for "ours" are invented.
