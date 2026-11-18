# DESIGN.md: framework simulation demo

Visual system for the demo app (sessions 4–5 in `.claude/TODOS.md`).
- **Philosophy:** "Quiet Telemetry" (`docs/mockups/PHILOSOPHY.md`). The surface stays still and only data moves.
- **Sources:**
  - palette taken from the live reply.com/sense-reply CSS (2026-11-18);
  - layout inspired by Reply's MAGO site screen (photos in `assets/images/`);
  - numbers and KPI IDs from `data/Sense_Reply_B2_KPI_Conformity.xlsx` and `docs/Sense Reply BDD B2 – Full Analysis Report.docx` (§5, §6, §11).
- **Rule:** be inspired by MAGO, but do not copy its renders or layout pixel for pixel.
- **De-slop pass (2026-11-18):** the rules below come from no-slop-ui, emil-design-eng and stop-slop. Where a rule here conflicts with an older note, the rule wins.

## 1. Audience and context
- A technical but relaxed Sense Reply jury, shown live on a projector, switching between windows. Design for a **1920×1080, 16:9 desktop first**. Below 1280 px, stack the agent panel under the site; phone width only needs to not break.
- Readable from 4 m: body ≥ 14 px, KPI numbers ≥ 28 px. Verdicts use an icon and a word, never colour alone.

## 2. Tokens (light theme only)

