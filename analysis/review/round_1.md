# Round 1 review: visualization suite

Graded against `analysis/review/RUBRIC.md`. Grader: independent reviewer (round 1).
Code state graded: `analysis/charts.py` as of 2026-10-31 19:48 (matches `figure_text.json`).

## Scores at a glance

| | Score |
|---|---|
| Average chart score (15 charts) | **74.5** / 100 |
| Suite score (G+H+I+J) | **66** / 100 |
| **Overall = 0.7 × 74.5 + 0.3 × 66** | **72.0** |

### Before reading: the round-1 static PNGs are broken by the render step, not by the charts

All 15 files in `/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/round1/static/` and `/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/round1/dark/` are **979 × 700 px**: Kaleido's default 700 × 500 at
scale 1.4. `pio.write_images(figs, paths, scale=1.4)` in `prep_round.sh` ignored each figure's
`layout.width/height` (1100 × 473–900). The result is that every title, subtitle and footer is cut off at the
right edge, and both maps are cropped. In the county map that crop removes most of the Rio Grande corridor,
which is the "85%" the title talks about. The project's own export path, `fig.to_image()` as used in
`export_figures.py`, renders correctly. I checked this by re-rendering all 15 charts at their true size
(`/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/grader/static_*.png` and `dark_*.png`), and I graded layout from those re-renders.
**Fix the review harness before round 2:** pass `width=[f.layout.width …]` and `height=[…]` to
`write_images`, or loop `fig.write_image(path, scale=1.4)`. The pre-wrapped titles (92 characters at
1100 px) also make the static figures fragile: any export at a different width will clip them again.

The app screenshots in `/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/round1/app/` date from 19:46–19:47, before the 19:48 edits to `charts.py` and
`cuba.py`. For example, they show "nearest *repeated* groundwater-level record", but the current code
says "of any kind". I graded the current code.

## Per-chart scores

| Chart key | A (15) | B (25) | C (15) | D (20) | E (10) | F (10) | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| county_coverage_map | 13 | 21 | 12 | 12 | 7 | 9 | **74** |
| groundwater_hydrographs | 12 | 17 | 12 | 15 | 8 | 10 | **74** |
| groundwater_trends | 14 | 20 | 13 | 17 | 9 | 10 | **83** |
| placitas_remeasured | 12 | 15 | 9 | 17 | 8 | 9 | **70** |
| well_depth_vs_water | 14 | 16 | 13 | 12 | 5 | 10 | **70** |
| formation_properties__transmissivity_drawdown_ft2_per_day | 11 | 8 | 11 | 13 | 6 | 9 | **58** |
| cuba_area_map | 14 | 17 | 12 | 15 | 8 | 10 | **76** |
| cuba_nearest_records | 14 | 18 | 12 | 15 | 8 | 10 | **77** |
| ojo_alamo_vs_san_jose | 11 | 15 | 10 | 13 | 8 | 10 | **67** |
| rio_puerco_visits | 13 | 22 | 14 | 17 | 9 | 10 | **85** |
| rio_grande_quality | 12 | 20 | 13 | 16 | 8 | 10 | **79** |
| canal_seasonal | 13 | 20 | 14 | 17 | 9 | 10 | **83** |
| bernalillo_river_vs_well | 9 | 14 | 11 | 12 | 9 | 8 | **63** |
| coverage_timeline | 14 | 19 | 13 | 18 | 8 | 8 | **80** |
| evidence_matrix | 14 | 19 | 11 | 16 | 9 | 10 | **79** |
| **Average** | | | | | | | **74.5** |

## Per-chart findings

### county_coverage_map (74)
- **Water-level sites are hidden under orange dots (D).** Traces are drawn in the order water-level, then
  well construction, then surface water. In the Placitas–Bernalillo cluster, the 87 NMBGMR wells (blue) are
  buried under the OSE aquifer-test dots, so the map seems to show about 10 of the "96" water-level sites.
  *Fix:* draw "Water-level records" last; use smaller markers with opacity around 0.7; add a zoomed inset
  for the Rio Grande corridor, or use a second map for it.
- **Town labels are missing (D).** MapLibre's label-collision rule silently drops the Rio Rancho and
  Placitas labels, and "Bernalillo" sits on top of the dots. *Fix:* use annotations or a separate text layer
  with offsets, or label only Cuba, Cochiti, Bernalillo and Jemez Springs.
