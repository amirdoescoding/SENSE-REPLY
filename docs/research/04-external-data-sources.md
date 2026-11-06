# 04 – External data sources for the Sense Reply business case

Prepared Nov 2026.

Verification policy: a number is stated plainly only if I saw it in a retrieved source or it is arithmetic on the case data. Everything else is marked "(unverified)". Several primary sources (the GME PDF, the Mistral price chart, ISPRA tables, the ENTSO-E API) could not be read in this session. No ENTSO-E, Terna or Electricity Maps values for 5–12 Jan 2026 were retrieved, so item 1 gives the method and endpoints, not the numbers.

---

## 0. Executive summary

1. **Carbon series.** The most reliable route is the ENTSO-E Transparency Platform. Pull "Actual Generation per Production Type" (A75) for Italy, 2026-01-05 to 2026-01-12. Multiply each technology's MWh by an IPCC AR5 lifecycle factor and divide by total generation. That gives an hourly average-intensity series.
   - Electricity Maps' general CSV datasets appear to have been sunset. The older portal text says 2021–2024 coverage, so 2026 is not covered. Academic access may remain (see 1.2).
   - Marginal intensity is not published by these sources. It has to be approximated.
   - Fallbacks: RTE éCO2mix gives France with a ready-made g/kWh at 15 min. Energy-Charts (Fraunhofer ISE) is an alternative for Germany.
