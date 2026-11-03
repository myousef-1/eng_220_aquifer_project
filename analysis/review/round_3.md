# Round 3 review: visualization suite

Graded against `analysis/review/RUBRIC.md` by an independent reviewer (round 3).
What was graded: `analysis/*.py` and `app_pages/*.py` as staged in the clone (charts.py last changed at 04:03), the
round-3 renders in `scratchpad/round3/` (18 static PNGs, dark PNGs, 7 fresh app screenshots, `figure_text.json`),
`docs/`, and `report/`. The text in `figure_text.json` matches what the current code produces for all 18 charts.

## Scores at a glance

| | Score |
|---|---|
| Average chart score (18 charts) | **86.1** / 100 |
| Suite score (G+H+I+J) | **87** / 100 |
| **Overall = 0.7 × 86.1 + 0.3 × 87** | **86.3** |

Round 2 scored 84.0, so this round gained 2.3 points. Under the stopping rule (gain ≥ 1, overall < 95), the loop
continues to round 4.

**Harness notes (no deduction):** the app screenshots are fresh this round; they show the current titles, such as
"5 of 9 monitored wells…" and "…1 well log, and 1 stream gage". Maps in `app/` are blank because tiles can't load in
the sandbox, and maps in `dark/` are drawn on `white-bg` with dark-theme ink. In the app itself, `st_helpers._build`
passes `carto-darkmatter` in dark mode.

**What I ran:** all 18 charts build in both themes, plus every `formation_properties` metric (6.5 s in total).
`python -m analysis.test_stats` passes. A fresh export of the staged index (`git checkout-index -a`) builds every chart
and the indicator table without errors. `report.tex` compiles cleanly in a scratch copy (6 pages, no undefined
references). Nothing is unstaged or untracked, and the only staged change under `data/` is the new GeoJSON.

## Per-chart scores

| Chart key | A (15) | B (25) | C (15) | D (20) | E (10) | F (10) | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| county_coverage_map | 14 | 24 | 14 | 15 | 9 | 9 | **85** |
| groundwater_hydrographs | 14 | 24 | 14 | 17 | 9 | 9 | **87** |
| groundwater_trends | 14 | 23 | 14 | 17 | 9 | 10 | **87** |
| placitas_remeasured | 13 | 22 | 14 | 16 | 9 | 10 | **84** |
| well_depth_vs_water | 14 | 23 | 14 | 15 | 9 | 10 | **85** |
| depth_by_area | 13 | 22 | 14 | 15 | 9 | 10 | **83** |
| formation_properties__transmissivity_drawdown_ft2_per_day | 13 | 19 | 13 | 17 | 9 | 8 | **79** |
| cuba_area_map | 14 | 23 | 14 | 16 | 9 | 10 | **86** |
| cuba_nearest_records | 14 | 23 | 15 | 17 | 9 | 10 | **88** |
| ojo_alamo_depth_map | 13 | 23 | 13 | 16 | 9 | 8 | **82** |
| ojo_alamo_vs_san_jose | 14 | 21 | 14 | 16 | 9 | 10 | **84** |
| rio_puerco_visits | 15 | 24 | 15 | 18 | 10 | 10 | **92** |
| rio_grande_quality | 14 | 24 | 15 | 17 | 9 | 10 | **89** |
| canal_seasonal | 13 | 24 | 15 | 18 | 10 | 10 | **90** |
| bernalillo_river_vs_well | 14 | 23 | 15 | 17 | 9 | 10 | **88** |
| coverage_timeline | 14 | 24 | 14 | 17 | 9 | 10 | **88** |
| evidence_matrix | 14 | 23 | 14 | 16 | 9 | 10 | **86** |
| aquifer_sensitivity_classes | 11 | 23 | 15 | 18 | 9 | 10 | **86** |
| **Average** (1,549 / 18) | | | | | | | **86.1** |

## Per-chart findings

### county_coverage_map (85)
- **Town labels are hidden by data markers (D).** `_town_traces` is added *before* `_map_points_traces`, so the dots
  are drawn over the labels: "Bernalillo" is split by orange and blue dots ("Bern…lillo"), "Placitas" sits inside the
  blue cluster, and "Rio Rancho" touches a blue dot. *Fix:* add the town traces after the data traces, and move
  Bernalillo to `"middle left"` and Placitas to `"bottom right"` with an offset point a few km outside the cluster.
- **About 35% of the frame is empty (D).** The county fills only the middle of the 1,000-px figure, with a ~90-px gap
  between the legend and the map. *Fix:* export the map at about 760 px wide, or raise the zoom to about 8.4 and set
  the legend's `y` closer to the map.
- **The legend counts include duplicate test records (B, minor).** The 154 "well construction and aquifer tests" count
  the Smelser Well twice (see cuba_area_map). *Fix:* deduplicate as described there.
- **The F score loses 1 for the dense Rio Grande cluster.** It is unreadable even in the static figure, and the
  "zoom in" note helps only in the app. *Fix:* add a small inset of the Bernalillo–Placitas cluster to the static
  export, or accept the loss.
- **Works well:** every number checks out (272; 96 / 154 / 22; 85.3% east; 18 within 25 km = 16 tests, 1 log, and the
  Rio Puerco gage). The 3 sites outside the county line are now disclosed and computed, and the scale bar, the
  meridian label, the record period in the subtitle, and the "not active monitoring" caveat are all present.