- **The "eastern side" is never drawn (A/B).** The title's "85% … eastern, Rio Grande side" uses an
  unstated cut at longitude −106.75 that the map doesn't show. *Fix:* say "east of 106.75° W" in the caption
  and draw a faint dashed meridian.
- **"Sites" mixes very different kinds of record (C).** The count lumps one-time 1930–2008 tests together
  with monitoring sites. Brief 7: "well-log counts do not indicate monitoring density." *Fix:* add to the
  caption "a dot is a site with any record, not active monitoring".
- **Source is too vague (E).** "All project datasets" can't be traced to files. *Fix:* list the files, as
  the other charts do.
- *Works well:* the numbers are correct (272 sites; 85%; 18 within 25 km; 96 / 154 / 22), the hover is rich,
  and the three data-type colors are a sound, consistent encoding.

### groundwater_hydrographs (74)
- **The title hides a rising well (B).** "Water levels fell at 3 of 4 monitored sites" counts the Bernalillo
  site as falling, but its Well A (PIEZ 2) *rose* +0.12 ft/yr over the full record (Mann-Kendall p = 0.005,
  recomputed). *Fix:* "At 3 of 4 sites at least one well fell; the Bernalillo shallow piezometer and the Sandia
  wells rose", or compute per-well counts.
- **The caption's reading advice is wrong (B/D).** Independent y-scales make Dome Road's 3-ft decline over
  27 years look as steep as Bernalillo's roughly 20-ft decline. The caption says "compare the shape of each
  line", but slope is scale-dependent too. *Fix:* give every panel the same y-span (for example 35 ft), or
  print the span in each panel ("scale: 3 ft").
- **One line hides another (D).** "Well" (blue) is almost completely covered by "Well A" (orange) at Lincoln
  and Sandia, so readers see two wells where the legend promises three. *Fix:* dash one line, or note
  "Well and Well A nearly coincide".
- **Wrong distance (C/I).** The scope says "65-90 km from Cuba", but the wells are 65.2, 87.2, 88.6 and
  95.2 km away (the Sandia site is 95 km). The groundwater page caption says the closest is "about 38 km",
  while the chart's finding says 65 km. *Fix:* compute the range, and make the page caption match the chart.
- **Brief 1 caveat missing (C).** *Fix:* add "these are water-level indicators, not measures of remaining
  supply".
- *Works well:* monthly-only data, breaks at gaps, a flipped axis stated in the subtitle, and a properly
  hedged hypothesis.

### groundwater_trends (83)
- **Same independence assumption in the intervals (B).** The confidence intervals use the same Mann-Kendall
  variance (independent years) as the p-values. The caption tells readers to "read … its interval, not just
  the color", but the interval is just as optimistic. *Fix:* say both are optimistic, or use a block
  bootstrap or an effective-n correction for the interval.
- **One missing marker is unexplained (B/E).** Sandia Well B has no 2016-2025 marker and no note (its record
  ends in 2015), while Bernalillo Well A gets "too few recent years". *Fix:* annotate "no data after 2015";
  `well_trends` drops wells that have zero recent years.
- **Unequal record lengths are invisible (B).** Full-record periods differ (17–27 years) but show only on
  hover. *Fix:* add "(1999–2025)" in muted text to each row label, or put it in the table.
- **Hand-typed parts of the title (I).** The parenthetical "(Lincoln MS and Dome Road)" and "only the Sandia
  site" are typed in, and the scope distance "65-90 km" is wrong (95). *Fix:* compute the site names from
  the `rec` table.
- **Confusing legend keys (D).** The dark-gray period keys look like the gray "No clear trend" key.
  *Fix:* draw the period keys as hollow outline symbols.
- *Works well:* the method is stated, the full-record and recent periods sit side by side, intervals are
  shown, the direction arrows are clear, and all numbers match (−0.40 to −0.36; 4 of 7; −0.52; +0.57).

### placitas_remeasured (70)
- **Wrong scope distance (C).** "Placitas area … about 65 km from Cuba": the five wells are **90.6–92.5 km**
  away (recomputed with pyproj). *Fix:* compute the distance from the data.
- **The caption doesn't fit PC-002 (B).** "The 1997-99 readings were taken about every two months …
  most wells have a single 2016-19 reading" doesn't hold for PC-002: it has **one** 1997 reading (flagged
  `LevelStatus = R`) and **three** 2016-19 readings, so its zero-width shaded bar means nothing.
  *Fix:* print n per period beside each dot (for example "n=9 → n=1"); rubric B requires small sample
  sizes to be visible.
