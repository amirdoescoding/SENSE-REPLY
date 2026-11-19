# report-ministral (2026-11-19)

**Done:** three commits on `report-ministral`.
- Diagram: hand-placed HTML of Reply's "Agentic Operations for E&U", rendered to PNG. Mermaid auto-layout scrambled the layout, so it was dropped.
- `data/ours_ministral.json` (data-scientist agent), the KPI workbook rebuilt to A | C | Ours (data-analyst agent), and the report rewritten as `docs/REPORT.md`, then built with pandoc to docx using the old file as reference-doc. Two new charts (`analysis/report_charts.py`).

**Findings:**
- With Ministral 8B central at 1,000 sites, F1 (value over the rule after AI cost) is −€0.06/wk. It turns positive at 10k sites or on an EU API.
- Ours' peak import is 3.38 kW, above C's 2.93.

**Not verified:** the docx in Word. LibreOffice is not installed (stale shim), so it was checked via an HTML render instead.

**Self-rating:** 7/10. The scope was delivered and the numbers agree across doc, Excel and JSON. The deck and demo now disagree with the report until sessions 10–11.