### groundwater_hydrographs (87)
- **The title breaks between number and unit (D).** "…has risen 13 / ft since 2007". *Fix:* use a non-breaking space
  in `f"{recovery:.0f} ft"` (as the Bernalillo title already does for ρ), and do the same in every title with
  "N ft".
- **There is dead space under the legend (D).** About 70 px between the legend row and the panel titles. *Fix:*
  `legend.y` ≈ 1.08 and `margin.t` ≈ 70.
- **Well B is faint in dark mode (F).** `blue_light` in dark mode is `#184f95` on `#0e1117`, which gives low contrast
  for a 2-px line (Lincoln and Sandia Well B). *Fix:* lighten the dark step to about `#4f86cc`, or use a dotted dash
  for Well B.
- **Works well:** every count is now computed (5 / 3 / 1, 9 wells, 4 sites, 37-ft span). The parenthetical that hid
  the mixed Bernalillo site is gone, the hypothesis now cites Ritchie et al. (2019), the axis is flipped and labeled,
  and the lines break at gaps.

### groundwater_trends (87)
- **The x-axis title floats onto the footer (D).** In the static export, "Water-level trend (ft per year)" sits about
  55 px below the tick labels and about 20 px above the Scope/Source footer, so it reads as part of the footer. The
  same happens in placitas, well_depth, depth_by_area, formation, and cuba_nearest. *Fix:* in `Chart.static()`, set
  `fig.update_xaxes(title_standoff=8)` and add `foot_h` to `margin.b` only after measuring with `automargin`; or put
  the footer at `yshift=-(base_b + 6)` relative to the axis title.
- **Dome Road's full-record interval is invisible (D, minor).** Its whisker (−0.12 to −0.10) is narrower than the
  marker, so readers can't tell "tiny interval" from "no interval". *Fix:* add a small end cap or a note: "interval
  narrower than the dot".
- **Recent-window intervals deserve one more caveat (B).** The 2016–2025 slopes rest on 9–10 annual means, and the
  Lincoln Well A interval is almost one-sided. The caption's serial-correlation caveat covers this in general. *Fix:*
  add "the 2016–2025 window has only 9–10 years per well" to the caption.
- **Works well:** the Sandia "fell, then rose" caveat for Sen's slope is now in the caption, every missing recent
  marker is explained, the legend separates shape (period) from color (trend), and all numbers check out (−0.40 to
  −0.36; 4 of 7; −0.52; +0.57 and +0.72).

### placitas_remeasured (84)
- **"3 changed ≤5 ft" rests mostly on flagged baselines (B).** Two of those three wells have flagged 1997–98
  baselines: PC-002 (a single reading, flagged R) and PC-055 (all 8 readings flagged R). The late period is one
  reading for 4 of the 5 wells. *Fix:* in the title, "3 changed ≤5 ft (2 with flagged baselines)", or move the count
  into the findings and lead with the method caveat.
- **The † note crowds the PC-014 row (D).** "† a 1997-1998 reading was flagged R" is anchored at paper y = 0, right
  under the "50.9 ft deeper … range 3 ft" label, and the two nearly touch. *Fix:* anchor it below the axis
  (`y=-0.18, yanchor="top"`) or at the top right above PC-025.
- **The title is ambiguous (A).** "(unstable baseline)" dangles after PC-025. *Fix:* "PC-025 is 57 ft shallower, from
  an unstable 1990s baseline".
- **Hidden early dots (D, minor).** For PC-002 (+1.0 ft) and PC-019 (−1.5 ft), the 1997–98 dot is completely covered
  by the 2018–19 dot. *Fix:* draw the early dot as a hollow ring one size larger.
- **Works well:** the † key is now on the figure, the range is printed per row, the median gap (63 days) and the
  method change (T → S/T) are computed, and every number checks out (+50.9, −57.2, 80-ft early range, 82 of 87,
  90.6–92.5 km).

### well_depth_vs_water (85)
- **The diagonal label collides with a data point (D).** "water level at the bottom of the well" starts exactly on the
  OSE well-log square at (630 ft, 480 ft): "wa▢ter level". *Fix:* move the label's anchor to `x=ymax*0.55` (on the
  diagonal, about 330 ft), with `ax=60, ay=25` toward the empty lower right, or put it horizontally at the line's
  lower end, beyond 600 ft.
- **Orphan words (D).** The title wraps to 3 lines with "down" alone on the last line, and the subtitle leaves
  "lower)" alone. *Fix:* shorten to "Where water is deeper, wells are drilled deeper (ρ = 0.63–0.64 within record
  types), but half of 181 wells have water 41–240 ft down", and drop "(axis flipped: deeper water is lower)" in favor
  of the y-axis title "Depth to water (ft, deeper ↓)".
- **"Within each record type" overstates the coverage (B, minor).** ρ is computed for 2 of the 3 types (the well logs,
  n = 5, aren't tested). *Fix:* "within the two larger record types".
- **Works well:** the causal phrasing is gone, ρ is reported within types with the pooled value labeled as inflated,
  the legend reads "102 shown, 2 off-chart", the excluded RG-54556x row is named, the brief-7 first-water caveat is
  present, and all numbers check out (0.644 / 0.633 / pooled 0.730; IQR 41.2–240; 8 within 25 km).

### depth_by_area (83)
- **The Placitas row is overplotted (D).** 127 wells sit in one row with ±0.2 jitter, so the orange diamonds hide most
  of the blue NMBGMR circles, and the dots partly hide the Cochiti median tick. *Fix:* use ±0.35 jitter for rows with
  n > 50, draw NMBGMR last (on top), use marker size 7 with `opacity=0.6`, and draw the median tick after the points
  (it already is) with a white outline.
- **Negative depths are unexplained (B/D).** Flowing wells plot left of 0 (Placitas about −26 ft), but this chart's
  caption doesn't say what a negative depth means. *Fix:* add "values below 0 = water above land surface (flowing
  wells)" to the caption, as the well-depth chart does.
