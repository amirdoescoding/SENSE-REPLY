# 03 – Competitive landscape: AI energy optimisation and edge-agent platforms (as of Nov 2026)

Method note: this is a quick web pass of about 10 searches. It was not a deep dive. Items from search snippets carry a URL. Items from my background knowledge, or only partly confirmed, are marked "(unverified)". All published KPIs are vendor-reported and were not independently audited. They use different baselines, so they are not comparable with each other.

## 1. Executive summary

- **Proof is weak across the market.** Almost every vendor claims "% savings" or "% revenue uplift". Baselines are rarely stated: manual bidding, a prior operator, a no-battery case, or a single showcase site. No competitor found publishes a multi-KPI trade-off report (cost vs. emissions vs. cycling). That is the gap Sense Reply's KPI work can fill.
- **Utility-scale BESS optimisers** (Fluence Mosaic, Stem Athena, Tesla Autobidder, Habitat) sell on trading revenue uplift. Their AI is ML forecasting plus optimisation. LLMs are not publicly part of the dispatch loop. Mostly cloud.
- **Residential, C&I and VPP players** (Kraken, gridX, Kiwigrid, Sonnen, Enel X) sell on euros saved, kW flexibility managed and avoided grid fees.
- **LLM-agentic entrants exist but are early and mostly human-in-the-loop.**
  - Sigenergy SigenAgent (June 2026) has four agents. Its Energy Manager plans household strategy and acts only after the user confirms.
  - Proximal Energy uses generative-AI agents for US BESS asset management.
  - Energentic is a research venture on LLM agents for battery dispatch.
  - Tibo Energy (NL) targets grid congestion.
  - None of these publishes audited KPIs.
- **Edge AI platforms** (AWS Greengrass, Siemens Industrial Edge + Azure IoT Operations) now have agent-deployment stories.
  - AWS has official guidance for deploying Strands agents with local SLMs (Ollama) on Greengrass, with fallback to cloud models.
  - Siemens and Azure pitch "closed-loop agentic and physical AI".
  - No edge platform ships an energy-specific agent with an energy KPI framework. That is the white space.
- **Market context.**
  - Generic European EMS market forecasts vary widely: about USD 30–39B by 2030, with a CAGR of 12–15%. No credible sized number was found for BESS optimisation software or edge AI in energy.
  - Italy is a live market: MACSE storage auctions, a growing CER base, and the EU AI Act high-risk date pushed to Dec 2027.

## 2. Competitor table

