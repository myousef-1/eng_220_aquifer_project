# Round 4 review: visualization suite

Independent grade against [`RUBRIC.md`](RUBRIC.md). Materials reviewed: all 18 light static renders
(viewed at true size), 7 dark renders, all 7 app-page screenshots, `figure_text.json`, every module in
`analysis/`, all app pages, the docs pages, and `report/report.tex`. I also exported the staged tree with
`git checkout-index` into a scratch folder and built every chart there, light and dark, plus the 5
formation-metric variants, with `FutureWarning` treated as an error. I compiled the report from that copy:
6 pages, one harmless caption-package warning. I re-rendered all 18 static figures and compared them pixel
by pixel with `docs/figures/`. 16 are identical. The 2 maps differ only by antialiasing. `test_stats`
passes. Numbers were recomputed with my own code from the CSVs (pyproj for UTM, scipy for Spearman,
Kendall and permutation tests); see the last section.

## Scores at a glance

| | Score |
|---|---|
| Average chart score (18 charts) | **86.1** |
| Suite score (G 27 + H 16 + I 26 + J 17) | **86** |
| **Overall = 0.7 × 86.06 + 0.3 × 86** | **86.0** |

## Per-chart scores

| Chart key | A (15) | B (25) | C (15) | D (20) | E (10) | F (10) | Total |
|---|---|---|---|---|---|---|---|
| county_coverage_map | 13 | 23 | 13 | 15 | 9 | 9 | **82** |
| groundwater_hydrographs | 14 | 23 | 15 | 18 | 9 | 10 | **89** |
| groundwater_trends | 14 | 24 | 15 | 18 | 9 | 10 | **90** |
| placitas_remeasured | 12 | 22 | 14 | 17 | 9 | 9 | **83** |
| well_depth_vs_water | 12 | 22 | 14 | 16 | 9 | 10 | **83** |
| depth_by_area | 13 | 23 | 14 | 18 | 9 | 10 | **87** |
| formation_properties__transmissivity_drawdown_ft2_per_day | 11 | 20 | 14 | 18 | 9 | 9 | **81** |
| cuba_area_map | 13 | 24 | 13 | 16 | 9 | 9 | **84** |
| cuba_nearest_records | 14 | 24 | 14 | 19 | 9 | 10 | **90** |
| ojo_alamo_depth_map | 14 | 23 | 14 | 17 | 10 | 8 | **86** |
| ojo_alamo_vs_san_jose | 13 | 23 | 15 | 16 | 9 | 10 | **86** |
| rio_puerco_visits | 15 | 23 | 15 | 17 | 10 | 10 | **90** |
| rio_grande_quality | 14 | 23 | 15 | 18 | 9 | 10 | **89** |
| canal_seasonal | 13 | 24 | 15 | 18 | 10 | 10 | **90** |
| bernalillo_river_vs_well | 14 | 22 | 13 | 16 | 9 | 10 | **84** |
| coverage_timeline | 14 | 24 | 14 | 18 | 10 | 10 | **90** |
| evidence_matrix | 12 | 19 | 12 | 18 | 9 | 10 | **80** |
| aquifer_sensitivity_classes | 12 | 22 | 12 | 19 | 10 | 10 | **85** |
| **Average** | | | | | | | **86.1** |

## Per-chart findings

### county_coverage_map (82)
- **D, labels hidden by data.** "Bernalillo", "Rio Rancho", and "Placitas" are partly covered by blue and orange
  dots, and "Rio Rancho" and "Placitas" render faint. The county outline runs through the "b" of "Cuba".
  *Fix:* draw `_town_traces` after the data traces, give the labels a white halo (or offset them east of the
  cluster with leader lines), and move the Cuba label to `top left`.
- **D, overplotting.** The Placitas/Bernalillo and Cochiti clusters are solid blobs (opacity 0.8, no outline), so
  the 96/153 split there can't be seen. *Fix:* add a 1 px white marker outline or drop to size 6 in the static
  export. Optionally add an inset of the Rio Grande corridor.
- **D, dead space.** There is about 100 px of white between the legend and the map in the static export.
  *Fix:* reduce `margin.t` / legend `y` for the map exports.
- **C, absence stated as fact.** "...and none of those is a monitoring well" omits "in the collected data".
  Brief 1 says the gap is "a gap in this extract, not proof that Cuba has no monitoring". *Fix:* end the title
  with "...and none of those has repeated water-level records in the collected data".
