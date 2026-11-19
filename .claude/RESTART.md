# Restart point

2026-11-19: `report-ministral` session closed. Three commits are on branch `report-ministral` (no PR yet):
- the diagram;
- report v2 + charts + `data/ours_ministral.json`;
- the KPI workbook.

All three are cut to Pilot A, Pilot C and Ours (Ministral 3 8B central). See MEMORY "Report + KPIs on Ministral".

**Open from before:** PR #11 (`demo-pipeline-cue`) and `demo-live` are still unmerged. The Render deploy runs from `demo-live`.

**Next sessions, one at a time:**
1. **Demo cleanup:**
   - remove the conservative/upside modes and S5 columns;
   - show A, C and Ours only;
   - relabel the stand-in model;
   - decide whether Ministral 3 3B can run on the demo host. Render free has 512 MB, so probably not; the options are the recorded bench plans, a paid instance, or an API-hosted Ministral.
2. **Deck:** PRESENTATION.md, SCRIPT.md and deck.pdf on the new numbers (N1 +0.98, AI €0.18, CO2 12.2 kg, F1 −0.06 caveat), with the new diagram on the framework slide. Same procedure as this session, with the data-analyst and data-scientist agents.

**Before handing in:** open `docs/Sense Reply BDD B2 – Full Analysis Report.docx` in Word once. It was only checked via an HTML render.
