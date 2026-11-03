# Findings

Following the proposal, each finding is labeled as one of these:

- **Measured:** a trend or pattern the data show directly.
- **Hypothesis:** a possible explanation the data are consistent with but don't prove.
- **Insufficient data:** a question the available records can't answer yet.

Every finding below comes from a chart on the [Analysis](analysis.md) page, and every number is computed from the data by that chart's code.

## Bottom line

**Are the available records enough to evaluate the concern that Cuba's main aquifer is approaching severe depletion? No: they can't confirm it or rule it out (Insufficient data).** Wells near Cuba have only one-time water levels from aquifer tests done between 1957 and 1979, and the nearest well measured more than once is about 38 km away. Answering the question needs Cuba's municipal well records: well IDs, the formation each well uses, pumping volumes, and water-level history.

Elsewhere in the county, where wells are monitored, the picture is mixed. Five of the nine USGS monitoring wells between Rio Rancho and Cochiti fell over their records, and the Lincoln Middle School and Dome Road wells were still falling in 2016-2025. At the Sandia site the water level has risen about 13 ft since 2007. These are indicators at four sites, not a county-wide measure of how much water is left.

| Research question | Short answer | Label |
|---|---|---|
| 1. Groundwater-level trends | Declines at Rio Rancho, Bernalillo, and Dome Road; recovery at the Sandia site; mixed changes at five re-measured Placitas wells | Measured |
| 2. Wells and aquifer units | Where water is deeper, wells are drilled deeper, with a wide spread; within some formations, aquifer properties vary more than between formations | Measured |
| 3. Groundwater near Cuba | Only one-time aquifer tests (1957-1979) and one well log within 25 km; no repeated water-level record near Cuba, so the depletion concern can't be evaluated | Insufficient data |
| 4. Ojo Alamo vs San Jose | Too few tests (1953-1977) to compare; the one San Jose test matches published values; on the USGS map the Ojo Alamo is shallow at Cuba | Insufficient data |
| 5. Coverage and gaps | Monitoring is concentrated along the Rio Grande; the northwest, around Cuba, has none | Measured |
| 6. Stress indicators | Five indicators are listed on the app's Data sources page, each with where it applies and how much to trust it | Measured |