- **A, title is long.** It runs 2.5 lines with two claims. *Fix:* "Most mapped sites (86% of 271) sit on the Rio
  Grande side; the 17 within 25 km of Cuba include no repeated water-level record".
- *What works:* every number checks out (271; 96/153/22; 85.6% east; 17 within 25 km). The split line is
  labeled, and off-county and unmapped sites are disclosed.

### groundwater_hydrographs (89)
- **A/B, the title's count can't be checked from the visual.** The 5 fell / 3 rose / 1 no trend classification
  (Mann-Kendall on annual means) isn't marked on the panels. Well and Well A also overlap at two sites.
  *Fix:* add a small end-of-line tag per well ("−0.36 ft/yr ↓", "no clear trend") in the trend colors.
- **B/E, method missing from the caption.** The caption never says how "fell/rose" was decided, and it lacks
  the autocorrelation caveat that applies to the title's count. *Fix:* add "Fell/rose = Mann-Kendall p < 0.05 on
  annual means (≥9 months); p-values are optimistic because years are correlated; see the trend chart."
- **D, coinciding lines.** Where Well and Well A coincide (Lincoln, Sandia), the dashed line over the solid one
  reads as a single ragged line. *Fix:* offset Well A by a thin white casing, or show Well A only in hover with
  a note.
- *What works:* the flipped axis is stated in the subtitle, every panel spans the same 37 ft, lines break at
  gaps, and the hypothesis is properly cited and labeled.

### groundwater_trends (90)
- **A, title names sites, not wells.** "4 of 7 wells were still falling (Lincoln Middle School and Dome Road
  well)" names 2 sites, so a reader counts 2. *Fix:* "(all 3 Lincoln Middle School wells and the Dome Road
  well)".
- **E, unclear caption phrase.** "Intervals narrower than the marker: Dome Road well · Well (full record)" is
  hard to parse. *Fix:* "The Dome Road well's full-record interval is narrower than its marker."
- **H/D, blue has two meanings.** Blue means "rising" here but "water-level records" everywhere else. *Fix:*
  acceptable, but note it in the legend title ("Trend color:"), or use a teal for rising.
- *What works:* the method, intervals, the window's n of years, the explanation for missing recent markers,
  and the honest autocorrelation caveat. All slopes verified.

### placitas_remeasured (83)
- **A, title too long.** It runs 3 lines (about 190 characters) with 4 numbers and 2 well IDs, so it isn't a
  repeatable sentence. *Fix:* "Of 5 Placitas wells re-measured after 20 years, 3 changed ≤5 ft; one is 51 ft
  deeper and one 57 ft shallower". Move the flagged-baseline detail to the caption.
- **B/C, single-reading change stated as fact.** PC-014's "51 ft deeper" rests on one 2019 reading with no
  status code. *Fix:* "one 2019 reading was 51 ft deeper than the 1997-98 average", and add that a single
  reading can't rule out recent pumping.
- **B, ambiguous wording.** "its 1997-1998 readings rose steadily by 80 ft": the depth readings fell (139 to
  59 ft); the water level rose. *Fix:* "its water level rose 80 ft during 1997-98 (depth 139 to 59 ft)".
- **D, crowded footnote.** The "†" footnote is set in 11.5 px at the top-right corner, touching the legend row.
  *Fix:* move it below the x-axis title, or into the caption only.
- **F, readings not downloadable.** The table holds per-well aggregates only, so the 46 individual readings
  (dates, status flags, methods) can't be downloaded. *Fix:* append the raw readings, or add a second table.
- *What works:* a proper before/after dumbbell. The 1997-98 range bars, n per period, R flags, and the
  method change are all disclosed, and every value matches the raw file.

### well_depth_vs_water (83)
- **A/B, title pools what the caption says can't be pooled.** "...but half of 180 wells have water 41-241 ft
  down" is an IQR across three record types that "measure water differently", and the "but" doesn't contrast
  with the first clause. *Fix:* "Wells reaching deeper water are drilled deeper (Spearman ρ ≈ 0.63 within each
  of the 2 larger record types); most wells keep 50-250 ft of water above the bottom". Or give the IQR per type.
- **D, label covered by data.** "water level at the bottom of the well" is overlapped by a blue dot at its
  first letter and an orange diamond on "well", and its leader line crosses points. *Fix:* anchor it in the
  empty lower-right triangle (about x = 900, y = 560), with `bgcolor` set to the surface color.