- **Possible duplicates inside the Cuba-area n = 11 (B).** It counts the school well and 21.1W.28.143 (same location
  and depth) separately, and also the Smelser Well (see cuba_area_map). *Fix:* say "11 records at 9–11 wells", or
  deduplicate.
- **The title takes 3 lines and splits "22 / ft" (D).** *Fix:* use a non-breaking space, and shorten to "Depth to water
  was smallest around Cochiti-Peña Blanca (median 22 ft) and largest around Bernalillo-Rio Rancho (375 ft, mostly
  1987-2007 tests)".
- **Works well:** "Cuba area" now uses the project's 25 km everywhere, wells without a well depth are included (11 Cuba
  wells, 10–509 ft, 1957–2018), the unmapped well is disclosed, the record-type mix is in the title, and every
  median checks out (22.5 / 95 / 116 / 180 / 212 / 375).

### formation_properties__transmissivity_drawdown_ft2_per_day (79)
- **The headline overgeneralizes (B/A).** "Transmissivity varies more within formations than between them" compares
  the *single widest* formation (Madera, 4.79 orders) with the 2.65-order spread of medians. Only 3 of the 10
  formations with ≥3 values exceed 2.65 (Madera 4.79, Santa Fe 3.41, Point Lookout 3.32). The rest span less: Yeso
  2.56, Abiquiu 2.52, Agua Zarca 2.23, Abo 2.20, Alluvium 1.32, Ojo Alamo 0.74, Morrison 0.12. *Fix:* "Within three
  formations, transmissivity spans more (up to 4.8 orders, Madera Limestone) than the 2.6-order spread between
  formation medians", computed as `(within > between).sum()`. The report and findings.md repeat the general claim;
  fix them too.
- **The app's Well depth menu option prints a false finding (B/F).** `formation_properties(metric="well_depth_ft")`
  outputs "Ojo Alamo: median of 4 wells 148 ft, inside the middle half of all tested wells (237-587)". 148 is below
  237. The cause is the condition `if inside or len(oa) < 5`: when n < 5, the "inside" sentence is printed whatever
  the value. *Fix:* build the sentence from `inside` alone, and add the n < 5 hedge separately: "…below the middle
  half of all tested wells (237–587); with 4 wells, too few to say it differs."
- **The other metrics' auto-titles rest on tiny groups (B, minor).** The Well depth title takes its "within" span from
  the Morrison Formation (3 values at 2 wells). *Fix:* compute the within-formation spans only for formations with
  ≥ `min_wells` wells.
- **The denominators differ (B/H, minor).** The caption says "54 of 179 rows" have no formation (all tests), while the
  finding says "22 wells" (transmissivity only). *Fix:* use the same basis: "22 of the 108 wells with a value have no
  recorded formation".
- **Works well:** medians are now per well (Ojo Alamo 94.2 from 4 wells, inside the IQR, "too few to say it differs"),
  "values · wells" labels on every row, the subtitle's double parentheses are fixed, the dotted line is drawn below,
  and the numbers check out (108 wells, 136, 27.5–988, 2,760, 6.2).

### cuba_area_map (86)
- **One well is counted twice and not disclosed (B).** The "16 wells" include the BIA-(RF)-033-2(10) Smelser Well
  twice: one row with formation San Jose at 8.77 km, and one with no formation at 9.14 km, both on the same date
  (1977-05-24) with the same well depth (206 ft) and water level (51 ft). With the school-well pair this chart already
  discloses, the distinct wells are probably 14, not 16, and those with a level are 8–10. The same count is on the
  Cuba KPI tile and in cuba_nearest_records. *Fix:* in `data._aquifer_tests`, flag rows with the same `site_name`,
  `date`, `well_depth_ft` and `depth_to_water_ft` within 1 km as one well, or say "16 well records (14–16 wells)".
- **Labels collide with markers (D).** An orange dot covers the "C" of "Cuba", a green dot touches "25 km", and an
  orange dot sits on the "S" of "San Ysidro". *Fix:* add the town and ring-label traces after the data, use
  `"bottom left"` for Cuba, and move the ring labels to the 135° bearing (`lab_la[5]`), where there are no sites.
- **Empty frame (D).** About a third of the width is blank on each side. *Fix:* use a narrower export width (about
  760 px) for both maps.
- **Works well:** all three rings now fit, the numbers check out (16 test keys, each tested on one date, 1957–1979;
  10 with a level, 1957–1978; 17.8 ft at 0.71 km; WL-0062 at 38.5 km, 2 readings in 2017), the double-count note for
  the school well is there, and the "analysis choice, not an official boundary" caveat is included.

### cuba_nearest_records (88)
- **"16 wells" carries the same possible duplicate (B).** See cuba_area_map. *Fix:* the same deduplication.
- **The report figure is unreadable at column width (D/J).** `report.tex` places this chart in a one-column `figure`
  at `width=\linewidth` (about 3.4 in). The 1,000-px PDF scales its 15-px labels to about 3.5–4 pt; I checked by
  rendering page 4. *Fix:* use `figure*` at `\textwidth`, or export a 560-px-wide version for one-column use.