2. **LLM cost.** On the Devstral 2 list price of $0.40 in / $2.00 out per 1M tokens (secondary sources, not Mistral's own chart):
   - Config A costs **$5.51** for the week and config B **$9.56**.
   - That is about $0.79 and $1.37 per day.
   - Per 15-min decision it is about $0.0082 (A) and $0.0142 (B).
   - Per request it is about $0.00187 (A) and $0.00175 (B).
   - The Sustainability agent adds about $4.05 per week (+73%). It nearly doubles requests (2,948 → 5,472) but costs less per request.
   - Inference cost is negligible compared with the energy bill of a home. Self-hosting a 123B model is not economical at this volume.
3. **Price sanity check.** The data's buyPrice of 0.11538 €/kWh is almost exactly the Switcho-reported PUN for "January 2026" (0.1155 €/kWh). It is far below a full residential retail price.
   - So buyPrice looks like a PUN-like or energy-only price, not an all-in tariff (inference).
   - The Switcho figure conflicts with another source (see §3).
4. **Battery wear.** A 10 kWh LFP battery has a typical wear cost of about €0.06–0.15 per kWh discharged (about €0.5–1.2 per full cycle). Both figures are assumption-based (unverified).
   - The buy/sell spread in the data is only about €0.025/kWh (0.11538 − 0.09). Grid arbitrage therefore cannot cover degradation.
   - Battery value must come from self-consumption of PV, which avoids buying at 0.115 versus selling at 0.09.
5. **Comparators.** Ausgrid Solar Home, CityLearn, Pecan Street and OPSD household data are the usable public references. Details are in §5.

---

## 1. Grid carbon intensity (TOP PRIORITY)

### 1.1 Average vs marginal

- **Average (attributional) intensity** is total emissions of the generation mix divided by total generation. ENTSO-E A75 plus emission factors, Electricity Maps and RTE éCO2mix all provide this.
- **Consumption-based intensity** adds emissions embedded in imports. Italy imports roughly 15% of its demand (unverified). It needs ENTSO-E cross-border flows (document A11) combined with neighbours' mixes. Electricity Maps does this natively.
- **Marginal intensity** is the emissions of the plant that would change output. No free public hourly series exists.
  - A proxy is the intensity of the dispatchable marginal fuel. In Italy this is almost always gas CCGT, about 350–490 gCO2/kWh (unverified), so a flat ~400 is a reasonable proxy.
  - WattTime sells marginal data (MOER). Its free tier is limited (unverified).
- **Recommendation for the case.** Use average intensity as the main series, and run a sensitivity with a flat gas-marginal factor.

### 1.2 Sources

| Name | What | Resolution | Access | Licence | URL |
|---|---|---|---|---|---|
| ENTSO-E Transparency Platform, Actual Generation per Production Type (A75) | Italy MW by technology; compute intensity yourself | Typically 60 min for Italy (unverified; 15 min exists for some areas) | Free account, then request a REST token by email; or `entsoe-py` | ENTSO-E terms: free reuse with attribution (unverified) | https://transparency.entsoe.eu ; API: https://web-api.tp.entsoe.eu/api |
| ENTSO-E, Physical flows (A11) | Cross-border flows for consumption-based intensity | 60 min | Same API | Same | same |
| Terna Transparency Report / Download Center | Italian generation by source, load, exchanges | Hourly or 15 min (unverified) | Download centre or developer API portal (registration) | Terna open-data terms (unverified) | https://www.terna.it/en/electric-system/transparency-report ; https://developer.terna.it |
| Electricity Maps Data Portal | Hourly carbon intensity, renewable % and CFE % for IT-North, IT-Centre-North, IT-Centre-South, IT-South, IT-Sicily and IT-Sardinia | Hourly | Free account CSV. Portal text says coverage 2021–2024, and a help-centre article says general datasets are sunset (academic access remains). Confirm before relying on it. | ODbL (attribution and share-alike) | https://portal.electricitymaps.com/datasets ; https://help.electricitymaps.com/en/articles/13168512-academic-data-access-and-availability |
| Electricity Maps API | Latest and recent carbon intensity | Hourly | Free tier is non-commercial. Historical range is limited, likely about 24 h (unverified). | Proprietary ToS | https://www.electricitymaps.com |
| ISPRA national emission factors for electricity | Annual national gCO2/kWh, production and consumption (SINA) | Annual | PDF reports and datasets | Public (Italian open data, unverified) | https://emissioni.sina.isprambiente.it ; https://www.isprambiente.gov.it/it/pubblicazioni/rapporti/settore-elettrico-emissioni-di-co2-e-altri-impatti-edizione-2026 |
| Ember | Monthly and yearly European electricity data, with carbon intensity | Monthly or yearly | Free download | CC BY 4.0 (unverified) | https://ember-energy.org/data/ |
| RTE éCO2mix (France) | Production per type plus ready-made CO2 rate (g/kWh) | 15 min | Open API / CSV on ODRÉ | Etalab open licence (unverified) | https://odre.opendatasoft.com (dataset "eco2mix-national-tr" and "-cons-def") |
| Energy-Charts (Fraunhofer ISE) | Germany, and several countries including Italy, generation per type | 15 min or hourly | Free API | CC BY 4.0 (unverified) | https://api.energy-charts.info |

Italian data coverage in the sources I saw:
- The Electricity Maps portal lists six Italian zones with hourly granularity.
- The ISPRA 2026 edition covers 1990–2024. I did not retrieve its numbers.
- A Climatiq entry shows 271.6 g/kWh for Italy, but its year is unclear (unverified).

### 1.3 Concrete download steps (ENTSO-E)

1. Register at transparency.entsoe.eu. Email transparency@entsoe.eu asking for "Restful API access". Then take the token from "My Account Settings → Web API Security Token".
2. Request (all times UTC, format YYYYMMDDHHMM). Cover the whole case week: 11:00 local on 5 Jan = 10:00 UTC, through 10:45 local on 12 Jan = 09:45 UTC. Pull a margin around it.
   ```
   GET https://web-api.tp.entsoe.eu/api?securityToken=TOKEN
     &documentType=A75&processType=A16
     &in_Domain=10YIT-GRTN-----B
     &periodStart=202601050900&periodEnd=202601121100
   ```
   The result is XML with one TimeSeries per `psrType`.
3. `psrType` codes: B01 biomass, B04 fossil gas, B05 hard coal, B06 fossil oil, B09 geothermal, B10 hydro pumped storage, B11 hydro run-of-river, B12 hydro reservoir, B14 nuclear, B16 solar, B17 waste, B18 wind offshore, B19 wind onshore, B20 other.
4. Python shortcut:
   ```python
   from entsoe import EntsoePandasClient
   import pandas as pd
   c = EntsoePandasClient(api_key=TOKEN)
   df = c.query_generation('IT', start=pd.Timestamp('2026-01-05', tz='Europe/Rome'),
                           end=pd.Timestamp('2026-01-13', tz='Europe/Rome'))
   ```
5. Compute:
   - Intensity(t) = Σ (generation_i(t) × EF_i) / Σ generation_i(t).
   - Resample to 15 min by forward-fill if the source is hourly.
   - Convert the timestamps to the dataset's time zone. The case timestamps' time zone is unknown, so check it.
   - Remove pumped-storage consumption: use only generation, not the negative values.
6. Other bidding zones:
   - France: `10YFR-RTE------C`.
   - Germany-Luxembourg: `10Y1001A1001A83F`.
   - Italy sub-zones, if needed: IT-North `10Y1001A1001A73I`, IT-Centre-North `10Y1001A1001A70O`, IT-Centre-South `10Y1001A1001A71M`, IT-South `10Y1001A1001A788`, IT-Sicily `10Y1001A1001A75E`, IT-Sardinia `10Y1001A1001A74G` (EIC codes from memory, unverified).

### 1.4 Lifecycle emission factors (gCO2eq/kWh)

IPCC AR5 WG3 Annex III (Schlömer et al. 2014) median lifecycle values. These are from memory (unverified); check against the Annex before citing. Electricity Maps uses a very similar set, which keeps results comparable.

| Technology | EF | Technology | EF |
|---|---|---|---|
| Hard coal | 820 | Hydro | 24 |
| Fossil gas (CCGT) | 490 | Nuclear | 12 |
| Fossil oil | 650 | Wind onshore | 11 |
| Biomass | 230 | Wind offshore | 12 |
| Geothermal | 38 | Solar PV (utility) | 48 (rooftop 41) |
| Waste | about 700 ("unknown" proxy; unverified) | Other / unknown | about 700 (unverified) |

ISPRA alternative: ISPRA reports direct (combustion) CO2 factors for fossil fuels rather than lifecycle values for renewables. Using it means ignoring lifecycle emissions of PV, wind and hydro, which gives a lower and more "Italian-official" figure. State the choice explicitly in the report.

### 1.5 Expected January 2026 values (not retrieved)

No January 2026 intensity values could be retrieved. Rough expectations, all (unverified):
- Italy: daily range about 200–400 gCO2/kWh. The minimum is around midday sun or windy nights. The maximum is the evening peak with gas on the margin.
- France: about 30–80.
- Germany: about 250–550.

Replace these with computed values before presenting.

### 1.6 Recommended data to pull and how

1. Primary: ENTSO-E A75 for Italy (country code `IT`), 2026-01-05 to 2026-01-13, with the table in 1.4. Cache the XML or CSV in the repo.
2. Alternative locations: France via RTE éCO2mix (no computation needed), Germany via ENTSO-E `DE_LU` or Energy-Charts.
3. Optional cross-check: Electricity Maps academic CSV if available; compare daily means.
4. Sensitivity: flat marginal factor 400 (gas), plus ISPRA annual average as a constant baseline.
5. Join to the case data on timestamp, then emissions per interval = grid import kWh × intensity.
6. Keep the "location assumed Italy" flag visible in every figure.

---

## 2. Mistral Devstral 2 pricing and inference cost

### 2.1 Price sources

| Name | What | Resolution | Access | Licence | URL |
|---|---|---|---|---|---|
| Mistral pricing page | Plans and API policy: batch 50% off, cached input up to 90% off. Per-model chart not readable. | per 1M tokens | Web | n/a | https://mistral.ai/pricing |
| Aggregators (pi.dev, Inworld, PriceperToken) | Devstral 2: $0.40 input / $2.00 output per 1M (cache read $0.04 per pi.dev) | per 1M tokens | Web | n/a | https://pi.dev/models/mistral/devstral-latest ; https://inworld.ai/models/mistral-devstral-2 ; https://pricepertoken.com/pricing-page/model/mistral-ai-devstral-2-123b |
| PriceperToken (variant page) | Outlier: $0.40 / $0.90 for the "2512" variant | per 1M tokens | Web | n/a | https://pricepertoken.com/pricing-page/model/mistral-ai-devstral-2512 |
| Vercel listing via ModelCompare | Devstral Small 2: $0.10 / $0.30 per 1M. Other sources conflict (some show $0). | per 1M tokens | Web | n/a | https://modelcompare.dev/fr/models/vercel/devstral-small-2 |

- Devstral 2 at $0.40 / $2.00 is consistent across most sources but not confirmed on Mistral's own chart.
- Devstral Small 2 at $0.10 / $0.30 is (unverified).
- Ministral and Mistral Medium list prices: not retrieved (unverified). The only primary data point I saw is Mistral Large at $0.5 / $1.5 per 1M, used as an example in Mistral's FAQ. Check https://docs.mistral.ai/getting-started/models for current rates.
- Self-hosting: Devstral 2 (123B) needs multi-GPU hardware, about 4× H100-class (unverified). Its licence is a modified MIT with a revenue cap (unverified). Devstral Small 2 (24B) is Apache 2.0 and runs on one GPU (unverified).
- Other hosts: Vercel AI Gateway, Inworld (see table), and EU clouds (unverified).
- Currency: prices are in USD. A EUR conversion needs a stated rate (unverified).

### 2.2 Worked calculation

Assumed rate: input $0.40/M, output $2.00/M. Seven days; 672 samples in A, 671 in B.

**Config A** (2,948 requests; 11,690,688 in; 418,362 out)
- Input: 11,690,688 / 1,000,000 × 0.40 = 11.690688 × 0.40 = **$4.6763**
- Output: 0.418362 × 2.00 = **$0.8367**
- Total: 4.6763 + 0.8367 = **$5.5130**
- Per day: 5.5130 / 7 = **$0.7876**
- Per decision: 5.5130 / 672 = **$0.008204**
- Per request: 5.5130 / 2,948 = **$0.001870**

**Config B** (5,472 requests; 20,049,658 in; 770,858 out)
- Input: 20.049658 × 0.40 = **$8.0199**
- Output: 0.770858 × 2.00 = **$1.5417**
- Total: 8.0199 + 1.5417 = **$9.5616**
- Per day: 9.5616 / 7 = **$1.3659**
- Per decision: 9.5616 / 671 = **$0.014249**
- Per request: 9.5616 / 5,472 = **$0.001747**

**Delta (cost of the Sustainability agent):** 9.5616 − 5.5130 = **$4.0486 per week**, which is +73.4%. Per day it is $0.578.

**Derived ratios**
- Requests per decision: A = 2,948 / 672 = 4.39. B = 5,472 / 671 = 8.16.
- Tokens per request: A has 3,966 in and 142 out. B has 3,664 in and 141 out.
- Input tokens make up about 85% of cost at these rates, so caching is the main lever.

**Sensitivities**
- Devstral Small 2 at $0.10 / $0.30 (unverified): A = 1.1691 + 0.1255 = **$1.2945**. B = 2.0050 + 0.2313 = **$2.2363**.
- Cached input at 90% off (input cost × 0.1; assumes every input token is cacheable, which is an upper bound): A ≈ 0.4676 + 0.8367 = **$1.304**. B ≈ 0.8020 + 1.5417 = **$2.344**.
- Batch at 50% off is not suitable for real-time control, but it works for offline replay.
- Self-hosting, assumed 4 GPUs at about $2.5/GPU-hour (assumption) = $10/h × 168 h = **about $1,680 per week** for always-on hosting. That is roughly 300× the API cost for A. It is only worth it for data-residency reasons.

### 2.3 Recommended data to pull and how

1. Read the live per-model table at https://docs.mistral.ai/getting-started/models and confirm Devstral 2 rates. Record the date.
2. Reuse the formulas above in a spreadsheet with price as an input.
3. Report cost with the energy bill saved, for example "€ saved per € of inference".

---

## 3. Italian electricity prices, January 2026

### 3.1 Sources

| Name | What | Resolution | Access | Licence | URL |
|---|---|---|---|---|---|
| GME Mercato Elettrico (MGP) | Day-ahead PUN and zonal prices (NORD, CNOR, CSUD, SUD, SICI, SARD) | Hourly (15-min day-ahead from late 2025, unverified) | Free registration; XML/Excel downloads; monthly summary PDF | GME terms (unverified) | https://gme.mercatoelettrico.org ; Jan 2026 summary https://gme.mercatoelettrico.org/Portals/0/Documents/it-IT/202601_Dati_di_sintesi_mensile.pdf (PDF not readable in my session) |
| Comparasemplice daily PUN | Daily PUN and running monthly average (secondary) | Daily | Web | n/a | e.g. https://www.comparasemplice.it/informazioni/news/pun-aggiornamento-del-29-01-2026 |
| Switcho | "PUN January 2026" article | Monthly | Web | n/a | https://www.switcho.it/blog/?p=146732 |
| ARERA | Regulated components, F1/F2/F3 definitions, tariff updates | Quarterly | Web | n/a | https://www.arera.it |
| GSE Ritiro Dedicato | Buy-back of PV energy | Hourly zonal price, and minimum guaranteed prices for small plants | GSE site | n/a | https://www.gse.it |

### 3.2 Findings and conflicts

- **PUN January 2026 conflicts across sources.**
  - Switcho reports 0.1155 €/kWh (about 115.5 €/MWh), −1% vs December and −14% vs January 2025.
  - Comparasemplice's running monthly average stood at 146.01 €/MWh on 29 Jan.
  - Segugio says January set a new peak.
  - The Switcho number and the 146 €/MWh average cannot both be January's average. Take the official value from the GME monthly summary, because I could not confirm it.
- **Link to the data:** buyPrice 0.11538 €/kWh is very close to 0.1155. The case price is probably PUN-linked energy-only, not a household all-in tariff. Test whether buyPrice varies by time. If it is constant, it is an assumption; if it follows F-bands or hourly prices, it is a market price.
- **Residential all-in tariff** (energy + network + system charges + taxes + VAT) is typically about €0.25–0.35/kWh (unverified).
- **F-bands (ARERA standard):**
  - F1: Mon–Fri 08:00–19:00, excluding holidays.
  - F2: Mon–Fri 07:00–08:00 and 19:00–23:00, plus Saturday 07:00–23:00.
  - F3: Mon–Sat 23:00–07:00, plus Sundays and national holidays all day.
  - Check the case week: **6 Jan 2026 is Epiphany, a national holiday, so it is F3 all day.** The week also contains one Sunday (11 Jan).
- **Ritiro Dedicato / feed-in:**
  - I could not retrieve official 2026 minimum guaranteed prices (unverified).
  - A solar vendor blog claims 8–14 ct/kWh but it is commercial and unverified.
  - sellPrice 0.09 €/kWh is plausible for RID at roughly PUN-minus-fees, but treat it as an assumption until confirmed.
  - Scambio sul posto is being phased out for new plants (unverified).

### 3.3 Recommended data to pull and how

1. Download the January 2026 MGP results from GME (hourly PUN and zones). Compute weekly mean, min and max for 5–12 Jan.
2. Compare to buyPrice: correlation with PUN means market-indexed; flat means fixed.
3. Pull the GSE RID rule for ≤ 1 MW plants and the 2026 minimum price table.
4. Present both the case prices and a retail-tariff scenario (about €0.30 buy). The ranking of strategies may change.

---

## 4. Battery degradation cost benchmarks (10 kWh LFP)

### 4.1 Benchmarks (all unverified; no sources retrieved this session)

| Parameter | Typical value |
|---|---|
| LFP cycle life | 4,000–8,000 cycles to 70–80% capacity at 80–100% DoD, 25 °C. Many warranties state about 6,000 cycles and 10 years. |
| Installed residential cost, Italy | about €500–900/kWh, so about €5,000–9,000 for 10 kWh (before the 50% Italian tax deduction, if any applies). |
| Calendar ageing | about 1–2% per year |

Check against current manufacturer warranty datasheets (BYD, Pylontech, Huawei, Sungrow) and https://atb.nrel.gov (NREL ATB, public-domain data).

### 4.2 Formulas and worked example

- Throughput over life = cycles × capacity × DoD. Example: 6,000 × 10 kWh × 0.8 = 48,000 kWh discharged.
- Degradation cost per kWh = capex / lifetime throughput.
- Cost per equivalent full cycle (EFC) = capex / cycles.

| Capex | Cycles | €/kWh discharged | € per full cycle (10 kWh) |
|---|---|---|---|
| €4,000 | 6,000 | 0.083 | 0.67 |
| €6,000 | 6,000 | 0.125 | 1.00 |
| €9,000 | 6,000 | 0.188 | 1.50 |
| €6,000 | 8,000 | 0.094 | 0.75 |

Capex-based cost is an upper bound. A residual-value or second-life credit would lower it.

**Implication for the case.** The data's price spread is about 0.025 €/kWh, so arbitrage does not pay unless degradation is priced very low. The dataset reports soc, soh and temperature, so the actual SoH loss over the week can be used to estimate degradation directly. Expect it to be tiny over one week, which means a modeled cost per kWh is needed.

### 4.3 Recommended data to pull and how

1. Pull two or three datasheets for 10 kWh LFP packs for cycle life and warranty throughput.
2. Pull the NREL ATB residential storage cost.
3. Sum BESS discharged energy per config from the data and compute degradation cost = discharged kWh × €/kWh. Do this at a low, central and high rate.

---

## 5. Public reference datasets for home EMS benchmarking

| Name | What | Resolution | Access | Licence | URL |
|---|---|---|---|---|---|
| Ausgrid Solar Home Electricity Data | 300 Sydney homes with rooftop PV: consumption and PV generation, 2010–2013 | 30 min | Free download (Excel/CSV) | Ausgrid open data terms (unverified) | https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Solar-home-electricity-data |
| CityLearn | RL environment for building energy and demand response with PV and battery; includes datasets | 1 h | GitHub / pip | MIT (unverified) | https://github.com/intelligent-environments-lab/CityLearn |
| Pecan Street Dataport | Home-level data for US homes with circuit-level load, PV, EV and batteries | 1 min (some 15 min) | Free for university researchers (application); paid for commercial | Proprietary | https://www.pecanstreet.org/dataport/ |
| Open Power System Data, household data | German households' load and PV, with some heat pumps | 1 min, 15 min, 60 min | Direct CSV download | CC BY 4.0 (unverified) | https://data.open-power-system-data.org/household_data/ |
| Smart* UMass, REFIT, UK-DALE | Household load datasets (US/UK), no PV in most | 1 s – 1 min | Free | various | https://traces.cs.umass.edu/ ; https://www.refitsmarthomes.org (UK-DALE and REFIT) |

Use: compare load shape and PV/load ratio to the case, then replay the case's price and carbon signals on these load profiles as a robustness test. Ausgrid and OPSD are fully open and need no approval. Pecan Street needs lead time to get access.

---

## 6. Unverified or conflicting items

- The Devstral 2 price comes from secondary sources. A PriceperToken page shows a different output price ($0.90) for the 2512 variant.
- Small 2, Ministral and Medium prices are not confirmed.
- Jan 2026 PUN: conflicting sources (115.5 vs 146 €/MWh running average).
- Ritiro Dedicato 2026 values were not retrieved.
- All emission factors, EIC codes, and January 2026 intensity ranges are from memory.
- Electricity Maps 2026 historical availability is unclear (portal says 2021–2024; help centre says general datasets sunset).
- Battery cycle life and capex are from memory and untested against datasheets.

## 7. References

- ENTSO-E Transparency Platform: https://transparency.entsoe.eu ; API: https://web-api.tp.entsoe.eu/api
- Terna: https://www.terna.it/en/electric-system/transparency-report ; https://developer.terna.it
- Electricity Maps portal and help: https://portal.electricitymaps.com/datasets ; https://help.electricitymaps.com/en/articles/13168512-academic-data-access-and-availability ; https://electricitymaps.com/terms-of-use
- ISPRA: https://www.isprambiente.gov.it/it/pubblicazioni/rapporti/settore-elettrico-emissioni-di-co2-e-altri-impatti-edizione-2026 ; https://emissioni.sina.isprambiente.it/wp-content/uploads/2025/05/Le-emissioni-di-CO2-nel-settore-elettrico_r413-2025_def.pdf
- Ember: https://ember-energy.org/data/
- RTE éCO2mix: https://odre.opendatasoft.com
- Energy-Charts: https://api.energy-charts.info
- IPCC AR5 WG3 Annex III (Schlömer et al. 2014): https://www.ipcc.ch/report/ar5/wg3/
- Mistral: https://mistral.ai/pricing ; https://docs.mistral.ai/getting-started/models
- Devstral price aggregators: https://pi.dev/models/mistral/devstral-latest ; https://inworld.ai/models/mistral-devstral-2 ; https://pricepertoken.com/pricing-page/model/mistral-ai-devstral-2-123b ; https://pricepertoken.com/pricing-page/model/mistral-ai-devstral-2512 ; https://modelcompare.dev/fr/models/vercel/devstral-small-2
- GME: https://gme.mercatoelettrico.org ; Switcho https://www.switcho.it/blog/?p=146732 ; Comparasemplice https://www.comparasemplice.it/informazioni/news/pun-aggiornamento-del-29-01-2026
- GSE: https://www.gse.it ; ARERA: https://www.arera.it
- NREL ATB: https://atb.nrel.gov
- Ausgrid: https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Solar-home-electricity-data ; CityLearn: https://github.com/intelligent-environments-lab/CityLearn ; Pecan Street: https://www.pecanstreet.org/dataport/ ; OPSD: https://data.open-power-system-data.org/household_data/