- **C, Cuba wells not marked.** The 7 wells within 25 km of Cuba aren't distinguished, so the chart can't feed
  the Cuba case study. *Fix:* ring them (black outline) and add "ringed = within 25 km of Cuba" to the legend.
- **C, causal wording.** "Where water is deeper, wells are drilled deeper" reads as a causal rule. The finding
  is an association. *Fix:* "...tend to be drilled deeper".
- *What works:* one point per well, off-chart and excluded records disclosed, flowing wells explained, and
  per-type correlations to avoid pooling inflation. ρ values verified with scipy.

### depth_by_area (87)
- **A, unclear referent.** "(375 ft; 9 of 11 are 1987-2007 aquifer tests)": 9 of 11 what? *Fix:* "(375 ft;
  9 of its 11 wells are 1987-2007 aquifer tests)".
- **D, points hidden.** The 26 px black median ticks hide the points sitting on the median (for example
  Bernalillo-Rio Rancho near 375). *Fix:* draw the ticks thinner (1.5 px) with a white casing, or put them
  behind the points with `opacity 0.7`.
- **C/B, date mixing not visible.** Areas mix decades (the Cuba area is 1957-1978 tests; Cochiti is 1997-2019
  NMBGMR readings), and the caveat lives only in a finding. *Fix:* add one caption sentence giving each area's
  record years, or encode the decade by marker fill.
- *What works:* n per area, medians only where n ≥ 5, Cuba included with the same 25 km rule, and flowing
  wells and the unmapped well disclosed. All medians verified.

### formation_properties__transmissivity_drawdown_ft2_per_day (81)
- **A, title is jargon.** "values span more than the 2.6-order spread between formation medians (up to 4.8
  orders, Madera Limestone)" is jargon that no reader can repeat. The "9 formations" also don't match the 11
  rows drawn. *Fix:* "Transmissivity varies more within some formations than between them: Madera Limestone
  tests range from 0.2 to 12,000 ft²/day".
- **B, uncaught duplicates.** The Madera row contains two cross-name duplicate tests that the same-name
  de-duplication misses. "Rock Springs Well" and "San Pedro Creek Estates, Rock Springs Well" (1994-04-14,
  0.23 km apart, 500 ft deep, both 0.2 ft²/day). "Campbell Ranch Well 4" and "San Pedro Creek Estates, Well 4"
  (1994-01-28, both 221 ft deep, same recovery T of 1,765 and specific capacity 0.6), but drawdown T is 221 vs
  22: likely a 10× entry error. So "13 values · 12 wells" is probably 11 values and 10 wells, and the
  headline low end is one test, not two. *Fix:* extend `well_key` merging to the same date, within 0.5 km,
  and the same well depth. Flag the 22/221 pair in the caption and in James's open issues.
- **B, method bias.** The full range grows with sample size (Madera has 13 values; most rows have 3-4), so the
  within/between comparison favors big groups and hinges on single extreme tests. *Fix:* compare IQRs (or the
  5th-95th percentile) for rows with ≥5 wells, or state the caveat in the caption.
- **C, hierarchy.** "Abiquiu Tuff (Santa Fe Group)" and "Santa Fe Group" appear as separate peers. *Fix:*
  note in the caption that the Abiquiu Tuff is part of the Santa Fe Group and is kept separate because OSE
  records it separately.
- **D/F, small issues.** The dotted-line label "median of all 108 tested wells: 136" has no unit (add
  "ft²/day"). The selector variants produce titles like "within 2 of 2 formations ... 0.7-order spread": use the
  plain-language template for every metric.
- *What works:* per-well medians, gray context with focus colors for the two Cuba-area formations, value and
  well counts per row, and an honest "too few to say it differs" for the Ojo Alamo. Numbers verified.

### cuba_area_map (84)
- **A/G, formations not shown.** The proposal's Cuba-area view should "highlight the Ojo Alamo Sandstone, San
  Jose Formation, nearby wells", but tested wells aren't distinguished by formation, even though the data
  name them (Ojo Alamo at 0.7 and about 20 km, San Jose at 9 km). *Fix:* outline or recolor the aquifer-test
  dots by recorded formation, using the project's ochre and violet with the gray context, and add them to the
  legend.
- **C, absence stated as fact.** "no well there is measured repeatedly" again omits "in the collected data".
  *Fix:* "...; the collected data hold no repeated water-level record there".
- **D, layout.** There is about 120 px of dead space between the legend and the map. "Jemez Springs" is struck
  through by the 50 km ring, "San Ysidro" touches a dot and the ring, and the county outline is cut off at
  the bottom. *Fix:* tighten the top margin, set town `textposition` away from the rings, and raise the map
  center slightly or reduce zoom so the outline closes.