- **The subtitle gives no period (E).** *Fix:* "…its closest site, and that site's record years (records 1926–2026)",
  or drop "record years".
- **Works well:** the wrong clause from round 2 is gone; the title is now computed and correct ("within 25 km there
  are only one-time tests at 16 wells (1957-1979), 1 well log, and 1 stream gage"). The bar labels use 0.7 km, the
  footer no longer cites the outline, and every distance checks out (0.71 / 2.26 / 21.1 / 33.0 / 38.5 / 65.2 km).

### ojo_alamo_depth_map (82)
- **The arrow covers the value it points at (D).** The "Red lines … (3,000 ft here)" arrow ends on the plate's own
  "3000" contour label and strikes through it. *Fix:* move `PLATE_POINTS["contour_3000"]` about 25 px to the right of
  the label, or set `standoff=8` on the annotation.
- **There's no way to judge distance (D).** The crop has latitude ticks but no scale bar or ring, so "Cuba sits at the
  southeastern end…" can't be related to the 25 km Cuba area used elsewhere. *Fix:* draw a 25 km bar (the plate is
  1:1,000,000; at the 200-dpi crop scaled to 1,200 px, compute the px per km) or a 25 km circle around the "Cuba"
  label.
- **The label for map-reading is doubtful (C).** The first finding, read by eye from a 1990 interpretive contour map,
  is labeled *Measured*; elsewhere, Measured means a value computed from data. *Fix:* keep Measured but begin the
  finding with "Published map (read by eye):", or label it *Hypothesis* if the team prefers.
- **No value-level interaction (F, expected for an image).** *Fix:* none needed beyond the metadata table already
  provided. Optionally add hover points at the "Cuba" label and the 1,000-ft line with the read-off values.
- **Works well:** the gap from round 2 is closed with a properly attributed public-domain crop, the map is unchanged
  except for clearly styled labels, and the brief-5 caveats ("don't infer depletion or Cuba's source aquifer") are
  carried into a correctly labeled Hypothesis and an Insufficient-data finding. The "148-ft Cuba school well in 1957"
  checks out.

### ojo_alamo_vs_san_jose (84)
- **The published values are mislabeled (B/C).** The finding says "inside the published Lindrith-area range of
  43-118 ft²/day", and `report.tex` says "within the transmissivity range published for the formation's Cuba Mesa
  Member". In dataset 6 (Table 1), however, 4–11 m²/d is **Stone et al. (1983), "range from two tests"**, listed for
  the San Jose Formation with no location or member. Only SJ-2259 (9.4 m²/d ≈ 101 ft²/day) is Lindrith-area and Cuba
  Mesa Member. SJ-2259's value was also back-calculated from specific capacity with an assumed 70% well efficiency,
  not from a drawdown test. *Fix:* "100 ft²/day, close to the one published Cuba Mesa Member value near Lindrith (101,
  SJ-2259, from specific capacity) and inside the San Jose range compiled from Stone et al. 1983 (43–118)". Fix the
  caption's "(Cuba Mesa Member)", which applies to SJ-2259 only, and the report sentence.
- **The two published markers read as one range (D).** SJ-2259 (a single diamond at y + 0.22) and the Stone range
  (y + 0.32) are 0.1 apart, so the chart looks like one line with three diamonds. *Fix:* separate them by 0.2 and
  label each directly ("SJ-2259 (Lindrith)", "Stone et al. 1983, 2 tests").
- **Duplicate rows show as two dots (D/B, minor).** Specific capacity for San Jose shows "n=2" for one test event
  (two rows, both 0.30). *Fix:* plot one dot per test event, or print "n=2 values, 1 test".
- **Works well:** an honest title, test events and wells counted correctly (7 + 1; 7–8 wells), a log depth axis that
  separates the shallow cluster, computed ages (`date.today()`), and conversions that check out (43.1 / 118.4 / 101.2
  ft²/day).

### rio_puerco_visits (92)
- **Single-letter month ticks (D, minor).** "J F M A M J J A S O N D" in the right panel is ambiguous in isolation.
  *Fix:* use 3-letter ticks every other month, or `tickangle=-90` with full abbreviations.
- **The subtitle wraps onto two lines (D, minor).** *Fix:* "One dot per USGS field visit, station 08332525, 2019–2026;
  not a continuous record". The left/right explanation is already in the panel titles.
- **Works well:** this follows brief 4 exactly (dots only, hollow no-flow markers, "not a continuous record"), the
  three October visits are now spread sideways in the month panel, the labels alternate so Aug and Oct 2020 don't
  collide, the hypothesis is hedged, and every number checks out (4 visits at 6.89–20.4 ft³/s in Apr–May; 6 no-flow
  visits from Aug to Mar; gage 2.26 km away).

### rio_grande_quality (89)
- **The guideline note is crossed by the data (D).** The top-right note "for scale: EPA taste guideline ≈ 700-900
  µS/cm, far above this axis" sits at the height of the late-2018 peak (about 370 µS/cm), and the line runs through
  "far". *Fix:* raise the panel's y-range to 400, or place the note under the panel title (`y=1.0, yanchor="bottom"`,
  right-aligned).
- **The subtitle gives no period and leaves "data" alone on the second line (E/D).** *Fix:* "Monthly values at USGS
  08317400, Rio Grande below Cochiti Dam, 2003–2026 (the only long water-quality record in the data)".