| Player | Category | AI approach | Edge/Cloud | Published KPIs (vendor-claimed) | Business model | Source |
|---|---|---|---|---|---|---|
| Fluence Mosaic (incl. ex-AMS, Nispera) | Utility BESS bidding | ML forecast + optimisation (stated "AI") | Cloud | Up to 10% more renewables revenue and up to 50% more storage revenue vs. manual bidding; exec claim of 50–100% uplift vs. a human trader; AMS claimed 12% revenue increase | Software licence/optimisation fee, often bundled with BESS (fee structure unverified) | [Fluence](https://fluenceenergy.com/mosaic-intelligent-bidding-software/), [ESN](https://www.energy-storage.news/fluence-goes-digital-with-deal-to-optimise-and-bid-182-5mw-battery-system-into-caiso-markets), [RenewEconomy](https://reneweconomy.com.au/fluence-buys-bidding-software-firm-ams-in-high-speed-push-to-energy-transition-81705/) |
| Stem Athena / PowerTrack | Utility/C&I AI software | ML forecasting + optimisation | Cloud | ERCOT backtest, Stem-published: 28% average revenue uplift over incumbent operators | SaaS plus revenue share (unverified) | [Stem](https://www.stem.com/?p=25574) |
| Tesla Autobidder | Utility BESS trading | Real-time optimisation (method undisclosed) | Cloud | No quantified uplift found | Platform fee/revenue share (unverified) | [Modo directory](https://modoenergy.com/research/en/australia-nem-battery-energy-storage-optimiser-autobidder-directory) |
| Habitat Energy (Bidcast) | Optimiser/trader | ML + trading | Cloud | None found | Revenue share/tolling (unverified) | Modo directory above |
| Octopus Kraken (Flex, residential VPP) | Utility platform / VPP | Optimisation + forecasting, "AI-powered" | Cloud | Over $200M estimated annual consumer savings; about 2 GW of domestic assets managed | SaaS licence to utilities, per-customer-account (unverified) | [Kraken](https://www.kraken.tech/press-releases/residential-vpp-hits-2gw), [EVIN](https://www.evinfrastructurenews.com/ev-technology/ai-powered-vpp-kraken-reaches-2gw-managed-domestic-assets) |
| gridX XENON | White-label EMS (home/C&I/EV) | Rules + optimisation | Edge gateway + cloud | Up to €50k avoided grid-extension costs; up to €600/yr via §14a dynamic grid fees | White-label SaaS plus hardware (unverified) | [gridX](https://www.gridx.ai/product) |
| Kiwigrid | VPP / EMS platform | Optimisation | Cloud, edge-capable (unverified) | Launched a pan-European VPP with Tibber (June 2026); no savings % found | Platform licence | [ESS News](https://www.ess-news.com/2026/06/08/kiwigrid-launches-pan-european-vpp-platform/) |
| Sonnen | Battery OEM + VPP | Rules + optimisation | Edge + cloud | Texas battery-only VPP, up to 10,000 customers planned by end of 2026 | Hardware plus VPP subscription | Same ESS News search; no direct URL |
| Enel X | Aggregator / energy services | Optimisation | Cloud | Aggregated residential storage under a Terna framework (2020 article) | Revenue share/service | [ESN](https://www.energy-storage.news/virtual-power-plants-enel-xs-aggregated-home-storage-goes-into-action-in-it) |
| Schneider EcoStruxure Microgrid Advisor | Microgrid / C&I EMS | Model Predictive Control (confirmed), marketed as AI | Cloud with local controller | 20–30% bill savings (trade-press); 335 tCO2/yr cut and payback within 5 years (South Africa case); over 60% monthly savings at one Australian site | Software subscription plus integration | [Schneider blog](https://perspectives.se.com/blog-stream/how-ai-powers-today-s-advanced-microgrids), [UCS release](https://www.se.com/au/en/about-us/newsroom/news/press-releases/ucs-group-and-schneider-electric-partner-to-deliver-intelligent-microgrid-solutions-across-australia-68ccc4e53c2f21a1520b555a), [AI Magazine](https://publication.aimagazine.com/ai-magazine-december-2025/0908584001763739738/p32) |
| Sigenergy SigenAgent | OEM, LLM agent | Goal-based LLM agents; four agents; user confirms before action | Cloud agent controlling edge hardware (unverified) | None quantified found | Bundled with hardware | [AAP](https://www.aap.com.au/aapreleases/globenewswire9731138/), [pv magazine](https://www.pv-magazine-australia.com/press-releases/sigenergy-unveils-sigenagent-the-first-all-domain-ai-agent-for-the-renewable-energy-industry-2/) |
| Proximal Energy | Startup, agentic BESS asset management | Generative-AI agents | Cloud | Pilot with Excelsior (US); no KPIs found | SaaS (unverified) | [ESN](https://www.energy-storage.news/startup-proximal-energys-ai-agents-to-optimise-excelsior-energy-capitals-us-battery-storage-sites) |
| Tibo Energy, Ogre, Energentic | Startups, AI forecasting and congestion; LLM-agent research | ML; LLM agents (Energentic) | Cloud | None | n/a | [Global Venturing](https://globalventuring.com/corporate/energy-and-natural-resources/8-startups-working-at-the-intersection-of-ai-and-the-energy-sector), [Energentic](https://energentic.github.io) |
| Entrix | AI trading platform, entering Italy for MACSE | ML trading | Cloud | None found | Revenue share (unverified) | [ESS News](https://www.ess-news.com/?p=5501) |
| Siemens, ABB, Hitachi Energy, SMA ennexOS, SolarEdge, Enphase, Next Kraftwerke | Incumbent OEMs / VPP | Rules, optimisation; ML forecasting | Mixed | Not researched in this pass | Mixed | (unverified; no sources retrieved) |

## 3. Scope 1: BESS / energy optimisation software

- **Revenue-uplift claims dominate.** Baselines are manual bidding, a human trader, or a prior operator. Time windows and markets differ. These are not comparable and are not audited.
- **Utility-scale tools are cloud bidding engines.** Their output is the market bid, not asset control. They are not edge-agentic.
- **C&I and residential EMS (gridX, Kiwigrid, Schneider) use MPC or rules,** with cost, tariff and self-consumption objectives. The best measurement practice seen is the case study with a named site and a stated payback.
- **LLM-agentic entrants (2025–2026) are the closest analogues to Sense Reply.**
  - The pattern is a human-confirmed LLM planner on top of deterministic control.
  - Nobody publishes a rigorous evaluation.
  - Sigenergy's "act only after confirmation" design is a notable safety choice. It suggests buyers and regulators are not ready for fully autonomous LLM dispatch.

## 4. Scope 2: Edge/IoT platforms and LLM-agent deployment

- **AWS IoT Greengrass:** official guidance for deploying AI agents to device fleets with Strands Agents and local SLMs via Ollama, with the option to switch to Bedrock cloud models. S3 downloader components distribute model files. Greengrass V1 reaches end of support in Oct 2026 (per a third-party write-up).
  - [AWS guidance](https://aws.amazon.com/solutions/guidance/deploying-ai-agents-to-device-fleets-using-aws-iot-greengrass)
  - [AWS IoT blog](https://aws.amazon.com/blogs/iot/deploying-small-language-models-at-scale-with-aws-iot-greengrass-and-strands-agents)
- **Siemens Industrial Edge + Azure IoT Operations:** models are trained in Azure ML or Foundry and deployed to the edge for inference. Siemens Industrial Copilot is the operator assistant. Siemens lists "closed-loop agentic and physical AI" as a target use. This is vendor marketing.
  - [Siemens architecture hub](https://www.siemens.com/en-gb/content/architecture-hub/azure-iot-operations/)
  - [ARC Advisory](https://www.arcweb.com/blog/siemens-integrates-industrial-edge-microsoft-azure-iot-operations-edge-cloud-ai-simulation)
- **Litmus Edge:** an industrial data layer. It has a Litmus Edge Bridge for Azure IoT Operations. No LLM-agent offering found. [Litmus](https://litmus.io/introducing-litmus-edge-bridge-webinar)
- **Not researched:** Balena, Edge Impulse (Qualcomm), ClearBlade, Cumulocity, Barbara IoT and Azure IoT Edge LLM support. No evidence retrieved. (unverified)
- **Takeaway.** These platforms offer generic agent runtimes and device management. None provides an energy-domain agent catalogue, safety guardrails, or KPI evaluation. Sense Reply's "edge apps store" competes on domain content, not on the runtime.

## 5. Scope 3: KPIs, measurement and pricing patterns

- **KPIs claimed:** revenue uplift %, bill savings %, euros saved per year, avoided grid-extension costs, CO2 tonnes cut, payback years, GW managed.
- **How measured:** mostly not disclosed. The exceptions are Stem's published backtest against incumbents and Schneider's named-site cases.
- **Not found anywhere:** BESS cycling efficiency or degradation-adjusted value, grid-penalty KPIs, confidence intervals, counterfactual methodology, or multi-objective trade-off curves.
- **Pricing models seen or likely:** per-site or per-kW SaaS, revenue share (trading optimisers), white-label licence (gridX, Kraken), and bundled with hardware (Sigenergy, Sonnen). Specific prices were not found. (unverified)

## 6. Scope 4: Market sizing and trends

- **EMS Europe (generic):** forecasts vary by source.
  - About USD 14.9B in 2024 growing at 12.4% CAGR to USD 30.3B by 2030 (PS Market Research).
  - About USD 19.6B in 2025 growing at 14.6% to USD 38.8B by 2030 (another report).
  - Scopes mix BEMS, HEMS and hardware. Methodologies are unchecked. Treat them as order-of-magnitude figures only.
  - [PS Market Research](https://psmarketresearch.com/market-analysis/europe-energy-management-systems-market)
  - [Mordor via MarketResearch](https://marketresearch.com/Mordor-Intelligence-LLP-v4018/Europe-Energy-Management-Systems-Share-36223358)
  - [Straits](https://straitsresearch.com/report/europe-energy-management-systems-market)
- **HEMS software:** one source cites a 22% CAGR for 2023–2028.
- **BESS optimisation software and edge AI in energy:** no credible sized figure found. State this as a gap. The EU storage capacity driver is cited at about 187 GW by 2030 (unverified, from the same research firms).
- **Italy BESS:** MACSE gives a 15-year tolling-style contract with the TSO and targets roughly 8-hour systems, mostly in the south. The northern zone uses the capacity market. Early tariffs surprised the market and need careful asset management. About 1 GW of grid-scale BESS was online in March 2025. Pipelines are large, for example ContourGlobal's 1.6 GW / up to 9.5 GWh.
  - [Rabobank](https://www.rabobank.com/knowledge/d011473382-backup-power-for-europe-part-3-italy-s-bet-on-bess)
  - [ESN MACSE](https://www.energy-storage.news/bess-industry-gears-up-italy-market-kick-off-first-macse-auction-2030-target-overly-ambitious/)
  - [ESN ContourGlobal](https://www.energy-storage.news/?p=82167)
- **Italy CER:**
  - The PNRR allocation was cut from EUR 2.2B to EUR 795.5M after the sixth PNRR revision. Press reporting only; check GSE and MASE.
  - GSE reports about 3,630 configurations and 302.9 MW at 30 June 2026, and over 4,800 configurations and about 400 MW at 31 August 2026.
  - The DM 414/2023 tariff incentive runs to 31 Dec 2027. Industry is lobbying for an extension to 2030.
  - [MASE results](https://greencam.unioncamere.it/wp-content/uploads/2026/02/Le-CER-risultati-della-misura-PNRR-e-possibili-sviluppi-futuri_MASE.pdf)
  - [Italia Solare, 11 Jun 2026](https://www.italiasolare.eu/wp-content/uploads/2026/06/20260611_cs-su-riduzione-fondi-per-le-cer.pdf)
  - [Infobuild](https://www.infobuildenergia.it/approfondimenti/cer-comunita-energetiche-in-italia/)
- **EU AI Act:** the Digital Omnibus moved Annex III high-risk obligations from 2 Aug 2026 to 2 Dec 2027. This covers AI used as a safety component in managing electricity, gas, water and heat supply. Systems embedded in regulated products (Annex I) move to 2 Aug 2028.
  - One source says the amending Regulation (EU) 2026/1744 entered into force on 27 Jul 2026. Sources disagree on some dates, so verify on EUR-Lex.
  - Applicability depends on the system's function, not on the operator's status. NIS2 and the CER Directive still apply in full. Implication: an LLM agent dispatching assets at critical-infrastructure scale needs risk management, logging, human oversight and accuracy documentation. A residential battery is likely out of scope.
  - [CSA note](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-omnibus-vii-deadline-delay-20260/)
  - [Travers Smith](https://www.traverssmith.com/knowledge/knowledge-container/eu-agrees-to-delay-key-ai-act-compliance-deadlines/)
  - [Bayern Innovativ](https://www.bayern-innovativ.de/en/emagazine/detail/eu-postpones-ai-regulations-for-critical-infrastructure)
- **Other trends:**
  - Grid-fee dynamics: gridX cites Germany's §14a dynamic grid fees.
  - Pan-European VPPs: Kiwigrid launched one with Tibber.
  - Residential VPP scale: Kraken at about 2 GW.
  - Curtailment: Kiwigrid cites about 5% of German generation curtailed in 2025.
  - A European VPP market size and dynamic-tariff penetration were not found. (unverified)

## 7. Scope 5: White space for an edge-agentic platform from Reply

1. **Evidence gap.** Competitors give headline savings with no method. A platform that ships a standard, auditable evaluation (counterfactual baselines, multi-KPI reporting) would be differentiated.
2. **Edge plus LLM plus energy domain.** Hyperscalers provide runtimes only. Energy OEMs provide cloud agents with human confirmation. Few combine edge protocol translation (Modbus, OPC-UA) with a catalogue of vetted energy agents. (Barbara, Cumulocity and Balena were not checked.)
3. **Multi-objective arbitration.** The cost, sustainability and orchestrator pattern is an explicit trade-off mechanism. No competitor publishes multi-objective Pareto results.
4. **Consultancy advantage.** Vendor-neutral integration, regulatory fluency (AI Act, CER, MACSE) and client-specific KPI baselining.
5. **Risks.**
   - LLM latency and cost for real-time control, so keep deterministic safety limits at the edge.
   - Buyers favour human-confirmed actions.
   - Incumbent OEMs bundle for free.
   - Regulatory exposure at critical-infrastructure scale.

**Evidence buyers expect (inferred from the competitors' own claims; buyer interviews not done):** a clear baseline, a named-site case study, payback, a backtest on public price data, euros per kWh and per kW, CO2 tonnes, and independent verification.

## 8. Benchmarks our KPIs should be compared against

| Our KPI | Benchmark from the market | Caveat |
|---|---|---|
| Energy cost reduction | Schneider 20–30% bill savings (trade press); 60%+ at one site; Sunsave claims at least GBP 180 extra in year one | Baselines differ; single-site claims |
| Revenue / value uplift | Stem 28% over incumbents; Fluence up to 10% (renewables) and up to 50% (storage) vs. manual bidding; AMS 12% | Utility trading, not behind-the-meter |
| Grid penalties / fees | gridX up to EUR 600/yr (§14a) and up to EUR 50k avoided grid extension | German context |
| Self-consumption | No published % found from the checked vendors | Use a no-battery baseline and a rule-based baseline |
| BESS cycling efficiency | None published by competitors | Our differentiator; use throughput per EUR and degradation-adjusted value |
| Emissions | Schneider 335 tCO2/yr (one site) | Specify the emission factor method |
| Trade-offs | None published | Present cost-vs-CO2 frontier curves |

Recommended internal baselines: no-control, rule-based and MPC/MILP optimum with perfect foresight. The perfect-foresight run provides the "% of achievable value captured" metric competitors do not show.

## 9. Positioning implications

- Lead with auditable, transparent KPI reporting rather than another "up to X%".
- Keep deterministic safety limits at the edge and use the LLM for planning and arbitration. This is consistent with the market's human-confirmation norm and the AI Act's direction.
- Position the "edge apps store" as domain content on top of the AWS and Azure runtimes, not as a competing runtime.
- Prepare an AI Act dossier (risk management, logging, oversight) before Dec 2027 for any critical-infrastructure-scale use.
- Italian hooks: CER energy communities (funding is uncertain after the PNRR cut) and MACSE-driven BESS asset management.
- Still to verify: pricing, the Siemens, ABB, Hitachi, SMA, SolarEdge, Enphase and Next Kraftwerke offerings, Barbara, Cumulocity, ClearBlade and Balena LLM support, and sized BESS-software and VPP markets.

## 10. References

All URLs are inline above. Key search-derived sources:
- https://fluenceenergy.com/mosaic-intelligent-bidding-software/
- https://www.stem.com/?p=25574
- https://www.kraken.tech/press-releases/residential-vpp-hits-2gw
- https://www.gridx.ai/product
- https://www.ess-news.com/2026/06/08/kiwigrid-launches-pan-european-vpp-platform/
- https://perspectives.se.com/blog-stream/how-ai-powers-today-s-advanced-microgrids
- https://www.aap.com.au/aapreleases/globenewswire9731138/
- https://www.energy-storage.news/startup-proximal-energys-ai-agents-to-optimise-excelsior-energy-capitals-us-battery-storage-sites
- https://aws.amazon.com/solutions/guidance/deploying-ai-agents-to-device-fleets-using-aws-iot-greengrass
- https://www.siemens.com/en-gb/content/architecture-hub/azure-iot-operations/
- https://psmarketresearch.com/market-analysis/europe-energy-management-systems-market
- https://www.rabobank.com/knowledge/d011473382-backup-power-for-europe-part-3-italy-s-bet-on-bess
- https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-omnibus-vii-deadline-delay-20260/
- https://greencam.unioncamere.it/wp-content/uploads/2026/02/Le-CER-risultati-della-misura-PNRR-e-possibili-sviluppi-futuri_MASE.pdf