| Token | Value | Use |
|---|---|---|
| `--ink` | `#151F27` | text, structure (Reply ink) |
| `--ink-2` | `#3F4D5A` | secondary text |
| `--mute` | `#66727E` | labels, axes (darkened from #8D99A5 on 2026-11-18: 2.9:1 failed WCAG AA, now 4.9:1 on white) |
| `--line` | `#D6E0EA` | borders, grid, idle paths |
| `--paper` | `#F4F8FC` | page background |
| `--card` | `#FFFFFF` | panels |
| `--agent` | `#3A7DDA` | intelligence: agent, plans, LLM calls (Reply brand blue) |
| `--agent-soft` | `#E8F0FB` | agent fills, "Ours" column |
| `--sun` | `#F2A900` | PV energy |
| `--store` | `#02B843` | battery |
| `--grid` | `#586674` | grid import/export |
| `--alert` | `#EB0037` | validator fail, fallback |
| `--good-bg` / `--good-fg` | `#E3F7EA` / `#027A31` | "Good" verdict |
| `--imp-bg` / `--imp-fg` | `#FDE7EC` / `#B0002A` | "Improvable" verdict |
| `--co2-lo` → `--co2-hi` | `#7FC8A9` → `#C9733A` | carbon intensity ramp |

- **Series colours:** ours = `--agent`, S5 = `--agent` (lighter), pilots = `--ink-2`, static rule = `--mute`.
- **Type:**
  - UI: **Instrument Sans**, standing in for Reply's proprietary *Alaska*. Numbers, units and timestamps: **JetBrains Mono**, tabular figures.
  - Labels are 13 px **sentence case** in `--mute`. Never uppercase eyebrow labels.
  - Body 14–16 px; KPI 30 px mono; one H1 per screen at most.
- **Spacing:** 4/8/12/16/24/32. Panel padding 20–24, gap 16.
- **Radius:** cards 12, controls and chips 6, verdict tags 4. No pills.
- **Shadow:** `0 1px 2px #151F270F` only. No glow and no blur-24 shadows.

## 3. Layout: chosen variant = `mock-1.png` (MAGO classic)
Mockups in `docs/mockups/`. The source is `mock.html` (`?v=1|2|3|kpi`); render them with `render.sh [variants]`. Variants 2 and 3 are kept for history only.
- **Header (64 px):**
  - logo;
  - tabs **Simulation · KPIs** (text tabs with a 2 px underline, no pill);
  - plain meta text separated by 1 px rules: replay window + "run C's sun, load and prices, start SoC 80 %", "Gemini Flash, stand-in for Devstral 2", and "Site: Italy (assumed) · CO2 0.356 kg/kWh".
- **Simulation tab (`mock-1.png`):**
  - **KPI strip**: one card, six cells with 1 px dividers. It shows the report's headline KPIs for our run, each with a Good tag when it meets the Excel threshold and the pilot C value underneath: N1, VORB, VCR, S1, O1, O5.
  - **Site**: the three.js isometric scene, the hero.
  - **Agent panel (right, 440 px):**
    - the plan for the day, with mode and λ;
    - knobs from the report's JSON schema (§11.2): `evening_reserve_kwh`, `soc_floor`, `export_hold_eur`, grid-charge window;
    - the reason the agent gives, in first person, ≤ 2 lines;
    - a collapsible "Model reasoning" (`<details>`, closed by default) with Gemini's thought summary (user decision, 2026-11-18). Gemini's reason is shown verbatim, so it may say "We…" and run longer than 2 lines;
    - on a gate-blocked day, the used knob values with the proposed values struck through;
    - checks (schema, clamp, replay gate vs the static rule);
    - the similar past days it was shown, with their regret;
    - a "Download plan JSON" button.
  - **Pipeline strip**: Inputs → Agent, 1×/day → Validator + gate → Rule, every 15 min → Clamp 10–90 %, 5 kW → Site → Memory, with the memory → agent return arc above it.
  - **Playback bar**:
    - play/pause, time, speed 1×/4×/16×;
    - day chips with a plan-status dot;
    - mode segmented control (Conservative / Upside, shadow);
    - λ slider snapping to 0 / 0.10 / 0.50 €/kg.
- **KPIs tab (`mock-kpi.png`):**
  - The KPI conformity table follows the Excel exactly: grouped by Economics & AI value, Carbon, Self-use & grid, Battery & orchestration. Columns are ID, name, unit, threshold, A, C, Static rule, S5 conservative, S5 upside, and **Ours, Gemini** (filled by the replay).
  - The Good-KPI count per scenario comes from the Excel Summary.
  - A live ENTSO-E Italy CO2 card, with the 356 g/kWh workbook constant as a dashed reference.
  - "Now measurable in the replay": F5 fallback rate and the P4 trust KPIs, which the Excel lists as not assessable for the pilots.

## 4. Components
- **KPI cell:**
  - label `ID · plain name` (sentence case);
  - value in 30 px mono, unit in mono `--mute`;
  - an optional verdict tag;
  - the comparison line (`pilot C −7.31`) in 13 px mono `--mute`.
- **Verdict tag:** ✓ on `--good-bg`, ↑ on `--imp-bg`, 4 px radius. In tables, use the icon only (with a `title`) and a legend.
- **Agent panel:** H2 with the date, a mono meta line (time · calls · tokens), knob rows, the "why" block (`--agent-soft`, 3 px left rule), checks, memory rows, and one secondary button.
- **Flow node:** a 56 px square with 14 px radius, a 1.5 px stroke icon, and a 14 px sentence-case label. Active = `--agent` border + `--agent-soft` fill. Fail = `--alert` border. No halos.
- **Packet:** a single 9 px dot, no halo. Colours: decision `--agent`; energy `--sun`/`--store`/`--grid`.
- **Buttons:** solid ink or 1 px border, 6–8 px radius, `scale(0.97)` on `:active` (160 ms ease-out).

## 5. Motion (emil-design-eng)
- Curves: `--ease-out: cubic-bezier(.23,1,.32,1)` for entering things, `--ease-in-out: cubic-bezier(.77,0,.175,1)` for packets moving on screen, `linear` for particles. Never use ease-in.
- UI transitions take 150–250 ms and animate only `transform` and `opacity`. Never use `transition: all`. Hover effects sit behind `@media (hover:hover) and (pointer:fine)`.
- Energy particles: speed ∝ |kW|, count ∝ kWh. An idle path fades to `--line` over 200 ms.
- Decision packet, once per simulated day: Inputs → Agent (the node fill breathes while waiting) → Validator (300 ms hold; pass continues, fail flashes `--alert` and the packet reroutes along the dashed fallback). Then Rule → Clamp → Site. At day end an outcome packet runs Memory → Agent along the arc.
- KPI numbers update in tabular mono with no layout shift. There is no count-up animation on every tick, only on day change.
- Playback: 1 day ≈ 20 s at 1×. Keyboard shortcuts (space, ←/→) are never animated.
- `prefers-reduced-motion`: particles and packets off, numbers and colours still update.

## 6. 3D site (three.js) art direction
- Orthographic camera at the isometric angle (35.264°, 45°). One key light plus an ambient light, soft shadows. The floor is `--paper` with a faint `--line` grid.
- Low-poly, matte, near-white objects (`#FFFFFF`/`#E8EDF2`):
  - house;
  - 9 PV panels (3×3, tilted);
  - battery cabinet with a live SoC bar;
  - grid pylon.
- Colour appears only on live elements (PV, SoC bar, flow paths). Flows are thin floor paths with particles riding them. Labels are DOM overlays pinned to the 3D anchors.
- No textures and no photoreal models. Original geometry only.

## 7. Content rules (stop-slop)
- Every number maps to a JSON field from the sim/API or to a cell in the KPI Conformity workbook. Mock values carry a "mock" tag.
- Always visible: "Site: Italy (assumed)", "Gemini Flash, stand-in for Devstral 2", and the carbon basis (0.356 kg/kWh constant; hourly ENTSO-E as a check).
- Copy is plain and specific. Use active voice, no adverbs, no em dashes, no slogans, no "not X but Y". The agent's reason is written in first person and names numbers ("I keep 4 kWh for 17–22 h").
- Evidence labels follow the report: pilots OBSERVED, rule and S5 MODELLED, carbon factor and token price ASSUMED.