The proposal's questions on groundwater quality, acequias, and groundwater-surface water links were dropped because the data weren't collected (see [Not collected](data-collection.md#not-collected)). The Rio Puerco visits at Cuba appear under the Cuba case study as surface-water context only.

<!-- BEGIN GENERATED: findings by topic -->
<!-- Written by `python -m analysis.write_docs`; edit the chart code, not this block. -->

## Groundwater levels

Research question 1.

- **Measured:** Full-record trends (Mann-Kendall p < 0.05): falling: all 3 at Lincoln Middle School; Bernalillo site Well; Dome Road well; rising: Bernalillo site Well A; Sandia site Well, Sandia site Well A; 1 with no clear trend. *(chart 2: [groundwater_hydrographs](analysis.md#2-groundwater_hydrographs))*
- **Measured:** At the Sandia site the water level fell until 2007, then rose about 13 ft by 2025. *(chart 2: [groundwater_hydrographs](analysis.md#2-groundwater_hydrographs))*
- **Measured:** Full-record trends at Lincoln Middle School: -0.40 to -0.36 ft/yr (water table falling). *(chart 3: [groundwater_trends](analysis.md#3-groundwater_trends))*
- **Measured:** Bernalillo site main well: -0.52 ft/yr over the full record, no clear trend in 2016-2025. *(chart 3: [groundwater_trends](analysis.md#3-groundwater_trends))*
- **Measured:** Sandia site well: +0.57 ft/yr over the full record and +0.72 ft/yr in 2016-2025. *(chart 3: [groundwater_trends](analysis.md#3-groundwater_trends))*
- **Measured:** 3 of 5 re-measured wells are within 5 ft of their 1997-1998 average. *(chart 4: [placitas_remeasured](analysis.md#4-placitas_remeasured))*
- **Measured:** PC-014 is 51 ft deeper than in 1997-1998 (well 420 ft deep; 1 recent reading). *(chart 4: [placitas_remeasured](analysis.md#4-placitas_remeasured))*
- **Measured:** PC-025 is 57 ft shallower, but its 1997-1998 readings rose steadily by 80 ft after a first reading flagged R, so its 1997-1998 average is not a stable baseline. *(chart 4: [placitas_remeasured](analysis.md#4-placitas_remeasured))*
- **Hypothesis:** The Sandia-site recovery after 2007 matches the timing of the San Juan-Chama Drinking Water Project (2008), after which the Albuquerque water utility pumped less groundwater; USGS mapped 30-40 ft rises across the Albuquerque area by 2016 (Ritchie et al. 2019, SIM 3435). These data alone can't show the cause. *(chart 2: [groundwater_hydrographs](analysis.md#2-groundwater_hydrographs))*
- **Insufficient data:** None of these wells are near Cuba (65-95 km away), so they say nothing direct about Cuba's aquifer. *(chart 2: [groundwater_hydrographs](analysis.md#2-groundwater_hydrographs))*
- **Insufficient data:** 5 wells, mostly with a single recent reading, can't establish an area-wide trend. *(chart 4: [placitas_remeasured](analysis.md#4-placitas_remeasured))*

## Wells and aquifer units

Research question 2.

- **Measured:** Median depth to water by record type: NMBGMR wells 53 ft (n=72); OSE aquifer tests 165 ft (n=103); OSE well logs 240 ft (n=5). *(chart 5: [well_depth_vs_water](analysis.md#5-well_depth_vs_water))*
- **Measured:** Spearman ρ between well depth and depth to water: NMBGMR wells 0.64; OSE aquifer tests 0.63 (all records pooled: 0.73, inflated because the record types differ in depth). Record types with fewer than 10 wells aren't tested. *(chart 5: [well_depth_vs_water](analysis.md#5-well_depth_vs_water))*
- **Measured:** Median water column above the well bottom: 142 ft. 2 wells had water above land surface when tested (flowing artesian; plotted above 0). *(chart 5: [well_depth_vs_water](analysis.md#5-well_depth_vs_water))*
- **Measured:** Median depth to water by area (areas with ≥5 wells): Cochiti-Peña Blanca 22 ft; Cuba area (≤25 km) 104 ft; Placitas 116 ft; Elsewhere in county 180 ft; Jemez Springs-San Ysidro 212 ft; Bernalillo-Rio Rancho 375 ft. *(chart 6: [depth_by_area](analysis.md#6-depth_by_area))*
- **Measured:** Cuba area: 10 wells with a recorded level, 10-509 ft to water, all recorded 1957-2018. *(chart 6: [depth_by_area](analysis.md#6-depth_by_area))*
- **Measured:** Median of all 108 tested wells with a value: 136 ft²/day (middle half 27.5-988; 22 wells have no recorded formation). *(chart 7: [formation_properties](analysis.md#7-formation_properties))*
- **Measured:** Among formations with ≥3 tested wells, the highest median is Alluvium and surface deposits (2,760 ft²/day) and the lowest is Point Lookout Sandstone (6.2 ft²/day). *(chart 7: [formation_properties](analysis.md#7-formation_properties))*
- **Measured:** Ojo Alamo: median of 4 wells 94.2 ft²/day, inside the middle half of all tested wells (27.5-988); with 4 wells, too few to say it differs. *(chart 7: [formation_properties](analysis.md#7-formation_properties))*
- **Insufficient data:** Only the aquifer tests record the formation; the NMBGMR and well-log files don't, so this chart can't say which aquifer each well uses. *(chart 5: [well_depth_vs_water](analysis.md#5-well_depth_vs_water))*
- **Insufficient data:** Areas mix record types and decades; differences may reflect different aquifers, land elevations, and dates, not just place. *(chart 6: [depth_by_area](analysis.md#6-depth_by_area))*
- **Insufficient data:** Most formations have fewer than 10 tested wells, many tested in the 1970s; a single new test can move a median a lot. *(chart 7: [formation_properties](analysis.md#7-formation_properties))*

## Cuba case study

Research questions 3 and 4.

- **Measured:** 9 of the tested wells within 25 km had a one-time depth to water recorded during their test (1957-1978), e.g. 18 ft at 0.7 km in 1957. Two of the well names may be the same well (same location and depth). *(chart 8: [cuba_area_map](analysis.md#8-cuba_area_map))*
- **Measured:** Transmissivity was recorded at 11 of the 15 tested wells within 25 km: from 57 ft²/day (20.3W.8.424, 19 km) to 5,508 ft²/day (Prod Well No 1, 12 km); the 4 Ojo Alamo wells with a value measured 57-164 ft²/day. One-time tests, 1957-1979. *(chart 8: [cuba_area_map](analysis.md#8-cuba_area_map))*
- **Measured:** The nearest well with repeated water-level measurements is 38 km away (WL-0062, 2 readings in 2017). *(chart 8: [cuba_area_map](analysis.md#8-cuba_area_map))*
- **Measured:** Nearest repeated water-level record: WL-0062 (NMBGMR well measurements), 38 km, 2 readings in 2017; nearest USGS monitoring well: 65 km. *(chart 9: [cuba_nearest_records](analysis.md#9-cuba_nearest_records))*
- **Measured:** Nearest aquifer test: 0.7 km (1957), a one-time record. *(chart 9: [cuba_nearest_records](analysis.md#9-cuba_nearest_records))*
- **Measured:** On the USGS map, Cuba sits at the southeastern end of the Ojo Alamo outcrop band, where the top of the sandstone is shallow; it deepens northward along the basin's eastern edge, past the 1,000-ft and 3,000-ft lines (read from the published map). *(chart 10: [ojo_alamo_depth_map](analysis.md#10-ojo_alamo_depth_map))*
- **Measured:** Ojo Alamo depth to water: 18-24 ft at the well(s) within 5 km of Cuba, and 10-604 ft at wells 19-45 km away. *(chart 11: [ojo_alamo_vs_san_jose](analysis.md#11-ojo_alamo_vs_san_jose))*
- **Measured:** San Jose: one test at one well (BIA-(RF)-033-2(10) Smelser Well, 9 km from Cuba, 1977): 51 ft to water, 206 ft deep, 100 ft²/day. That is close to the one published Cuba Mesa Member value near Lindrith (101 ft²/day at well SJ-2259, estimated from specific capacity) and inside the San Jose range from Stone et al. (1983), 43-118 ft²/day. *(chart 11: [ojo_alamo_vs_san_jose](analysis.md#11-ojo_alamo_vs_san_jose))*
- **Measured:** 6 of 10 visits (2019-2026) found no measurable flow; flowing visits measured 6.89-20.4 ft³/s, all in Apr or May. *(chart 12: [rio_puerco_visits](analysis.md#12-rio_puerco_visits))*
- **Hypothesis:** Because the Ojo Alamo is shallow at Cuba, shallow wells there can reach it, as the 148-ft Cuba school well did in 1957; whether Cuba's municipal wells use it today isn't established. *(chart 10: [ojo_alamo_depth_map](analysis.md#10-ojo_alamo_depth_map))*
- **Hypothesis:** Flow at Cuba may depend mostly on spring snowmelt from the mountains upstream; ten visits are consistent with that but can't prove it. *(chart 12: [rio_puerco_visits](analysis.md#12-rio_puerco_visits))*
- **Insufficient data:** Without repeated water levels near Cuba, the data can't confirm or rule out severe decline in Cuba's aquifer (research question 3). *(chart 8: [cuba_area_map](analysis.md#8-cuba_area_map))*
- **Insufficient data:** Answering research question 3 needs Cuba's municipal well records: well IDs, formation, pumping, and water-level history. *(chart 9: [cuba_nearest_records](analysis.md#9-cuba_nearest_records))*
- **Insufficient data:** This is a 1990 regional interpretation at 1:1,000,000 scale, read by eye; it doesn't show current water levels, how much water the formation holds, or which formation Cuba's wells use. *(chart 10: [ojo_alamo_depth_map](analysis.md#10-ojo_alamo_depth_map))*
- **Insufficient data:** Comparing the formations needs more (and recent) tests, plus the Ojo Alamo thickness and extent maps in USGS HA-720-B (dataset 5), which is a scanned map plate not yet digitized. *(chart 11: [ojo_alamo_vs_san_jose](analysis.md#11-ojo_alamo_vs_san_jose))*
- **Insufficient data:** Spot visits can't show how many days a year the river has no flow, or any long-term trend. *(chart 12: [rio_puerco_visits](analysis.md#12-rio_puerco_visits))*

## Data gaps and monitoring coverage

Research questions 5 and 6.

- **Measured:** 271 mapped sites: 96 water-level records, 153 well construction and aquifer tests, 22 surface-water stations. *(chart 1: [county_coverage_map](analysis.md#1-county_coverage_map))*
- **Measured:** Within 25 km of Cuba: 17 sites, none of them water-level monitoring sites; they are one-time aquifer tests or well logs and the Rio Puerco stream gage. *(chart 1: [county_coverage_map](analysis.md#1-county_coverage_map))*
- **Measured:** USGS monitoring sites cover 1998-2026 (all 4 from 1999); NMBGMR wells were measured in 1997-1999 and 2016-2019, with nothing in between. *(chart 13: [coverage_timeline](analysis.md#13-coverage_timeline))*
- **Measured:** Cuba-area well records come from 9 separate years (1957-2018); the only recent Cuba-area data are Rio Puerco visits (2019-2026). *(chart 13: [coverage_timeline](analysis.md#13-coverage_timeline))*
- **Measured:** 613 polygons: High 152, Moderate 339, Less 122; share of listed area: High 48%, Moderate 36%, Less 16%. *(chart 15: [aquifer_sensitivity_classes](analysis.md#15-aquifer_sensitivity_classes))*
- **Insufficient data:** The northwest of the county, around Cuba, has no repeated groundwater-level record in the collected data. *(chart 1: [county_coverage_map](analysis.md#1-county_coverage_map))*
- **Insufficient data:** No repeated groundwater-level records exist for the Cuba area in the collected data. *(chart 13: [coverage_timeline](analysis.md#13-coverage_timeline))*
- **Insufficient data:** No dataset is rated moderate or strong for question 3 (Groundwater near Cuba). *(chart 14: [evidence_matrix](analysis.md#14-evidence_matrix))*
- **Insufficient data:** Question 3 needs Cuba's municipal well records, which weren't collected. *(chart 14: [evidence_matrix](analysis.md#14-evidence_matrix))*
- **Insufficient data:** The CSV has no coordinates, and what 'sensitivity' measures isn't documented in it; the map layer and its metadata weren't collected (a coverage gap, research question 5). *(chart 15: [aquifer_sensitivity_classes](analysis.md#15-aquifer_sensitivity_classes))*

<!-- END GENERATED: findings by topic -->