- **Works well:** the period is now given per parameter, the guideline is on the figure, pH ticks read 7.5 / 8.0 / 8.5,
  the hypothesis is properly hedged, and all numbers check out (221.1–342.1; 7.8–8.3; median 293.8; Sen +0.225, MK
  p = 0.735; Sulphur Creek 4,210–5,000 µS/cm, pH 2.24–2.32; 72.5 km).

### canal_seasonal (90)
- **The tie to research question 6 is still indirect (A).** That's honest, but the chart answers "when do canals
  run", not anything about acequias. *Fix:* if a source documents it, add one sentence saying which communities the
  Cochiti East Side and Sile canals serve (Pueblo and acequia irrigation), so the chart answers part of RQ6.
- **Works well:** the month names now show in the hover, n is printed under every month, the winter caveat is
  quantified (8–14 vs 24 years), the panels share a y-axis, and the numbers check out (zero medians Dec–Feb; 86.3
  ft³/s in June; 2001–2025).

### bernalillo_river_vs_well (88)
- **The title describes levels, but the analysis uses changes (B).** "Well A's water level tended to rise in years
  with more river flow" doesn't match a change-vs-change scatter. *Fix:* "Well A's water level tended to rise in years
  when river flow increased (ρ = +0.54, n = 17)…".
- **The scatter y-scales differ without a note (D).** The main-well scatter spans ±4 ft and Well A's ±1 ft; the
  caption mentions different scales only for the left panels. *Fix:* add "the two scatters also use different
  vertical scales" to the caption.
- **The p-value is rounded differently (H, minor).** The panel shows "p = 0.03" while the findings say 0.027.
  *Fix:* use `:.3f` in the panel annotation.
- **Works well:** the reading guide fills the empty cell, depth ticks are every 5 ft (main) and 1 ft (Well A), the
  spans are computed (17 and 3 ft), the result is hedged ("suggestive, not firm", Bonferroni 0.053), and all numbers
  check out (ρ 0.539, n 17, permutation p 0.027; 0.124, n 22, p 0.58; gage 40.8 km; the near-Bernalillo gage ended
  in 1969).

### coverage_timeline (88)
- **The acequia gap isn't drawn (C/G).** The finding says no acequia records exist, but there is no acequia row, so
  the chart can't show the gap. *Fix:* add "Acequias" rows to both blocks (with "no records in the collected data"),
  as for water quality.
- **The count bins hide the USGS story (D, minor).** Four sites and two sites both fall in the "2-4 sites" bin, so the
  USGS row looks uniform. In dark mode the "1 site" and "2-4 sites" steps (`#4a4945` vs `#75736d`) are hard to tell
  apart. *Fix:* make the bins 1 / 2–4 / 5–20 / 20+, or print the count in the USGS cells; widen the two dark steps.
- **Works well:** the USGS row now counts locations (4), "since 1999" is computed, the neutral gray ramp keeps blue
  for water levels, the Cuba block is explicit, and the numbers check out (1998: 1 site, 1999: 4; NMBGMR 1997–1999 and
  2016–2019; 9 Cuba-area years, 1957–2018).

### evidence_matrix (86)
- **The rotated header touches the right edge (D).** The † in "OSE aquifer tests†" ends at the image edge. *Fix:*
  `margin.r=90`.
- **"None" is nearly invisible in dark mode (D).** The None cells (`grid` `#2c2c2a`) and the legend chip barely differ
  from the `#0e1117` background. *Fix:* use `#3a3936` for None in dark mode, with a 1-px outline.
- **The RQ7 row slightly undersells dataset 1 (B, minor).** The project's only RQ7 analysis (Bernalillo) uses dataset
  1's wells *and* river, yet "1 · USGS stats (wells)" is blank for RQ7. *Fix:* rate it "Partial†" (rated by the
  analysis), which keeps the title true.
- **Works well:** ‡ is now defined in the footer, each cell shows the brief's own word, the briefs' ratings match
  (spot-checked for briefs 1, 2, 4, 5, 6 and 7), and both findings are correctly labeled *Insufficient data*.

### aquifer_sensitivity_classes (86)
- **Its analytical value is low (A).** It answers RQ8 only as a gap. That's honest, but it's a page of bars about an
  unlocatable table. *Fix:* keep it last on the page (it is), and consider moving it to an expander.
- **"The shares are valid" is slightly overstated (B).** `Shape__Area` values around 0.003 are almost certainly
  degrees², and areas in degrees² shrink with cos(latitude) across New Mexico, so the shares are approximate (by a
  few percent). *Fix:* "the units appear to be square degrees, so the shares are approximate".
- **Works well:** the area share has been added (High 25% of polygons but 48% of area), the brief-3 rules are
  followed (no mapping, "map units", "not Cuba"), and every number checks out (613; 152 / 339 / 122; 24.8 / 55.3 /
  19.9%; 47.5 / 36.0 / 16.5%).

## Suite scores

### G. Coverage of questions and planned outputs: 27 / 30
- **Present:** a county map, a Cuba-area map and nearest-record view, the new attributed HA-720-B geologic figure
  (closing the biggest round-2 gap), time series (hydrographs, trends, Placitas), comparisons by area and by aquifer
  unit, two coverage views, and the RQ9 indicator table. The indicator table now uses measured first-to-last changes
  (−16 to +8 ft; checked: Bernalillo main −16.0, Sandia +7.8). Missing data for research questions 3, 5 and 6 is shown
  honestly through the Cuba info box, page warnings, and Insufficient-data findings.