- **A data-quality flag is applied selectively (B/C).** PC-025's first reading is discounted because of the
  "R" flag, but *all eight* of PC-055's 1990s readings and PC-002's only baseline reading carry the same
  flag, and nothing is said about them. The measurement method also changes between periods (`T` in the
  1990s, `S` in 2016-19). Brief 2 asks to check "measurement methods, and data-quality flags". *Fix:* mark
  flagged baselines (hollow marker or †) and add the method change to the caption.
- **Selective title (A).** The title names the 51-ft drop but not the larger 57-ft rise. *Fix:* "…; one is
  51 ft deeper and one 57 ft shallower (unstable baseline)".
- **Inconsistent period label (E).** The findings say "1997-98" and the labels say "1997-99". *Fix:* pick one.
  The range bar is nearly invisible in dark mode (opacity 0.25 on dark blue).
- *Works well:* the dumbbell-with-arrow form is ideal for before/after, the labels are direct, and wells
  measured in only one period are excluded and that exclusion is disclosed.

### well_depth_vs_water (70)
- **The caption is backwards (E/B).** "Points far below the diagonal have a lot of water above the well
  bottom": the y-axis is flipped, so those wells plot **above** the diagonal. Points below it would have water
  below the bottom of the well, which is impossible. *Fix:* "Points far above the line have a lot of water
  above the well bottom; points near it have little."
- **The diagonal's label is never drawn (D).** The annotation "water level at the bottom of the well" sits at
  y = 760 while the axis ends at 634, so it is clipped and the line is unexplained. *Fix:* place it at
  x ≈ y ≈ 450.
- **An impossible data point is plotted and used (B).** RG-54556x (30-ft well, water at 458 ft) is plotted
  unflagged and included in r. *Fix:* exclude it as a likely data error and disclose that in the caption
  (or show it hollow).
- **One correlation across incompatible records (B).** The caption says "treat them as context, not one
  comparable series", yet the finding computes a single Pearson r = 0.63 and one median across all three
  record types (Spearman = 0.70). *Fix:* name the method, use Spearman, and give per-source n and median.
- **Truncated sources (E).** "data2" and "data7" are not file names. *Fix:* give the full paths.
- *Works well:* every number checks out (182; IQR 41–243; r = 0.63; median 142; 2 flowing wells), the
  off-chart wells are disclosed, and record type is encoded by both shape and color.

### formation_properties__transmissivity_drawdown_ft2_per_day (58)
- **The headline is false (B).** "the 5 Ojo Alamo tests (40-222 ft²/day) sit below the countywide median of
  74": two of the five (164 and 222) are **above** 74. Only the Ojo Alamo *median* (57.5) is below.
  *Fix:* "the Ojo Alamo median (58 ft²/day, n = 5) is below …".
- **"Countywide median" is mislabeled (B).** 73.5 is the median of the 94 tests that have a value **and**
  a formation. All **117** tests with a value have a median of **100**. The finding "across all 94 tests with
  a value" is also wrong. *Fix:* compute the median from all tests with a value, or relabel it "median of
  tests with a recorded formation".
- **Duplicate rows counted as separate tests (B).** Two of the five Ojo Alamo values (40 and 222) are rows
  for the same Cuba school well on 1957-08-01. San Jose's "n=1" still gets a median tick and a rank.
  *Fix:* group by well and date, and don't draw a median or rank a formation with fewer than 3 wells.
- **False precision in the title (A/B).** "more than 61,100-fold" comes from two 0.2 ft²/day Madera values.
  *Fix:* "spans more than four orders of magnitude within one formation".
- **Cluttered log axis (D).** Minor-tick labels ("5 2 5 2 …") clutter the axis. *Fix:* set
  `tickvals=[0.01, 0.1, 1, 10, 100, 1e3, 1e4]` with `ticktext` "10k" and drop the minor labels.
- **Findings and captions break for other measures (E/F).** The findings print "73.5" and "2.76e+03" with
  no units. When the app's selectbox switches to another measure, the caption still says "Higher
  transmissivity means …" and the title becomes generic. A latent bug: "Highest median among formations with
  ≥3 tests" reads from `keep`, which includes the focus formations whatever their n. *Fix:* write a caption
  and units per measure in `FORMATION_METRICS`, and filter by n before picking the top formation.

### cuba_area_map (76)
- **"Of any kind" is false (B/C).** "The nearest water-level record of any kind is 38 km from Cuba": 10 of
  the 18 aquifer tests within 25 km recorded a depth to water (the Cuba school well had water at 17.8 ft,
  0.7 km from the center, in 1957), and the 21-km well log records first water at 114 ft. *Fix:* "The
  nearest **repeated** (monitoring) water-level record is 38 km away".
