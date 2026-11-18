# SENSE-REPLY BDD

## 0. Project context

Albert School 2nd-year Business Deep Dive with **Sense Reply** (Reply group): performance assessment of
LLM edge agents that dispatch a home battery (PV + BESS + grid + residential load).

- **Mission:** define KPIs (with formulas), compare two agent configurations, quantify the cost vs
  sustainability trade-off, and suggest improvements to the agentic decision framework.
- **Deliverables:** KPI dashboard, time-series analysis report, trade-off matrix, executive summary,
  framework improvement proposals.
- **Data:** `data/DatasetV4/` (V3 kept for history). `dataset-001.json` = Orchestrator + Cost agent;
  `dataset-002.json` = Orchestrator + Cost + Sustainability agent; `dataset-003.json` = same as 002 but same panel dirt as 001.
  `Prompts/` = agent prompts, `Assets/` = BSS/PV specs. Field definitions are in `DATA_MODEL.pdf`,
  and LLM usage per config is in `DataIndex.xlsx`. Key facts are in @MEMORY.md.
- **Brief:** `docs/Albert_School_BDD_Template - Second Year - v1.2.docx`, `docs/SENSE_REPLY_TRANSCRIPT.md`,
  `docs/Sense Reply BDD 2026 - v1.1.pdf`. Research is in `docs/research/` (start at `00-synthesis.md`).
- Every KPI must map to a real JSON field or a named external source. Flag assumptions (e.g. site = Italy).

## Context via Graphify (read first)

- **Before starting any task**, query the knowledge graph in `graphify-out/` first:
  `graphify query "<question>"`, `graphify path "<A>" "<B>"`, `graphify explain "<node>"`.
  Read only the files the graph points to. `graphify-out/GRAPH_REPORT.md` is for broad overviews.
- After code changes, run `graphify update .` (AST-only, free). After doc/PDF changes, run
  `/graphify . --update` (semantic re-extraction of changed docs only).
- `graphify-out/` is gitignored; each teammate builds it locally with `/graphify .`.

## **GIT**

- Always create a new branch for a new feature
- Split work in commits

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant
clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to
overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## Session close

1) Run `/qa`, write the recap + self-rating to `.logs/YYYY-MM/DD/<slug>.md`.
2) Update @MEMORY.md with Key facts & decisions so far
3) Update @RESTART.md with what you were doing and where you stopped
4) Update Backlog with Everything still left to do
5) Update ARCHITECTURE.md if any changes were made to the structure

## Demo (framework simulation)
- Plan and progress: `.claude/TODOS.md`. One session = one feature branch, split into commits.
- Mockups (PNG, canvas-design) come before any front-end code. The UI follows `docs/DESIGN.md`.