- *What works:* the rings at 10/25/50 km make the 25 km definition concrete, and the legend counts match
  (1/44/10 within 60 km). Same-location pairs are disclosed.

### cuba_nearest_records (90)
- **C, absence claim.** "within 25 km there are only one-time tests...": add "in the collected data" for the
  same reason as the maps.
- **H, rounding mismatch.** The Rio Puerco gage is "2.3 km" here but "2 km from the village center" in the
  rio_puerco_visits scope. *Fix:* use one rounding rule (1 decimal under 5 km) everywhere.
- **A, long title.** It runs to 2 lines. *Fix:* "The nearest repeated water-level record is 38 km from Cuba;
  everything within 25 km is a one-time test, one well log, or the river gage".
- *What works:* the clearest single picture of the Cuba data gap. The shaded Cuba band, data-type colors,
  end labels with record years, and the caption warning that a short bar doesn't answer the question are
  all good.

### ojo_alamo_depth_map (86)
- **C, label choice.** The first finding labels a 1990 published interpretation "read by eye" as
  **Measured**. The team didn't measure it. *Fix:* keep "Measured" only if the proposal's definition allows
  published values; otherwise phrase it "Measured (published map)" consistently with the San Jose values, or
  add a note in the findings legend that published maps count as measured context.
- **D, crop artifacts.** Fragments "ownpoint" and "CO" sit at the left edge, and a stray frame line runs at
  x ≈ 1200. *Fix:* crop 15 px tighter on the left and right, or mask the edges with a thin white border.
- **F, little interactivity.** There is no hover (the figure is an image), and the "data" table is
  publication metadata, which is acceptable. The bright plate sits in the dark theme without a frame.
  *Fix:* add a 1 px neutral border so the image edge is visible on dark backgrounds.
- *What works:* attribution, an unchanged plate, the map's own Cuba label, and a scale bar I checked against
  the graticule (25 km ≈ 161 px vs 163 px from 30′ latitude = 55.5 km). Brief 5's "historical regional
  interpretation" caveat is carried.

### ojo_alamo_vs_san_jose (86)
- **A, awkward count.** "8 test events at 7-8 wells" is clumsy. *Fix:* "8 tests at 7 wells (8 well names)".
- **D, log scales not marked.** Three panels are log scale and one is linear, but only the caption says so.
  *Fix:* add "(log)" to the three panel titles.
- **D, unlabeled row.** The published San Jose diamonds sit in an unlabeled third row below "San Jose
  Formation". There is also large blank space above the panels (legend at y = 1.3). *Fix:* add a y tick
  "Published San Jose (dataset 6)" for that row and tighten the legend.
- *What works:* the honest headline (too few to compare), n per panel, duplicates drawn once, a correct
  m²/day to ft²/day conversion (9.4 × 10.7639 = 101), and the possible same-well pair disclosed.

### rio_puerco_visits (90)
- **D, month panel ticks.** The month-of-year panel labels only odd months, so the three October visits look
  like September and the December visit sits past the last tick. *Fix:* tick every month with single
  letters, as canal_seasonal does.
- **B, undisclosed spread.** Visits in the same month are spread ±0.28 month sideways, which reads like day of
  month. The caption doesn't say so. *Fix:* add "visits in the same month are spread sideways for
  visibility".
- *What works:* no lines between spot visits, open vs filled markers, month labels on each dot, the brief 4
  caveats ("not dry all season", "river, not groundwater"), and a sensible hypothesis label. All 10 visits
  verified.

### rio_grande_quality (89)
- **E/B, statistic not named for conductance.** The pH panel says "monthly median" but the specific
  conductance panel doesn't say "monthly mean". *Fix:* panel title "Specific conductance, monthly mean
  (µS/cm)".
- **B, uneven months.** Monthly values include partial months with few samples (for example the first month
  starts 2003-09-30). *Fix:* drop months with fewer than about 10 daily values, or disclose
  `sample_count` in hover and the caption.
- **D, low dip unremarked.** The 2023 pH dip to 7.1 goes unremarked, and readers will ask. *Fix:* one
  sentence in the caption, or an annotation.
- *What works:* separate panels for separate units, a well-sourced scale reference, and a clear river-not-
  groundwater scope with an Insufficient-data finding for RQ5. Percentiles and the trend test verified.