- **Outer ring unlabeled (D).** The 50 km ring has no label (it is placed at the ring's north point, off the
  frame or hidden). *Fix:* put the labels at bearing 45° or 135°.
- **Cuba marker hides a site (D).** The black Cuba marker covers the Cuba school-well dot. *Fix:* draw the
  town marker as a hollow ring under the data, or offset it.
- **Source is too vague (E).** "All project datasets" again. *Fix:* list the files.
- *Works well:* the numbers are correct (16 wells, 1957–1979, one well log, one gage), the distance rings
  are a useful scale, and the 25 km radius is disclosed as an analysis choice.

### cuba_nearest_records (77)
- **"Groundwater-level record" needs "repeated" (B).** The title says "The nearest groundwater-level record
  is 38 km from Cuba", but the aquifer tests 0.7 km away recorded water levels. The same wording is in the
  Cuba page's metric and info box (`cuba.py`, "of any kind"). *Fix:* add "repeated" in all three places.
- **Label on top of a bar (D).** The "Cuba area (≤25 km)" text is drawn over the USGS monitoring-wells bar.
  *Fix:* anchor it at the top of the shaded band (`y=1, yanchor="bottom"`).
- **Mislabeled scope (C).** "Cuba area (within 25 km of Cuba)" doesn't fit a chart that reaches 65 km.
  *Fix:* "Cuba and the nearest record in each dataset".
- *Works well:* a clear, honest distance chart. The caption's "a short bar only means a site is close, not
  that it answers the question" is exemplary. Values check out (0.7, 21, 33, 38, 65 km).

### ojo_alamo_vs_san_jose (67)
- **Counting rows as tests (B).** "Only 10 aquifer tests … (8 Ojo Alamo, 2 San Jose)": the two San Jose rows
  are one 1977 test at the Smelser well, split into two rows, and two Ojo Alamo rows are the same 1957 test.
  That leaves about 8 test events at 6–7 wells. *Fix:* count tests by well and date, and report wells as well.
- **Misleading finding (B).** "the shallow values (18-24 ft) are the Cuba school well" leaves out the
  shallowest value, **10 ft**, at 23.1W.27.233, 19.8 km away. *Fix:* "18–24 ft at the Cuba school well and
  10 ft at a well 20 km away; the deep ones (339–604 ft) are 20–45 km away". Also drop "one well (1)".
- **The title overclaims (C).** "enough to describe them" doesn't fit a single San Jose well. *Fix:* "too
  few to describe either formation, let alone compare them".
- **Transmissivity values can't be read (D).** The transmissivity panel shows a single tick label ("100") on
  a log axis. *Fix:* use ticks [30, 50, 100, 200] or a linear axis. Label the depth panel "ft below land".
- *Works well:* every test is shown, n is given per panel, the possible duplicate well is disclosed, and the
  caption clearly says this doesn't identify Cuba's producing formation.

### rio_puerco_visits (85)
- **The seasonal claim isn't on the x-axis (A).** The title's claim is seasonal, but the x-axis is calendar
  date, so readers must read the month labels. *Fix:* add a small month-of-year strip (Jan–Dec) with the
  same dots, or order a second panel by month.
- **Labels touch (D).** "Aug" and "Oct" (2020) touch, and overlap at smaller widths. *Fix:* stagger the
  label positions (top/bottom).
- **"Dry" overstates the data (B/C).** The data say "no measurable flow" (`measurement_type` "Other"), which
  can include standing pools. *Fix:* use "no measurable flow" in the title and caption instead of "had water"
  and "dry".
- *Works well:* this follows brief 4 exactly (dots only, zero flow marked, not a continuous record), the scope
  is Cuba, the hypothesis is properly hedged, and all numbers match.

### rio_grande_quality (79)
- **Isolated months disappear (B/D).** `mode="lines"` drops single months between gaps (for example
  dissolved oxygen in 2014 and pH in 2018), so some data are invisible. *Fix:* use `lines+markers` with
  size-3 markers, or markers for points with no neighbours.
- **Panels that support nothing (A/D).** The dissolved-oxygen and turbidity panels support no finding.
  *Fix:* drop them or move them to the table, or add a finding for each.
- **Inconsistent ranges and false precision (B).** The title gives specific conductance as a 5–95% range but
  pH as min–max. "about 4,605 µS/cm" is the mean of two months (5,000 and 4,210); write "about 4,200–5,000".