- **The San Jose side of the Cuba-area view is tabular only (−1).** Brief 6 / dataset 6 has the Cuba Mesa Member maps
  (e.g. Fig. 8, the head surface, and Fig. 10, wells with ≥3 water levels). *Fix:* add an attributed crop like the
  Ojo Alamo one.
- **The acequia gap isn't visualized (−1),** only stated in a warning (see coverage_timeline).
- **Water quality by area exists only for rivers (−1),** which is disclosed.

### H. Consistency across charts: 17 / 20
- **Good:** "Cuba area" means 25 km everywhere, including depth_by_area. Counts now use "sites" (locations) vs "wells"
  consistently, gray is used for counts and ratings, blue is reserved for water level, footers are anchored the same
  way, and the finding labels and caption structure are uniform.
- **The San Jose published values are described three ways (−1):** "Lindrith-area range" (finding and findings.md),
  "Cuba Mesa Member" for both values (caption), and "range published for the formation's Cuba Mesa Member" (report).
  Table 1 supports none of these for the 43–118 range.
- **The docs contradict the charts (−1).** `docs/analysis.md` → Colors says "Counts and ratings: one blue scale,
  darker = more", but the charts and `theme.py` use a gray ramp. The `docs/findings.md` RQ2 short answer still says
  "Deeper wells usually reach water deeper down" (the causal wording the chart dropped) and "vary over 1,000-fold
  within formations" (true for 3 formations only).
- **Mixed meanings of a label and a rounding (−1).** *Measured* is used for a by-eye map reading (Ojo Alamo map);
  "p = 0.03" in the Bernalillo panel vs 0.027 in its findings; "16 wells" vs a disclosed "two may be the same well"
  without adjusting the count.

### I. Reproducibility and code quality: 26 / 30
- **Good:** a fresh export of the staged index builds all 18 charts and the indicator table. `test_stats` passes,
  paths come from `__file__`, raw data are untouched, the prep is documented in `data.py` and `docs/analysis.md`,
  almost all numbers in titles and captions are computed (the round-2 hand-typed list is fixed), and the code is
  readable and well commented.
- **A logic bug produces a false sentence (−1.5).** In `formation_properties`, `if inside or len(oa) < 5` prints
  "inside the middle half" for the Well depth metric (148 vs 237–587). See that chart.
- **A few literals can go stale (−1):** "ten visits" (Rio Puerco hypothesis; `len(rp)` is available), "seven towns"
  (from `AREA_ANCHORS`), "Two of the well names may be the same well" (detected in the Ojo Alamo function but typed in
  the map), "fewer than 9 months" in the Bernalillo caption (`MIN_MONTHS_PER_YEAR`), and the page-text counts on Data
  sources ("30 monitoring sites", "456 … from 87 wells", "6 wells", "10 … visits", "613").
- **Documentation drift (−1):**
  - `docs/analysis.md` says `data3 … Counts polygons by class; nothing else`, but the chart now also sums
    `Shape__Area`.
  - The `stats.py` docstring says "Only numpy and the standard library are used", but the module imports pandas.
  - `docs/streamlit-app.md`'s Cuba-page row omits the new Ojo Alamo map.
  - `figure_index.csv` and `report/analysis_figures.tex` are stale (they say "1926-2024 records"; the code and PNGs
    say 1926–2026). A subset export (`export_figures <keys>`) doesn't rewrite them.
- **Unverified floor (−0.5).** `st.plotly_chart(..., alt=...)` is used, but I could only confirm that `alt` exists in
  Streamlit 1.66 (installed here), not at the declared floor `streamlit>=1.50`. *Fix:* test once on 1.50, or raise the
  floor to the version you tested.

### J. Integration: 17 / 20
- **Good:** every chart is on its matching page with takeaway, subtitle, scope, caption, labeled findings, table and
  CSV download; the fresh screenshots confirm this on all 7 pages. Static exports exist for all 18 charts (PDF for
  LaTeX, PNG for slides and docs). `docs/analysis.md` and `findings.md` are generated and match the code exactly (I
  diffed every title, subtitle and caption). The Results text is merged into `report.tex`, which compiles cleanly.
- **Report Figure 3 is unreadable (−1.5):** `cuba_nearest_records` at one-column width prints at about 3.5–4 pt.
  Its caption source "all project datasets" is also less precise than the rubric asks.
- **The report repeats two overstated claims (−0.5):** "Aquifer properties vary more within formations than between
  them" and the San Jose "Cuba Mesa Member range".
- **Generated artifacts are out of sync (−0.5):** `analysis_figures.tex` and `figure_index.csv` are stale (see I).
- **App detail (−0.5):** on Data sources, the indicator table's Caveat column runs past the page width, so the last
  column needs horizontal scrolling. *Fix:* set `column_config` widths, or move Caveat into a second line of Value.

**Suite score = 27 + 17 + 26 + 17 = 87.**

## Overall

- Average chart score: **86.1** (1,549 / 18 = 86.06)
- Suite score: **87**
- **Overall = 0.7 × 86.06 + 0.3 × 87 = 86.3**