### canal_seasonal (90)
- **A, unclear canal.** "median flow peaks near 86 ft³/s" doesn't say which canal (Sile peaks near 58).
  *Fix:* "...; the East Side canal peaks near 86 ft³/s in June".
- **D, small counts.** The years-with-data counts under each month are set at 10.5 px and become about 7 px
  at report width. *Fix:* use 12 px.
- *What works:* the IQR band, n of years per month, an honest note that the winter zeros rest on fewer years,
  and clear "context, not acequia records" scoping.

### bernalillo_river_vs_well (84)
- **C/B, title states a suggestive result as firm.** The title gives "Well A's water level tended to rise
  in years when river flow increased" as a finding, but the Bonferroni-adjusted p is 0.053. *Fix:* append
  "(suggestive: p = 0.03, 0.05 after correcting for two wells)".
- **B, regulated gage.** The flow gage is Rio Grande below Cochiti Dam, a regulated dam release 41 km
  upstream. The distance is disclosed, but the regulation isn't. *Fix:* add "flow is regulated by Cochiti
  Dam" to the caption.
- **D, text touches a point.** The annotation "ρ = +0.12, n = 22, p = 0.572" touches a data point (the dot at
  about +150 ft³/s, +2.5 ft). *Fix:* move the stats box to the bottom-right corner, or give it a surface-color
  `bgcolor`.
- **H/D, style mismatch.** Well A is a solid line here but dashed in the hydrographs. The caption also says
  "different vertical scales" twice. *Fix:* use the same dash, and delete the second sentence.
- *What works:* a change-vs-change design that avoids spurious drift correlation, a permutation test with
  correct n, and a reading guide for the scatter. Numbers verified with scipy.

### coverage_timeline (90)
- **C, absence claim.** "the Cuba area has no water-level monitoring or water-quality records": add "in the
  collected data" in the title. The caption already says other agencies may have data.
- **B/H, year range.** The subtitle says "(1925-2026)", which is the axis range. The data start in 1926, and
  other charts say 1926-2026. *Fix:* take `start` from the data's first year, or say "axis 1925-2026".
- *What works:* the clear two-block design (county vs Cuba area), an explicit "no records" row for
  acequias, a gray ramp that keeps blue for water level, and accurate counting rules in the caption.

### evidence_matrix (80)
- **C/H, contradicts the Q4 result.** Q4 (Ojo Alamo vs San Jose) shows two **Strong** cells (datasets 5 and 6),
  while ojo_alamo_vs_san_jose and the findings table say Q4 is *Insufficient data*. The title's "coverage and
  well questions are the best supported" also ignores Q4's two Strong ratings. A reader will trip on this.
  *Fix:* mark those cells "Strong‡ (maps, not digitized)" or add a right-hand column "With data in hand",
  showing Q4 = Insufficient. Reword the title: "Per the briefs, RQ3, 5, 6 and 7 have at best limited support;
  RQ4's strong ratings depend on maps not yet digitized".
- **B, words are paraphrased.** The caption says "each cell shows the brief's own word", but several are
  paraphrases. "Best fit" stands for brief 2's "Strongest fit (partial)" and brief 7's "Strongest (partial)".
  "Context" stands for "CONTEXTUAL" / "Supporting context". "None" stands for "Not supported" / "NOT DIRECTLY
  ESTABLISHED". Brief 5's "Strong" is qualified "for the Ojo Alamo side". *Fix:* say "short form of the brief's
  rating", and put the brief's exact phrase in the hover.
- **B, cell symbol.** "Partial†" on the USGS wells × Q7 cell uses † (a column-level "no brief" marker) on a
  single cell. *Fix:* use a distinct symbol (*) defined as "rated by the analysis; the brief doesn't rate
  this question".
- *What works:* a compact, readable summary that makes the gaps obvious. The gray ramp has in-cell text
  (colorblind-safe), and it is honestly labeled a judgment summary.

### aquifer_sensitivity_classes (85)
- **C/B, scope can be narrowed.** The scope says "Unknown extent", but the listed `Shape__Area` sums to 30.9
  units. In square degrees that is about New Mexico's area (≈30.8 sq. degrees at 34.4° N); Sandoval County is
  only about 0.9. So the layer is almost certainly statewide, and "48% of listed area" is a statewide share.
  *Fix:* say "likely statewide (total listed area ≈ New Mexico's area); Sandoval would be about 3% of it", and
  keep "not Cuba".
- **A, weak research link.** The chart mostly documents a gap and answers little. *Fix:* acceptable; consider
  folding it into the coverage section as a small table so it doesn't read as a result.