- **Interpretation labeled as measurement (C).** "a natural geothermal stream" is an interpretation inside a
  *Measured* finding. *Fix:* move it to a Hypothesis or cite a source.
- **Loose, uncited reference value (E).** "drinking water is often under about 1,500 µS/cm" (the US EPA
  secondary limit of 500 mg/L total dissolved solids is roughly 800 µS/cm). *Fix:* cite a standard.
- *Works well:* honest about river versus groundwater, monthly data only, the trend is reported with
  p = 0.74, and every number matches.

### canal_seasonal (83)
- **Winter medians rest on few years (B).** December–February medians come from 8–14 years, against 21–24
  in other months; months not recorded may be unmeasured rather than zero. *Fix:* print n per month
  (muted, under the axis) and caveat "dry in winter".
- **Subtitle start year is wrong (B/I).** The subtitle says "2000-2025" (the `since` parameter) but the
  canal data start in 2001. *Fix:* compute the start year from the data.
- **Direct labels sit on the lines (D).** "Cochiti East Side" and "Sile" overlap the lines, and repeat the
  legend. *Fix:* put the labels at the right end (x = 12.4) and drop the legend.
- *Works well:* a clean seasonal profile with an interquartile band, clearly labeled as context rather than
  acequia data; the numbers match (Mar–Nov; 86 ft³/s in June).

### bernalillo_river_vs_well (63)
- **The chart doesn't show its own finding (A/D).** The claim is a correlation between *year-to-year
  changes* (ρ = −0.54), but the chart shows levels. On the shared 30–60 ft axis Well A is a flat line, so
  readers cannot see "rises in years the river runs higher". *Fix:* add two small scatters (Δ flow vs
  Δ depth, one per well) with ρ, n and p, and keep the time panels as context. If levels stay, give Well A
  its own scale.
- **Lines cross missing years (B).** Both wells lack 2007–2008 (fewer than 9 months), but `lines+markers`
  draws straight segments from 2006 to 2009. This breaks the project's "no interpolation across gaps" rule.
  *Fix:* insert None rows for missing years.
- **The title overstates the evidence (B/C).** "rises in years the river runs higher" is strong for
  ρ = −0.54 with n = 17 and two wells tested (no multiple-comparison note). "Shallower well" is asserted,
  although the well's construction is unknown (the hypothesis itself says so). *Fix:* "Well A's level
  tended to rise in years with higher river flow (ρ = −0.54, n = 17); the main well showed no link".
- **Missing tick and distant legend (D).** At export size the bottom panel has no 60-ft tick, and the legend
  sits far below the lines. *Fix:* set `dtick` and label the lines directly.
- **Statistics hidden from the app (F).** The correlation statistics live only in `Chart.notes`, which the app
  never shows. *Fix:* append the Δ series and ρ to the data table.
- *Works well:* two panels instead of a dual axis, the correlation is computed on differences to avoid shared
  drift, a permutation p-value is used, and the 40-km gage offset is disclosed.

### coverage_timeline (80)
- **"At all" is false (B).** "the Cuba area has no water-level … records at all": the Cuba-area aquifer tests
  include 10 one-time depth-to-water readings. *Fix:* "no repeated water-level monitoring".
- **Hover lacks the row (F).** The tooltip "%{x}: n site(s)" doesn't say which dataset row it is. *Fix:* put
  the row label in `customdata`.
- **Labels crowd (D).** The "Cuba area (≤25 km)" group header crowds the "Water levels" row label. *Fix:*
  give the headers their own row, as with "Whole county".
- **Hand-typed numbers (I).** The title and findings type in 1998, 1997-99 and 2016-19, and 2019-2026.
  *Fix:* compute them.
- *Works well:* a strong gap view with county and Cuba area split explicitly, "no records" written into empty
  rows, and binned sequential colors.

### evidence_matrix (79)
- **Wrong finding label (C).** The finding is labeled *Measured* although the caption says "a judgment
  summary, not a measurement". *Fix:* create a "Judgment" label, or phrase it as "Per the briefs, …".
- **Rates potential, not delivered work (B/C).** The Q4 "Strong" ratings come from datasets 5 and 6, which
  are PDFs the project never digitized or charted, so the matrix overstates how well Q4 is answered now.
  *Fix:* add a "used in a chart?" marker, or a caption line.
