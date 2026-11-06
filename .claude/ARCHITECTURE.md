# Architecture Overview

Analysis repo for the Sense Reply BDD (agent performance assessment). No application code yet.

## 1. Project Structure

```
SENSE-REPLY/
├── .claude/              # Agent context: CLAUDE, MEMORY, RESTART, BACKLOG, ARCHITECTURE, agents/
├── data/DatasetV3/       # Source data (read-only)
│   ├── dataset-001.json  # Orchestrator + Cost agent, 672 x 15-min samples
│   ├── dataset-002.json  # Orchestrator + Cost + Sustainability, 671 samples
│   ├── DATA_MODEL.pdf    # Field definitions, units, sign conventions
│   └── DataIndex.xlsx    # LLM requests / tokens / latency per dataset
├── docs/                 # Case brief, transcript, slides, background briefing
│   └── research/         # Research sprint outputs (00-synthesis.md = entry point)
└── analysis/             # (planned) KPI computation notebooks/scripts
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

Date of last update: 2026-11-06
