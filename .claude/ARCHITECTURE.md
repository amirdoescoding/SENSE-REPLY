# Architecture Overview

Analysis repo for the Sense Reply BDD (agent performance assessment). Stdlib-only Python KPI scripts + markdown deliverables.

## 1. Project Structure

```
SENSE-REPLY/
├── .claude/              # Agent context: CLAUDE, MEMORY, RESTART, BACKLOG, ARCHITECTURE, agents/
├── data/DatasetV4/       # Source data (read-only); DatasetV3 kept (001/002 identical)
│   ├── dataset-001.json  # A: Orchestrator + Cost agent, 672 x 15-min samples
│   ├── dataset-002.json  # B: Orchestrator + Cost + Sustainability, 671 samples, dirtier panels
│   ├── dataset-003.json  # C: same agents as B, same panel dirt as A (main comparison C vs A)
│   ├── Prompts/          # Cost.txt, Sustainability.txt (agent system prompts)
│   ├── Assets/           # BSS.json (wear, target SoC 80%), PV.json (dirt rates)
│   ├── DATA_MODEL.pdf    # Field definitions, units, sign conventions
│   └── DataIndex.xlsx    # LLM requests / tokens / latency per dataset
├── data/SENSE REPLY - Method & Context.csv  # teammate's method notes
├── docs/                 # Case brief, transcript, slides, background briefing
│   ├── PROPOSAL.md       # Executive summary + simple framework (1 agent, carbon dial, daily knobs, memory)
│   ├── KPIS.md           # KPI dashboard A/B/C, trade-off matrix, teammate reconciliation
│   ├── TIMESERIES.md     # Time-series report: daily pattern, per day, grid, coordination, anomalies
│   ├── FRAMEWORK.md      # OLD redesign, superseded by PROPOSAL.md
│   ├── diagrams/         # framework.mmd (source) → .svg/.png/.excalidraw
│   ├── DESIGN.md         # demo design system (Reply palette, components, motion, 3D direction)
│   ├── mockups/          # demo mockups: mock.html → render.sh → mock-{1,2,3,kpi}.png; daychart.html → mock-daychart.png; cue.html → mock-cue.png; sky.html → sky.sh → sky-{backdrop,dome}-*.png
│   └── research/         # 00-synthesis.md = entry point; 05 hosting, 06 loop/learning, 07 self-hosting + simple framework
├── demo/                 # hosted demo of PROPOSAL (sessions in .claude/TODOS.md)
│   ├── sim.py            # engine: daily agent knobs → gate → rolling LP → Excel KPIs (+ META name/unit/group) → out/*.json (--check); main() regenerates run_{λ}.json with the local model
│   ├── agent.py          # Ministral 3 8B via llama-server (LLAMA_URL) + committed cache + validator + k-NN memory (seed A+C)
│   ├── local_bench.py    # bench other local models through the same agent.ask (own bench_cache.json)
│   ├── api.py            # FastAPI: /api/run?lambda=, /api/kpis, /api/compare, /api/live/carbon (ENTSO-E card), /healthz; DEMO_PASSCODE Basic auth; serves web/dist
│   ├── test_api.py       # python demo/test_api.py → "api ok"
│   ├── web/              # Vite + React (plain JS) + three: App (data, header, KPI strip, playback bar, λ state), Kpis (KPIs tab), AgentPanel (+ DayChart: plan-day SoC vs pilot C/rule + price),
│   │                     #   Pipeline (WAAPI packets + 'now' cue: working stage 1.18× + fill), Site (three.js site + data-driven sky), usePlayback, lib; npm run build → dist
│   └── out/              # run_{0.0,0.1,0.5}.json (Ministral 3 8B replay), kpis.json (A, C, New framework), compare.json, memory.json, model_cache.json (last two not served)
├── render.yaml           # one free Render web service (Python 3.14 + NODE_VERSION 22 for the vite build); secrets ENTSO_API, DEMO_PASSCODE (no model on the server); health /healthz
└── analysis/
    ├── kpis.py           # python3 analysis/kpis.py → KPI table A/B/C, baselines, T1-T3, self-check
    ├── timeseries.py     # per-day KPIs, day-type trade-off, hourly profile, anomalies
    ├── carbon.py         # CI_t from ENTSO-E API (token ENTSO_API in .env), else static ISPRA 198.9 g/kWh
    └── forecast_check.py # load/CO2/soiling predictability; CO2 day-ahead forecast test (FC2)
```

## 2. System under assessment

```
[9 PV panels] [BESS 10 kWh] [Residential load] [Grid connection]
        \           |              |               /
         └──── IoT Edge Gateway (Modbus/OPC-UA → IoT) ────┐
                    │ agents run here                     │ telemetry
         Orchestrator (structured AI workflow)            ▼
          ├── Cost agent          ──┐            Cloud IoT platform
          └── Sustainability agent ─┤ proposals  (device mgmt, data lake,
                                    │ + scores    edge apps store)
              LLM calls ──► Mistral Devstral 2 123B (cloud)
         orchestrator picks ONE battery power setpoint every 15 min
```

- Config A (dataset-001): orchestrator + cost agent only.
- Config B (dataset-002): agents discuss; each proposes power + self-scores (cost, resilience,
  comfort, sustainability); orchestrator selects.

## 3. Data model (summary of DATA_MODEL.pdf)

- Sample: `datetime`, `time` (s since start), `state.assets[]`. Ordered newest first.
- PV: `pv_power` kW, `pv_energy_interval` kWh, `pv_soh`, `pv_dirt`, `pv_fault`, `pv_energy_total`.
- BESS: `power` (+charge / −discharge), `soc`, `soh`, `temperature`, `throttling`, `fault`,
  `energy{Charged,Discharged}{Interval,Total}`, `capacityKwh`, SoC min/max, charge/discharge efficiency.
- Building: `load` kW.
- Grid: `power` (+import / −export), `energy{Import,Export}{Interval,Total}`, `buyPrice`, `sellPrice`
  €/kWh, `cost` (cumulative €), `violation`, `penalty` (cumulative €), `available`.
- No emissions field. Carbon intensity must come from an external source.

## 4. Glossary

- **BESS**: Battery Energy Storage System. **SoC/SoH**: state of charge / health (fractions).
- **PV**: photovoltaic. **KPI**: key performance indicator. **EFC**: equivalent full cycles.
- **Orchestrator**: workflow that discovers agents, runs the discussion, picks one proposal.
- **BDD**: Business Deep Dive (Albert School case format).

Date of last update: 2026-11-17