- **Too many cell words for four colors (D).** Eight different cell words ("Partial", "Best fit", "Useful",
  "Context", …) map onto four legend colors without a key. *Fix:* add the mapping to the caption, for example
  "Partial / Potential / Context → Limited".
- *Works well:* the ratings match the briefs (checked cell by cell), analysis-team ratings are marked with †,
  and the matrix is readable in both themes.

## Suite scores

### G. Coverage of questions and planned outputs: 21 / 30
- Present: county map, Cuba-area view, time series, aquifer-unit comparison, two coverage views, and an
  indicator table for research question 9. Gaps for questions 3, 5 and 6 are shown honestly (info box,
  warnings, evidence matrix).
- **Missing: the aquifer/geologic-region layer and the Ojo Alamo/San Jose extent view** that the proposal
  promised. Datasets 5 and 6 are unused; the briefs suggest annotated, attributed map figures. *Fix:* add an
  attributed figure of each formation map with Cuba marked, or a simple geologic-region layer.
- **Dataset 3 (aquifer sensitivity) appears nowhere**, not even on the Data sources page. *Fix:* list it,
  with the brief's "no geometry yet" caveat (and optionally a class-count bar chart).
- **No comparison by area.** For example, depth to water by area (Placitas vs Rio Rancho/Bernalillo vs the
  northwest) is missing. The brief-recommended NMBGMR "measurement counts per well" chart is also absent.
- `docs/findings.md` (the interpretation section) is still a stub.

### H. Consistency across charts: 13 / 20
- **Color meanings change between charts.** Blue, orange and aqua stand for the data types on the maps, but
  for Well / Well A / Well B, NMBGMR / OSE tests / well logs, Ojo Alamo / San Jose, two canals, and two
  periods elsewhere. Orange means "well construction" on the map but "Ojo Alamo" and "2016-19" elsewhere.
  *Fix:* reserve the three slots for data types and use another palette for wells, periods and formations, or
  document the convention.
- **"Water-level record" is used inconsistently.** The well-depth chart plots aquifer-test levels as depth to
  water, while three charts and the Cuba page say no water-level record of any kind exists near Cuba.
- **Distances disagree.** The groundwater page says 38 km, the hydrograph says 65 km, Placitas is given as
  "65 km" (actually 91), and the USGS wells as "65-90" (actually up to 95).
- Some scope strings are ad hoc ("Cuba and surroundings (within 60 km)") rather than the constants. Dark mode
  inverts the sequential ramps (acceptable, but undocumented). The finding labels and Chart structure are
  consistent throughout.

### I. Reproducibility and code quality: 19 / 30
- **`analysis/` and `data/sandoval_county_boundary.geojson` are untracked in git**, while the app pages that
  import them are modified. A fresh clone, or the live app after a push without them, crashes on every page.
  *Fix:* `git add analysis data/sandoval_county_boundary.geojson`.
- **About 25 hand-typed numbers** appear in titles, captions, scopes and findings, and two are already wrong.
  Examples: the scope distances, "82 of 87", "54 of 179", "1930-2008", "1930 to 2022", "18-24 ft",
  "339-604 ft", "Smelser … 9 km … 1977 (51 ft, 206 ft, 100)", "measured twice in 2017", "April-May",
  "Oct-Nov 2024", "December-February", "since 1998", "after 2008", and "Lincoln MS and Dome Road". These
  break the rubric and the module's own docstring ("Numbers in titles and captions are computed from the
  data").
- **`requirements.txt` has no version floors**, although the code needs Plotly ≥ 5.24 (`go.Scattermap`,
  `layout.map`) and a recent Streamlit (`st.context.theme`, `width="stretch"`, `:blue-badge[]`). *Fix:* e.g.
  `plotly>=5.24`, `streamlit>=1.46`.
- **Broken documentation references.** `data.py` says every preparation step is in `docs/analysis.md` under
  "Data preparation inside the analysis code", but that section doesn't exist. The `charts.py` docstring
  points to a non-existent `app_pages/_chart_helpers.py`.
- **Dead code**: `m = m[...] if False else m` (bernalillo), the useless `textfont.color` loop in
  `evidence_matrix`, and the unused `labels` and `months_flow`. **Latent bugs**: in `formation_properties`
  the "≥3 tests" top formation and "tests with a value" counts.
- Good: paths are built from `__file__`, raw data are untouched, the stats module is clean and documented, and
  loaders are cached and return copies.

### J. Integration: 13 / 20
- Strong: every chart appears on its page with takeaway, subtitle, scope, caption, labeled findings, and a
  table with CSV download. Charts follow the light and dark themes.