- *What works:* it follows brief 3 exactly (polygon counts are not land shares, units are unstated, it
  describes the inventory and not Cuba) and is clean and readable.

## Suite scores

### G. Coverage of questions and planned outputs: 27 / 30
Every planned output that the data allow exists. There is a county map, a Cuba-area view (map, nearest
records, Ojo Alamo plate, formation comparison, Rio Puerco), time series for repeated measurements
(hydrographs, trends, Placitas re-measures), comparisons by area and by aquifer unit, and three coverage
views (map, timeline, evidence matrix). RQs without data are shown as gaps, not skipped: page warnings, an
"Acequias: no records" row, and Insufficient-data findings for RQ3, 5 and 6. RQ9 gets an indicator table.
Deductions:
- The Cuba-area map doesn't highlight the Ojo Alamo or San Jose wells, as the proposal asks.
  *Fix:* color tested wells by formation.
- The county map shows no aquifer or geologic regions or acequias, and the figure itself doesn't say so (only
  the page caption does). *Fix:* add one caption sentence or an in-map note: "Geologic regions and acequias:
  not yet collected".
- The proposal asks to group comparisons "by region or aquifer system". The town-based areas are a disclosed
  substitute.

### H. Consistency across charts: 16 / 20
Colors, scope phrases, the 25 km "Cuba area", the caption structure (Chart object) and finding labels are
consistent across the app, docs, and report. Inconsistencies a reader would notice:
1. **The report contradicts the charts.** `report.tex` §5.3 says "Ten of the tested wells recorded a depth to
   water on test day". The charts and data say **9** tested wells (the 10th Cuba-area level is the 2018 well
   log).
2. evidence_matrix rates Q4 strongly supported, while ojo_alamo_vs_san_jose and `findings.md` mark Q4
   *Insufficient data*.
3. The indicator table gives the 2016-2025 trend "Confidence: High at these wells", while the trends caption
   says the window has 9-10 years and the p-values are optimistic.
4. Absence claims are qualified ("in the collected data") in some titles and findings but not others
   (county map, Cuba-area map, coverage timeline).
5. Small items: 1925 vs 1926; 2 km vs 2.3 km; Well A dashed vs solid; blue means both "water-level records"
   and "rising".

*Fix:* correct the report sentence; reconcile Q4; change the indicator confidence to "Moderate (9-10 years;
p-values optimistic)"; apply one qualifier rule to absence claims; tidy the small items.

### I. Reproducibility and code quality: 26 / 30
Strong points:
- A fresh export of the staged tree builds all 18 charts (light and dark) and all metric variants with no
  warnings.
- Paths come from `__file__`; numbers in titles and captions are computed; raw data are never edited; prep is
  documented in `docs/analysis.md` and the loader docstrings.
- Statistics carry unit tests that pass; the README explains teammate tasks.

Deductions:
- `charts.py` is a single 2,100-line module with several 100+ line functions and dense inline conditionals
  (for example the nested f-string on line 461), which is hard for a teammate to change safely. *Fix:* split
  it into `charts/levels.py`, `wells.py`, `cuba.py`, `surface.py`, and `coverage.py`, and factor the repeated
  "absence title" and "years" phrasing into helpers.
- Duplicate detection in `data._aquifer_tests` only merges same-name rows, so the cross-name Madera duplicates
  (and a likely 22/221 typo) pass through. *Fix:* also merge rows with the same date, within 0.5 km, and the
  same well depth, and log them.
- `ojo_alamo_vs_san_jose` builds its caption from `date.today()`, so the text ("49-73 years old") changes
  with the run date and the exports drift from the app. *Fix:* use the data's years ("tests from
  1953-1977").
- `Chart.static()` renders each figure an extra time to SVG (`_plot_left_px`) inside a bare `except`, which
  slows exports and hides errors. *Fix:* catch the specific kaleido error, or cache the measurement.
- A few hand-typed counts remain outside the chart code: the `data_sources.py` page says "30 monitoring sites
  ... from 1926 to 2026". *Fix:* compute them from `load_usgs_sites()`.

### J. Integration: 17 / 20
Every chart is on its matching page with title, subtitle, scope, caption, labeled findings, and a data table
with CSV download (confirmed in all 7 screenshots). Static exports are current: my re-render matches
`docs/figures/` pixel for pixel except map antialiasing. `analysis_figures.tex` and `figure_index.csv` match
`figure_text.json`. The report compiles, with figures 1-3 placed and referenced. The docs chart sections are
generated. Deductions:
- The report's Results text has the "Ten of the tested wells" error and isn't generated from the charts.
  *Fix:* emit a `report/analysis_numbers.tex` of `\newcommand`s from `export_figures`, and use them in
  Results.
