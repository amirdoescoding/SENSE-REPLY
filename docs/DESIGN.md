# DESIGN.md: framework simulation demo

Visual system for the demo app (sessions 4–5 in `.claude/TODOS.md`).
- **Philosophy:** "Quiet Telemetry" (`docs/mockups/PHILOSOPHY.md`). The surface stays still and only data moves.
- **Sources:**
  - palette taken from the live reply.com/sense-reply CSS (2026-11-18);
  - layout inspired by Reply's MAGO site screen (photos in `assets/images/`).
- **Rule:** be inspired by MAGO, but do not copy its renders or layout pixel for pixel.

## 1. Audience and context
- A technical but relaxed Sense Reply jury, shown live on a projector, switching between windows. Design for a **1920×1080, 16:9 desktop first**. Phone width only needs to not break.
- Readable from 4 m: body ≥ 15 px, KPI numbers ≥ 28 px, and no information carried by colour alone.

## 2. Tokens (light theme only)

| Token | Value | Use |
|---|---|---|
| `--ink` | `#151F27` | text, structure (Reply ink) |
| `--ink-2` | `#3F4D5A` | secondary text |
| `--mute` | `#8D99A5` | labels, axes |
| `--line` | `#D6E0EA` | borders, grid, idle paths |
| `--paper` | `#F4F8FC` | page background |
| `--card` | `#FFFFFF` | panels |
| `--agent` | `#3A7DDA` | intelligence: agent, plans, LLM calls (Reply brand blue) |
| `--agent-soft` | `#E8F0FB` | agent panel fills |
| `--sun` | `#F2A900` | PV energy (warmer cousin of Reply `#FFD138`, readable on white) |
| `--store` | `#02B843` | battery charge/discharge (Reply green `#02D34A`, darkened for contrast) |
| `--grid` | `#586674` | grid import/export paths |
| `--alert` | `#EB0037` | validator fail, fallback, import at dirty hours (Reply red) |
| `--co2-lo` → `--co2-hi` | `#7FC8A9` → `#C9733A` | carbon intensity ramp (cool → dirty) |

Series colours are fixed across every chart: **ours = `--agent`, run A = `--ink-2`, run C = `--mute`, no battery = `--line` hatched.**

- **Type:**
  - UI and labels: **Instrument Sans** (Google Fonts), standing in for Reply's proprietary *Alaska*;
  - numbers, units and timestamps: **JetBrains Mono**, with tabular figures.
  - Labels: 12–13 px uppercase, tracking +0.08em, `--mute`. Body: 15–16 px. KPI: 32–40 px mono. Use one headline per screen at most.
- **Spacing:** 8 px grid; panel padding 24; gap 16.
- **Radius:** 12 (cards), 999 (chips).
- **Shadow:** `0 1px 2px #151F270F, 0 8px 24px #151F270A`. Never heavy.

## 3. Layout (from mockups, chosen variant TBD)
Mockups in `docs/mockups/` (source `mock.html`, render with `render.sh`):
- `mock-1.png` **MAGO classic**: KPI row, site, horizontal pipeline, right agent panel.
- `mock-2.png` **Pipeline-first**: vertical framework column, site, week timeline (SoC, PV, price, CO2).
- `mock-3.png` **Stage**: full-bleed site with floating KPI and agent panels, and the pipeline across the bottom.
- `mock-kpi.png` **KPIs tab**: comparison bars, the λ trade-off scatter, and the live ENTSO-E card.

- **Header (64 px):**
  - Sense Reply logo;
  - tabs **Simulation · KPIs**;
  - run chip `Replay · 5–12 Jan 2026 · Gemini Flash (stand-in for Devstral 2)`;
  - assumption chip `Site: Italy (assumed)`.
- **Simulation tab:**
  - KPI tile row;
  - the 3D isometric site (hero);
  - the agent panel (today's plan + why + validator + memory);
  - the agent-flow pipeline;
  - the playback bar (play, speed, day chips, λ snap slider 0 / 0.10 / 0.50 €/kg).
- **KPIs tab:** a comparison of ours vs A vs C vs no battery (bill, CO2, import, P99 peak, LLM calls, tokens, LLM spend), the cost-vs-CO2 trade-off scatter (one point per λ), and a live ENTSO-E carbon card for today.

## 4. Components
- **KPI tile:** label (caps, mute), value (mono 32), unit (mono 15, mute), and a delta vs run A (green if better, red if worse, with an arrow so it does not rely on colour).
- **Agent panel:** day header, then the 3–4 knob rows (name · value · unit), then the "why" in ≤ 2 lines, then three validator checks (✓/✗ + label), then memory chips (date · regret €).
- **Flow node:** a 56 px rounded square with an icon and a caps label underneath. States: idle (`--line` border), active (`--agent` border + soft glow), fail (`--alert`), fallback path (dashed).
- **Packet:** an 8 px dot on a 1.5 px path, coloured by type: decision (`--agent`), energy (`--sun`/`--store`/`--grid`), outcome (`--ink`).
- **Timeline:** shared x axis (7 days × 96 steps). Tracks: price line, CO2 band (ramp), SoC area (`--store`), battery kW bars. The playhead is a 1 px ink line.
- **Chips:** day chips (Mon…Sun) show a dot for the plan status (passed / fallback).

## 5. Motion
- Energy particles: speed ∝ |kW|, density ∝ kWh. When a flow is idle, its path fades to `--line`.
- Decision packet, once per simulated day: Inputs → Agent (pulse while "thinking") → Validator (pause 300 ms; pass = continue, fail = red flash, then reroute to Fallback) → Rule → Clamp → Site. Every evening an outcome packet runs Site → Memory → Agent.
- Easing: `cubic-bezier(.2,.8,.2,1)`. UI transitions take 150–250 ms. Number tickers move in tabular mono with no layout shift.
- Playback speeds: 1 day ≈ 20 s at 1×, plus 4× and 16×. `prefers-reduced-motion` turns particles off and keeps the numbers updating.

## 6. 3D site (three.js) art direction
- Orthographic camera at the isometric angle (35.264°, 45°). Soft studio light with one key light and an ambient-occlusion feel. The floor is `--paper` with a faint `--line` grid.
- Low-poly, matte, near-white objects (`#FFFFFF`/`#E8EDF2`) with an ink outline feel:
  - house;
  - 9 PV panels (3×3, tilted);
  - battery cabinet with a live SoC bar;
  - grid pylon.
- Colour appears only on live elements (PV glow, SoC bar, flow tubes).
- Flows are thin tubes on the floor between the assets, with particles riding them. Floating labels are DOM overlays (mono kW values) pinned to the 3D anchors.
- No textures and no photoreal models. Original geometry only.

## 7. Content rules
- Every number shown maps to a JSON field from the sim/API. Mock values in mockups are labelled "mock".
- Always visible somewhere: "Site: Italy (assumed)" and "Gemini Flash = stand-in for Devstral 2, not a model proposal".
- Copy is short, outcome-led and in sentence case, matching Sense Reply's tone ("Lower bill, less CO2, 7 calls a week").