- **No static exports exist in the repository**: `report/figures/` is empty, `docs/figures/` and
  `analysis/figure_index.csv` don't exist, `report.tex` still has placeholders, and `docs/analysis.md` lists
  no charts. The round-1 static renders are clipped (see the note at the top). *Fix:* run
  `python -m analysis.export_figures`, commit the output, and embed the figures in `docs/analysis.md` and the
  report.
- **Page intros overpromise**: the County map page intro says it shows "major aquifer and geologic regions,
  and acequias", and the Water quality intro promises groundwater quality, before each page's warning says
  otherwise. *Fix:* rewrite the intros to describe what is actually shown.
- **Export legibility at 7 in**: the 1100-px static figures scaled to 7 in put 14-px text at about 6.4 pt and
  footers at about 5.3 pt. *Fix:* export at width ≈ 800, or scale fonts in `static()`.

**Suite score = 21 + 13 + 19 + 13 = 66.**

## Overall

- Average chart score: **74.5**
- Suite score: **66**
- **Overall = 0.7 × 74.5 + 0.3 × 66 = 72.0**

## Top 10 fixes (ordered by expected overall gain)

1. **Commit `analysis/` and the county GeoJSON; add version floors to `requirements.txt`; write the promised
   "Data preparation inside the analysis code" section in `docs/analysis.md`; remove dead code and stale
   references.** (I +5, about +1.5)
2. **Generate and commit the static exports** (`report/figures`, `docs/figures`, `figure_index.csv`); embed
   them in `docs/analysis.md` and `report.tex`; rewrite the County map and Water quality page intros to match
   what is shown. (J +5, about +1.5)
3. **Replace hand-typed numbers with computed ones, and correct the wrong ones**: Placitas ≈ 91 km (not 65);
   USGS wells 65–95 km (not 65–90); the groundwater page's "38 km" against 65 km; canal start year 2001.
   (I, C and B on 4 charts, about +1.4)
4. **Use "repeated (monitoring) water-level record"** in `cuba_area_map` ("of any kind"),
   `cuba_nearest_records`, `coverage_timeline` ("at all") and `cuba.py`; mention the one-time levels from
   1957–79 tests near Cuba. (3 charts plus H and J, about +1.1)
5. **Fix the `formation_properties` headline and findings**: the false "5 Ojo Alamo tests below the
   countywide median"; the true countywide median is 100 (117 tests); group by well and date; no median or
   rank for n < 3; units; explicit log ticks; a caption per measure. (about +1.0)
6. **Make color meanings consistent across the suite**: reserve blue, orange and aqua for the three data
   types; use another palette (or line style) for wells, periods and formations. (H +3, about +0.9)
7. **Bernalillo**: add Δ flow vs Δ depth scatters (the actual analysis), break lines at 2007–08, soften the
   title, drop "shallower", and show the statistics in the table. (about +0.8)
8. **Well depth vs water**: fix the backwards caption (above the line = more water column), move the diagonal
   label into range, flag or exclude RG-54556x, and use and name Spearman with per-source statistics.
   (about +0.65)
9. **Ojo Alamo vs San Jose**: count test events and wells (not CSV rows); fix the "shallow values are the Cuba
   school well" finding (the 10 ft value is 20 km away); retitle "too few to describe either"; add readable
   log ticks. (about +0.55)
10. **Placitas**: show n per period on the chart; mark `LevelStatus = R` baselines consistently (PC-002,
    PC-055, PC-025); disclose the T→S method change; name the 57-ft rise in the title. (about +0.5)

Next in line: give the hydrograph panels equal y-spans (or print each span) and correct its title; draw water
levels on top on the county map, with a corridor inset; small layout fixes (the nearest-records annotation
collision, the 50 km ring label, canal labels, Rio Puerco month labels, Rio Grande isolated months, the
coverage hover row name); relabel the evidence matrix's "Measured" finding.

## Numeric spot-checks

I recomputed these independently from the CSVs, using my own Sen's slope and Mann-Kendall, my own haversine
distances, and pyproj (EPSG:26913 → 4269) for UTM, rather than the project's loaders. Scripts are in
`/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/grader/verify1.py` … `verify5.py`.