- The report still lists "County boundary" under "Datasets to Be Collected" although one is now used.
- The County map page caption says "Research questions 1 and 8", while the chart lists 8, 1, 3.
- The report PDFs embed Type 3 fonts from kaleido, which is fine for the course but can be rejected by some
  print workflows.

## Overall

- Average chart score: **86.1** (1,549 / 18)
- Suite score: **86** (27 + 16 + 26 + 17)
- **Overall = 0.7 × 86.06 + 0.3 × 86 = 86.0**

## Top 10 fixes (ordered by expected overall gain)

1. **Reconcile the evidence matrix with the Q4 result (about +0.5).** Mark the Q4 Strong cells as conditional
   on undigitized maps, or add a "with data in hand" column. Fix the title's "best supported" clause. Change
   "brief's own word" to "short form", with the exact brief phrase in hover.
2. **Make the report agree with the charts (about +0.45).** Change "Ten of the tested wells" to "Nine (plus
   one 2018 well log)". Generate the Results numbers as LaTeX macros from the Chart objects so they can't
   drift.
3. **Cuba-area map shows formations (about +0.4).** Color the aquifer-test wells by recorded formation (ochre
   Ojo Alamo, violet San Jose, gray other or unrecorded). Remove the dead band under the legend and move the
   town labels off the rings.
4. **Clear every text/mark collision (about +0.4).** Bernalillo stats box (bottom-right or with a background);
   well_depth "bottom of the well" label (empty lower-right, with a background); county map town labels (on
   top, with a halo; Cuba label off the outline); Placitas "†" footnote (below the axis).
5. **Formation chart: plain title and clean duplicates (about +0.4).** Plain-language title with the actual
   range. Merge the cross-name duplicate tests (same date, within 0.5 km, same depth) and flag the 22 vs 221
   ft²/day pair. Compare IQRs, or caveat the range comparison's dependence on n.
6. **One rule for absence claims (about +0.35).** Add "in the collected data" to the titles of
   county_coverage_map, cuba_area_map, coverage_timeline, and cuba_nearest_records.
7. **Consistency sweep (about +0.3).** Indicator-table confidence for 2016-2025 → "Moderate (9-10 years;
   p-values optimistic)". Well A dashed in the Bernalillo chart. Year spans from the data (1926). One
   rounding rule for the Rio Puerco distance. Compute the hand-typed "30 sites / 1926 to 2026" on the Data
   sources page.
8. **Hedge the Bernalillo title (about +0.2).** Append "(suggestive: p = 0.03, 0.05 after correcting for two
   wells)" and note that Cochiti Dam regulates the flow gage.
9. **Shorten and hedge the Placitas and well-depth titles (about +0.3 for both).** Placitas to 2 lines, with
   PC-014 as "one 2019 reading" and the PC-025 wording made unambiguous. In well_depth_vs_water, drop the
   pooled IQR and ring the 7 Cuba-area wells.
10. **Rescope aquifer sensitivity (about +0.15).** State that the total listed area ≈ New Mexico's area, so the
    shares are statewide (Sandoval about 3%). Also label all 12 months in the Rio Puerco month panel and
    disclose the sideways spread (about +0.1).

## Numeric spot-checks

Recomputed with my own code from the CSVs (pyproj EPSG:26913 to 4269 for UTM; scipy for Spearman, Kendall,
and permutation tests). These do not use the project's loaders.

