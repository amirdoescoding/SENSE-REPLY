# deck-ministral (2026-11-19)

**Done:**
- Rebuilt the pitch on Ministral 3 8B self-hosted and three scenarios. Slides 0–9 plus appendix A1–A6. Branch `deck-ministral`, 3 commits plus docs.
- **Storyline.** `docs/PRESENTATION.md` holds the action titles (title-only read). Timing: Sydney 2:40, Amir 2:15, Francesco 1:50.
- **Slide 2.** The KPI slide is one layer. Each of the 20 KPIs is a card: plain question, code and pass line. The card's left edge shows the yardstick: blue for the free rule, ink for no battery, dotted for the optimiser, grey for a fixed target. The user asked for this because the old 2-layer version was unclear.
- **Slide 7.** Same grid with A/C/New verdict dots: A 5/19, C 6/20, New 15/20. Recomputed from the workbook thresholds; this matches.
- **Slide 5.** Reply's platform diagram, redrawn inline in deck style. The pipeline moved to A1.
- **Slide 8 (new).** Log-log chart of AI cost per site against fleet size, from `model_cost.OPTIONS`:
  - the on-prem 8B beats the rule from ~1,500 sites, the EU API from ~580;
  - the 3B box is a band at €1.86–8.12/wk, so it is sold as a premium (€97–422/site/yr);
  - default sites already keep running offline.
- **Framing for F1 −0.06.** Ahead of the rule before AI cost, level after it; fleet size closes the gap. It appears on slides 7 and 8 and in Q&A 1.
- **Slide 4.** The scatter keeps y = N1, so the new framework sits next to the free rule.
- **Demo shot.** Refreshed: the blocked Tuesday on a local uvicorn plus the Playwright metal recipe.
- **Script.** Rewritten (762 words) with stop-slop. Q&A rewritten: F1, why self-host, offline box, why Ministral, cost basis, gate 2/7, one week, run B, rule vs MPC.

**Not done:**
- No separate impeccable or gstack /design-review run; I reviewed the PNGs by eye.
- The deck is not pushed.
- `deck.pdf` was not opened in a viewer.

**Self-rating 7/10.** First renders had label collisions on slides 4, 5 and 8, fixed after looking. I wrote the first KPI dots as blue in the docs and corrected it to green.