| # | Claim (chart) | Recomputed | Match |
|---|---|---|---|
| 1 | 272 sites; 85% east; 18 within 25 km; 96 / 154 / 22 (county map) | 272; 85.3%; 18; 96 / 154 / 22 | Yes |
| 2 | Sandia site risen 13 ft since 2007 (hydrographs) | 2007 annual mean 492.05 → 2025 478.84 = 13.2 ft | Yes |
| 3 | "Water levels fell at 3 of 4 sites" (hydrographs) | Main wells yes; Bernalillo Well A **rose** +0.12 ft/yr (p = 0.005) | Partly (misleading) |
| 4 | Lincoln full-record −0.40 to −0.36 ft/yr; 4 of 7 declining in 2016-25; Bernalillo ≈ −0.5; Sandia ≈ +0.6 (trends) | −0.403 to −0.360; 4 of 7; −0.522; +0.572 | Yes |
| 5 | USGS wells "65-90 km from Cuba" (hydrographs, trends) | 65.2, 87.2, 88.6, 95.2 km | **No** |
| 6 | 5 wells in both periods; 3 within 5 ft; +51 ft; −57 ft; 82 of 87 (Placitas) | 5; 3; +50.9; −57.2; 82 | Yes |
| 7 | Placitas "about 65 km from Cuba" | 90.6–92.5 km | **No** |
| 8 | 182 wells; IQR 41–243 ft; r = 0.63; median column 142 ft; 2 flowing (well depth) | 182; 41.3–243.3; 0.632 (Spearman 0.70); 141.6; 2 | Yes (plus 1 impossible row unflagged) |
| 9 | "5 Ojo Alamo tests (40-222) sit below the countywide median of 74" (formation) | Values 40, 57, 57.5, 164, 222: **2 above 73.5**; all-test median = **100** (117 tests) | **No** |
| 10 | "Median across all 94 tests with a value: 73.5" (formation) | 94 = tests with a value **and** a formation; 117 have a value | **No** |
| 11 | 61,100-fold spread (formation) | Madera 12,232 / 0.2 = 61,160 | Yes (fragile) |
| 12 | 16 wells with tests in 1957–1979, one well log, one gage within 25 km (Cuba map) | 16 wells (18 tests), 1957–1979; SJ 04288 at 21 km; Rio Puerco gage | Yes |
| 13 | Nearest water-level record 38 km, "of any kind", measured twice in 2017 (Cuba map) | WL-0062, 38.5 km, 2017-09-13 and 2017-12-26; but 10 tests within 25 km recorded depth to water (17.8 ft at 0.71 km) | **No** ("of any kind") |
| 14 | Nearest aquifer test 0.7 km (1957); USGS wells 65 km; surface-water statistics 33 km (nearest records) | 0.71 km, 1957-08-01; 65.2; 33.0 | Yes |
| 15 | 10 tests (8 Ojo Alamo, 2 San Jose), 1953–1977, 1–45 km; depth to water 10–604; "shallow values 18–24 ft are the Cuba school well" (Ojo Alamo) | Counts, years and distances match; the 10 ft value is at 23.1W.27.233, **19.8 km** away; the 2 San Jose rows are one test | Partly |
| 16 | Smelser well 9 km, 1977, 51 ft, 206 ft, 100 ft²/day | 8.8 km, 1977-05-24, 51, 206, 100 | Yes |
| 17 | 4 flowing visits in Apr–May; 6 no-flow visits Aug–Mar; 6.89–20.4 ft³/s (Rio Puerco) | Same | Yes |
| 18 | Specific conductance 221–342 (5–95%); median 294; pH 7.1–8.6; Sen +0.2, p = 0.74; Sulphur Creek 4,605 / pH 2.2 (Rio Grande) | 221–342; 293.8; 7.1–8.6; +0.23, p = 0.74; mean(5,000, 4,210) = 4,605; 2.2 | Yes |
| 19 | Canals carry water Mar–Nov; peak 86 ft³/s in June; Dec–Feb zero; 2000–2025 (canals) | Same; peak 86.3; but data start **2001**, and winter n = 8–14 years against 21–24 | Mostly |
| 20 | Well A ρ = −0.54, n = 17, p = 0.026; main well ρ = −0.12, p = 0.57 (Bernalillo) | −0.539, 17, p ≈ 0.029; −0.124, p ≈ 0.58; 2007–08 missing but drawn as connected | Yes (numbers) |
| 21 | Cuba-area records from 9 years, 1957–2018 (coverage) | 1957, 1960, 1962, 1971, 1972, 1977, 1978, 1979, 2018 | Yes |
| 22 | Rio Grande at Cochiti about 70 km; Bernalillo about 85 km | 72.5 km; 87–88 km | Yes |