| # | Claim (where) | Recomputed | Match |
|---|---|---|---|
| 1 | 271 mapped sites: 96 water-level, 153 tests/logs, 22 surface water (county map) | 271; 96 / 153 / 22 | yes |
| 2 | 86% of sites east of 106.75° W (county map title, report) | 85.6% | yes |
| 3 | 17 sites within 25 km of Cuba (15 tested wells, 1 log, 1 gage) | 17 (15 / 1 / 1) | yes |
| 4 | Nearest repeated water-level record WL-0062, 38 km, 2 readings in 2017 | 38.5 km, 2 readings (Sep and Dec 2017) | yes |
| 5 | Nearest USGS monitoring well 65 km; nearest aquifer test 0.7 km (1957) | 65.2 km; 0.71 km, 1957 | yes |
| 6 | 5 of 9 wells fell, 3 rose, 1 no clear trend (Mann-Kendall, annual means ≥9 months) | 5 / 3 / 1 | yes |
| 7 | Sandia site rose 13 ft since 2007 | 492.05 ft (2007) → 478.84 ft (2025) = 13.2 ft | yes |
| 8 | Lincoln −0.40 to −0.36 ft/yr; Bernalillo main −0.52; Sandia +0.57 / +0.72; 2016-2025: 4 of 7 falling, 2 rising | −0.403 to −0.360; −0.522; +0.572 / +0.722; 4 of 7, 2 | yes |
| 9 | Placitas: PC-014 +50.9 ft (n 9→1), PC-025 −57.2 ft (1997-98 range 80 ft); 3 within 5 ft, 2 of them flagged R | +50.9; −57.2 (range 80.4); 3 (PC-002, PC-019, PC-055); PC-002 and PC-055 flagged | yes |
| 10 | Spearman ρ: NMBGMR 0.64, OSE tests 0.63, pooled 0.73; medians 53 / 165 / 240 ft | 0.644 / 0.633 / 0.730; 52.8 / 164.7 / 240.0 | yes |
| 11 | Half of 180 wells have water 41-241 ft down | 181 wells and IQR 41.2-240.0 before merging the Smelser duplicate; 180 after the project's merge | yes (merge accounts for the difference) |
| 12 | Area medians: Cochiti 22, Cuba 104, Placitas 116, Elsewhere 180, Jemez-San Ysidro 212, Bernalillo-Rio Rancho 375; 9 of 11 are 1987-2007 tests | 22.5 / 104.5 / 116.3 / 179.5 / 211.5 / 374.9; 9 tests (1987-2007) + 2 NMBGMR | yes |
| 13 | Transmissivity: 108 wells, median 136 (IQR 27.5-988); Alluvium 2,760; Point Lookout 6.2; Madera span 4.8 orders; between-median spread 2.6; 3 of 9 formations | 108; 135.5 (27.5-988.5); 2,759.5; 6.2; 4.79; 2.65; 3 of 9 | yes |
| 14 | Cuba area: 15 tested wells (1957-1979), 9 with a level (1957-1978), 18 ft at 0.7 km in 1957 | 15; 9; 17.8 ft at 0.71 km | yes |
| 15 | **Report §5.3: "Ten of the tested wells recorded a depth to water on test day"** | **9 tested wells** (10 Cuba-area levels only when the 2018 well log is counted) | **no** |
| 16 | Ojo Alamo / San Jose: 8 events (7 / 1); Ojo Alamo levels 18-24 ft near Cuba and 10-604 ft at 19-45 km; SJ-2259 = 101 ft²/day; Stone range 43-118 | 8 (7 / 1); 17.8-24 and 10-604 at 19.5-44.9 km; 9.4 × 10.7639 = 101.2; 43.1-118.4 | yes |
| 17 | Rio Puerco: flow on all 4 Apr-May visits (6.89-20.4 ft³/s), none on the 6 Aug-Mar visits | 4 flowing (Apr 2019, May 2020, Apr 2021, Apr 2024), 6 zero | yes |
| 18 | Rio Grande specific conductance, 90% of months 221-342 µS/cm, median 294; pH 7.8-8.3; trend +0.2 /yr, p = 0.74 | 221.1-342.1, 293.8; 7.8-8.3; Sen +0.225, Kendall p 0.738 | yes |
| 19 | Canals: zero median Dec-Feb; East Side peaks near 86 ft³/s in June; winter 8-14 years vs up to 24 | 0 in Dec, Jan, Feb; 86.3 in June; 8-14 vs 24 | yes |
| 20 | Bernalillo: Well A ρ = +0.54, n = 17, p = 0.027; main well ρ = +0.12 (p = 0.57), n = 22 | 0.539, 17, permutation p 0.028; 0.124, 22, p 0.59 | yes |
| 21 | Aquifer sensitivity: 613 polygons (High 152, Moderate 339, Less 122); area shares 48 / 36 / 16% | 613; 152 / 339 / 122; 47.5 / 36.0 / 16.5% (total 30.9 units ≈ New Mexico's area in square degrees) | yes |
| 22 | USGS monitoring sites cover 1998-2026, all 4 from 1999 | Lincoln from June 1998; 4 sites every year from 1999 | yes |
| 23 | Indicator table: full-record change −16 to +8 ft | −16.0 (Bernalillo main) to +7.8 (Sandia) | yes |