(`score_history.md` needs a round-3 row; I didn't edit it because this review may change only this file.)

## Top 10 fixes (ordered by expected overall gain)

1. **Sweep the docs and terms for consistency (≈ +0.8).**
   - Fix the color-ramp sentence and the data3 prep row in `docs/analysis.md`.
   - Fix the `findings.md` RQ2 short answer ("Where water is deeper, wells are drilled deeper"; "within some
     formations").
   - Describe the San Jose published values the same way everywhere: SJ-2259 Lindrith / Cuba Mesa Member = 101;
     Stone et al. 1983 San Jose range = 43–118. This applies to the finding, caption, findings.md and report.
   - Fix the `stats.py` docstring and the `streamlit-app.md` Cuba row.
   - Effect: H +1.5, I +1, one chart B +1.
2. **Fix report integration (≈ +0.45).** Make Fig. 3 `figure*` at `\textwidth` (or export a narrow version), give it
   a precise source, run a full `export_figures` so `analysis_figures.tex` and `figure_index.csv` match the code, and
   remove the two overstated report sentences. Effect: J +1.5.
3. **Static-export layout pass (≈ +0.3).** Use a small `title_standoff` for x-axis titles so they stop crowding the
   footer (6 charts), non-breaking spaces between numbers and units in titles ("13 ft", "22 ft"), shorter
   well-depth and depth-by-area titles with no orphan words, and less space between legends and plots. Effect: D +1
   on about 8 charts.
4. **Fix `formation_properties` (≈ +0.3).** Fix the `inside or n < 5` bug (false Well-depth finding), rewrite the
   headline to the computed count ("within three formations…"), compute within-spans only for formations with ≥3
   wells, and unify the denominators. Effect: B +3 and F +1 on the chart, I +0.5.
5. **Fix text-over-mark collisions (≈ +0.23).** Move the well-depth diagonal label off the 630/480 well-log marker,
   the Rio Grande guideline note off the 2018 peak, the Placitas † note below the axis, and the Ojo Alamo "3,000"
   arrow off the plate label, and widen the evidence-matrix right margin.
6. **Fix map labels and whitespace (≈ +0.16).** Draw town and ring labels after the data (Bernalillo, Placitas, Rio
   Rancho, Cuba, "25 km", San Ysidro), offset them from clusters, and export both maps at about 760 px wide.
7. **Deduplicate test wells (≈ +0.15).** The Smelser Well appears twice (8.77 vs 9.14 km, same date, depth and
   level). Flag same-name / same-date / same-depth rows within 1 km as one well, and report "14–16 wells" and "8–10
   with a level", or deduplicate in all counts (Cuba map, nearest records, KPI tile, depth_by_area).
8. **Ojo Alamo vs San Jose markers (≈ +0.12).** Separate and directly label "SJ-2259 (Lindrith)" and "Stone et al.
   1983, 2 tests", note that SJ-2259's T comes from specific capacity, and show one dot per test event.
9. **Depth by area (≈ +0.12).** Spread out the Placitas row (wider jitter or a beeswarm, NMBGMR on top, lower
   opacity), and explain negative depths (flowing wells) in the caption.
10. **Small honesty and coverage items (≈ +0.1–0.2).** Reword the Bernalillo title to "when river flow increased";
    add acequia rows to the coverage timeline (G +1); compute the remaining literals ("ten visits", "seven towns",
    "9 months", the Data-sources page counts); use "Published map (read by eye)" for the Ojo Alamo map finding.

## Numeric spot-checks

All recomputed with my own code from the CSVs. I used pyproj (EPSG:26913 → 4269) for UTM, my own haversine, Sen's
slope and tie-corrected Mann-Kendall, `scipy.stats.spearmanr`, my own permutation test, and matplotlib's `Path` for
point-in-polygon. I didn't use the project's loaders. Scripts: `/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/grader3/v1.py`, `v2.py` and `v3.py` in the same folder.

| # | Claim (chart) | Recomputed | Match |
|---|---|---|---|
| 1 | 272 sites; 96 / 154 / 22; 85% east of 106.75° W; 18 within 25 km; 3 outside the county line (county map) | 272; 96 / 154 / 22; 85.29%; 18 = 16 tests + 1 log + Rio Puerco; 3 outside (Hunters Ridge, R23, USGS-08313350) | Yes |
| 2 | 5 of 9 wells falling, 3 rising; Sandia +13 ft since 2007; 65–95 km; 37-ft panels (hydrographs) | 5 / 3 / 1; 2007 492.05 → 2025 478.84 = 13.2 ft; 65.2–95.2 km; 34.7 × 1.08 = 37.5 | Yes |
| 3 | 2016–25: 4 of 7 falling, only Sandia rose; Lincoln −0.40 to −0.36; Bernalillo −0.52, no recent trend; Sandia +0.57 / +0.72 (trends) | 4 of 7 (Lincoln ×3, Dome Road); Sandia +0.722 / +0.726; Bernalillo recent −0.055, p = 0.86; −0.403 to −0.360; −0.522; +0.572 | Yes |
| 4 | 5 wells; 3 within 5 ft; PC-014 +51; PC-025 −57; 80-ft early rise; 63-day gap; 82 of 87; ~90 km (Placitas) | PC-002 +1.0, PC-019 −1.5, PC-055 +3.4; +50.9; −57.2; 80.4; median 63 days; 82 of 87; 90.6–92.5 km | Yes |
| 5 | ρ 0.63–0.64 within types, pooled 0.73; 181 wells; IQR 41–240; medians 53 / 165 / 240; 8 within 25 km; water column 142; 2 flowing; 1930–2022 (well depth) | 0.633 / 0.644, pooled 0.730; 181; 41.2–240.0; 52.8 / 164.7 / 240; 8; 141.8; 2; 1930–2022 | Yes |
| 6 | Medians 22 / 95 / 116 / 180 / 212 / 375; n 28 / 11 / 127 / 12 / 16 / 11; Cuba 11 wells 10–509 ft, 1957–2018; Bernalillo-RR 9 of 11 tests 1987–2007; 1 unmapped (depth by area) | 22.5 / 95.0 / 116.3 / 179.5 / 211.5 / 374.9; same n; 10 tests + 1 log, 10–509, 1957–2018; 9 tests (1987–2007) + 2 NMBGMR; 1 | Yes (Cuba n includes possible duplicates) |
| 7 | T: 108 wells, median 136, IQR 27.5–988; 22 without formation; OA 94.2 from 4 wells; Alluvium 2,760; Point Lookout 6.2; Madera 4.8 vs medians 2.6 orders (formation) | 108; 135.5; 27.5–988.5; 22; 94.25 (5 values, 4 wells); 2,759.5; 6.2; 4.79 vs 2.65. **Only 3 of 10 formations span > 2.65** | Numbers yes; headline overgeneralized |
| 8 | Well-depth menu: "Ojo Alamo median of 4 wells 148 ft, inside the middle half (237-587)" (formation, app) | OA per-well median 148 (788, 148, 48, 148); all-wells IQR 237–587, so 148 is **below** | **No** |
| 9 | 16 wells with one-time tests 1957–1979; 10 with a level 1957–1978; 18 ft at 0.7 km in 1957; WL-0062 at 38 km, 2 readings in 2017 (Cuba map) | 16 test keys, each on 1 date; 10 with a level; 17.8 ft at 0.71 km; 38.5 km, 2 readings. **Smelser Well appears twice** (8.77 / 9.14 km, same date, depth and level) | Numbers yes; likely 14–15 distinct wells |
| 10 | Nearest site per dataset: 0.7 / 2.3 / 21 / 33 / 38 / 65 km (nearest records) | 0.71 / 2.26 / 21.08 / 32.96 / 38.48 / 65.22 | Yes |
| 11 | 8 events (7 OA, 1 SJ), 1953–1977, 1–45 km; OA 18–24 ft within 5 km, 10–604 at 19–45 km; SJ 9 km, 51 / 206 / 100; published 43–118; school well 148 ft in 1957 (Ojo Alamo) | 7 + 1 events, 7 + 1 keys; 1953–1977; 0.7–44.9 km; 17.8–24; 10–604 at 19.5–44.9; 8.8 km, 51 / 206 / 100; 4–11 m²/d → 43.1–118.4 (Stone et al. 1983, not Lindrith); 148 ft, 1957 | Numbers yes; attribution no |
| 12 | Flow on all 4 Apr–May visits, none of 6 Aug–Mar; 6.89–20.4 ft³/s; gage 2 km (Rio Puerco) | Apr 2019 19.4, May 2020 20.4, Apr 2021 6.89, Apr 2024 20.2; dry Oct 2019, Aug 2020, Oct 2020, Oct 2024, Dec 2025, Mar 2026; 2.26 km | Yes |
| 13 | SC 221–342 (90% of months, 2003–2026), pH 7.8–8.3 (2004–2025); median 294; +0.2/yr, p = 0.74; Sulphur Creek 4,210–5,000, pH 2.2–2.3; 73 km (Rio Grande) | 221.1–342.1 (n = 266); 7.8–8.3; median 293.8; Sen +0.225, MK p 0.735; 4,210–5,000, 2.24–2.32 (Oct–Nov 2024); 72.5 km | Yes |
| 14 | Zero median Dec–Feb; peak 86 ft³/s in June; 2001–2025; winter n 8–14 vs 24 (canals) | Same; Cochiti East Side, June, 86.3 | Yes |
| 15 | Well A ρ +0.54, n = 17, p = 0.027; main ρ +0.12, p = 0.57; depths 31 / 52 ft; spans 3 / 17 ft; gage 41 km; 87 km; near-Bernalillo gage stopped 1969 (Bernalillo) | 0.539, 17, perm p 0.027; 0.124 (n = 22), p 0.58; 31.1 / 52.3; 3.0 / 17.4; 40.8; 87.2; last month 1969-09 | Yes |
| 16 | USGS sites 1998–2026, all 4 from 1999; NMBGMR 1997–1999 and 2016–2019; Cuba-area records from 9 years, 1957–2018 (coverage) | 1998: 1 site, 1999: 4; NMBGMR years 1997, 1998, 1999, 2016–2019; 9 years (1957, 1960, 1962, 1971, 1972, 1977, 1978, 1979, 2018) | Yes |
| 17 | 613 polygons, 152 / 339 / 122; area shares 48 / 36 / 16% (sensitivity) | 613; 152 / 339 / 122; 47.5 / 36.0 / 16.5% | Yes |
| 18 | Indicator table: water-level change −16 to +8 ft, first to last full year (Data sources, RQ9) | −16.0 (Bernalillo main) to +7.8 (Sandia) | Yes |
| 19 | Data sources page: 30 USGS sites; 456 measurements from 87 wells; 6 well logs 1978–2022; 10 Rio Puerco visits | 30 (17 stream, 9 well, 2 canal, 2 lake); 456 rows, 87 wells; 6 logs 1978–2022; 10 | Yes |
