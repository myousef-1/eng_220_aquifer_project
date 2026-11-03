# Round 2 review: visualization suite

Graded against `analysis/review/RUBRIC.md` by an independent reviewer (round 2).
Code graded: `analysis/charts.py` and the app pages as staged in the clone (charts.py last changed 20:36;
static exports and `figure_text.json` were regenerated afterward and match the code).

## Scores at a glance

| | Score |
|---|---|
| Average chart score (17 charts) | **84.4** / 100 |
| Suite score (G+H+I+J) | **83** / 100 |
| **Overall = 0.7 × 84.4 + 0.3 × 83** | **84.0** |

Round 1 scored 72.0, so this round gained 12.0 points.

### Before reading: two problems with the review harness (not project defects)

1. **The round-2 app screenshots are stale.** All seven files in `scratchpad/round2/app/` are
   byte-identical to `scratchpad/round1/app/` (same md5). They still show the round-1 text, for example
   "Water levels fell at 3 of 4 monitored sites" and "the closest is about 38 km away". The cause is in
   `prep_round.sh`: `shoot.js` writes fresh full-size screenshots to `OUT=$R/app`, and then the resize loop
   reads `png/app_*_light.png` (the old round-1 folder) and saves those files over the fresh ones. *Fix:*
   resize from `$R/app/*.png` in place, or run `shoot.js` with `OUT=$S/png`. Because of this, I graded app
   integration from the page code and `st_helpers.py`. I also built every chart in both themes for every
   selectbox option; all of them build without errors.
2. Maps in `dark/` are drawn on `white-bg` with dark-theme ink, so the town labels are white on white.
   In the app, `st_helpers._build` passes `carto-darkmatter` in dark mode, so this only happens in the
   harness. I did not deduct for it.

## Per-chart scores

| Chart key | A (15) | B (25) | C (15) | D (20) | E (10) | F (10) | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| county_coverage_map | 14 | 22 | 14 | 15 | 8 | 9 | **82** |
| groundwater_hydrographs | 14 | 23 | 14 | 18 | 9 | 10 | **88** |
| groundwater_trends | 14 | 22 | 14 | 18 | 9 | 10 | **87** |
| placitas_remeasured | 13 | 23 | 14 | 16 | 9 | 10 | **85** |
| well_depth_vs_water | 13 | 20 | 13 | 16 | 9 | 10 | **81** |
| depth_by_area | 14 | 19 | 10 | 17 | 8 | 10 | **78** |
| formation_properties__transmissivity_drawdown_ft2_per_day | 12 | 19 | 12 | 16 | 9 | 9 | **77** |
| cuba_area_map | 14 | 23 | 14 | 16 | 9 | 10 | **86** |
| cuba_nearest_records | 14 | 16 | 14 | 18 | 9 | 10 | **81** |
| ojo_alamo_vs_san_jose | 14 | 21 | 13 | 16 | 9 | 10 | **83** |
| rio_puerco_visits | 15 | 22 | 15 | 17 | 10 | 10 | **89** |
| rio_grande_quality | 14 | 22 | 15 | 17 | 9 | 10 | **87** |
| canal_seasonal | 13 | 24 | 15 | 18 | 10 | 9 | **89** |
| bernalillo_river_vs_well | 14 | 23 | 15 | 15 | 9 | 10 | **86** |
| coverage_timeline | 14 | 20 | 14 | 17 | 9 | 10 | **84** |
| evidence_matrix | 14 | 22 | 14 | 16 | 9 | 10 | **85** |
| aquifer_sensitivity_classes | 10 | 24 | 15 | 18 | 9 | 10 | **86** |
| **Average** | | | | | | | **84.4** |

## Per-chart findings

### county_coverage_map (82)
- **Sites outside the county are counted without saying so (B/C).** Three of the 272 "mapped sites" lie
  outside the county outline (2 OSE tests and 1 surface-water site; I checked them point-in-polygon against
  `sandoval_county_boundary.geojson`). They are visible below the southern border near Rio Rancho.
  *Fix:* add a `inside_county` flag and say "including 3 just outside the county line" in the caption, or
  leave them out of the counts.
- **Placitas and Rio Rancho aren't on the map (D),** although other charts lean on them ("Placitas-area
  wells", "Lincoln Middle School (Rio Rancho)"). The "Bernalillo" label also sits under blue dots. *Fix:*
  label Placitas and Rio Rancho with offset annotations, and move Bernalillo's label to the west of its dot.
- **No distance scale on a map whose title is about distance (D).** The static map has no scale bar, and
  about 40% of the frame is empty white space on either side of the county. *Fix:* draw a 25 km scale bar
  (a two-point line with a label), and tighten the zoom or the figure width so the county fills the frame.
- **The subtitle doesn't give the period (E).** Records span 1926–2026. *Fix:* "…colored by what it
  measures, records from 1926–2026".
- **Works well:** every number checks out (272; 96 / 154 / 22; 85.3% east; 18 within 25 km: 17 tests or logs
  and 1 gage). The meridian is drawn and explained, water levels are drawn on top, the source now lists the
  actual files, and the "any record, not active monitoring" caveat is included.

### groundwater_hydrographs (88)
- **Hand-typed counts (I/B).** `f"{n_fall} of 9 monitored wells"`, "the 9 USGS monitoring wells",
  "four sites" and "four points" are literals. *Fix:* use `gw['site_id'].nunique()` and
  `gw['site_group'].nunique()`.
- **The title's site list hides a mixed site (B).** "(Lincoln Middle School, Bernalillo site, Dome Road
  well)" lists the Bernalillo site among falling sites, but its Well A rose (+0.12 ft/yr, p = 0.005). The
  findings disclose this, but the title is what readers repeat. *Fix:* "5 of 9 wells fell (all 3 at Lincoln,
  Bernalillo's main well, Dome Road); 3 rose (Sandia ×2, Bernalillo Well A)", or drop the parenthetical.
- **The hypothesis has no source (C).** "Albuquerque area began relying more on river water" is a factual
  premise (the San Juan–Chama drinking-water project, which came online in late 2008). *Fix:* cite it in
  `references.bib`, and note that the 2007 turn slightly precedes it.
- **Works well:** equal 37-ft y-spans make the slopes comparable, Well A is dashed, lines break at gaps, the
  axis is flipped and labeled, the brief-1 "not how much water is left" caveat is there, and the distances
  (65–95 km) are now computed and correct.

### groundwater_trends (87)
- **One monotonic trend fitted to a V-shaped record (B).** Sandia's full-record "+0.57 ft/yr, rising"
  averages a fall from 1999 to 2007 and a rise from 2007 to 2025. Its actual change from 1999 to 2025 is
  +7.8 ft, not 0.57 × 26 ≈ 15 ft. *Fix:* add to the caption "Sen's slope assumes one direction; at the
  Sandia site the level fell until 2007, then rose (see hydrographs)". Better still, show a 2007–2025 marker
  for that site.
- **Footer placement (D).** In the static export the footer starts at x ≈ 88 px instead of 33 px like the
  other charts, and it sits about 20 px below the x-axis title. *Fix:* in `static()`, anchor the footer to
  `xref="container"` (x=0 with a pad), as the title is, rather than shifting from the paper edge by
  `margin.l`.
- **Works well:** the method, the "both look more certain than they are" caveat, record years beside each
  row, every missing recent marker explained, hollow period keys, clear direction arrows. All numbers
  verified (−0.40 to −0.36; 4 of 7; −0.52; +0.57 and +0.72).

### placitas_remeasured (85)
- **† is unexplained in the static export (D/E).** The slide and docs PNG shows "PC-025†", "PC-002†" and
  "PC-055†", but the † key exists only in the caption, which isn't baked in. *Fix:* add a small in-plot note
  under the axis: "† first-period reading(s) flagged R (recently pumped)".
- **The title is 170 characters and wraps badly (A/D).** The line breaks between "5" and "ft or less", and
  "baseline" sits alone on the third line. *Fix:* shorten it to "Of 5 Placitas wells measured in 1997–98
  and 2018–19, 3 changed ≤5 ft; PC-014 is 51 ft deeper and PC-025 57 ft shallower (unstable baseline)".
- **Hidden range bars (D).** The 1997–98 range bars of PC-014 (2.6 ft) and PC-055 (3.6 ft) are narrower
  than the dot, so readers can't tell "small range" from "no bar". *Fix:* print the range in the right-hand
  label ("range 3 ft"), or give the bar end caps.
- **The subtitle runs to within about 15 px of the right edge (D)** because the wrap width is
  `width/7.4` = 135 characters at 14.5 px. *Fix:* use `width/8.3` in `Chart.static()`; this affects every
  chart.
- **Works well:** n per period on the chart, flagged baselines marked consistently (PC-002, PC-025, and all
  eight PC-055 readings), the T→S/T method change disclosed, the distance correct (90.6–92.5 km), and the
  dumbbell is the right form.

### well_depth_vs_water (81)
- **Pooling inflates the headline correlation (B).** Spearman ρ = 0.73 is computed across three record
  types that the caption says are "not one comparable series". Within each type, ρ is 0.64 (NMBGMR, n = 72),
  0.63 (OSE tests, n = 104) and 0.60 (logs, n = 5). Pooling shallow NMBGMR wells with deep OSE wells adds
  correlation that no single source shows. *Fix:* report "ρ = 0.63–0.64 within each record type" in the
  title, and put the pooled ρ (if any) in the table.
- **The title implies a causal direction (A).** "Deeper wells usually reach water deeper down" reads as if
  drilling deeper finds deeper water; the usual explanation runs the other way. *Fix:* "Where water is
  deeper, wells are drilled deeper (ρ ≈ 0.63 within each source)…".
- **The diagonal label crosses its own line (D).** The text is rotated 31°, but the line is drawn at about
  39° at this aspect ratio, so the line strikes through the middle of the label and past nearby markers.
  *Fix:* compute the angle from the axis pixel ratio, or put the label horizontally at the line's lower
  end, with a small offset.
- **Legend wording (D).** "NMBGMR wells (median reading) (n=72)" has double parentheses, and the legend's
  n = 102 for tests differs from the finding's n = 104. *Fix:* "NMBGMR wells, median reading (n = 72)", and
  "OSE aquifer tests (102 shown, 2 off-chart)".
- **"Cuba area" scope uses another definition (C).** "7 in the Cuba area" comes from the 20 km
  nearest-town grouping; elsewhere "Cuba area" means 25 km. See depth_by_area.
- **Works well:** the impossible RG-54556x row is excluded and named, the caption is now correct ("above
  the diagonal"), per-source medians and n are given, the flowing wells and off-chart wells are disclosed,
  and both shape and color carry the record type.

### depth_by_area (78)
- **"Only 7 wells with a recorded level" is wrong as worded (B).** Under the chart's own grouping, 8 wells
  near Cuba (within 20 km) have a recorded level; the 8th, 20.3W.8.424 at 19.5 km with water at 343 ft, is
  dropped because it has no well depth. Within the project's standard 25 km Cuba area, 10 wells have a
  level, which is what `cuba_area_map` reports. *Fix:* build this chart from all tests with a depth to water
  (well depth isn't needed on this axis), or say "7 wells with both well depth and a level".
- **"Cuba area" means something else here (C/H).** It is the nearest-town group within 20 km, but the
  project defines it as 25 km (`CUBA_RADIUS_KM`). *Fix:* use `CUBA_RADIUS_KM` for the Cuba anchor, or label
  the row "Within 20 km of Cuba".
- **The title states as fact what the finding says may be an artifact (C/B).** "Water is shallowest around
  Cochiti… deepest around Bernalillo-Rio Rancho" compares a mostly NMBGMR 1997–2019 group (shallow
  domestic wells) with a group of 6 deep OSE tests from 1950–1990 plus 1 NMBGMR well (n = 7). *Fix:* "Among
  recorded wells, depth to water was smallest around Cochiti (median 27 ft, n = 15) and largest around
  Bernalillo-Rio Rancho (375 ft, n = 7, mostly old deep test wells)".
- **A well is dropped without saying so (B).** The counts add up to 180, against 181 in the well-depth
  chart; SJ 04455 (unmapped) is silently left out. *Fix:* add "1 well without a valid location is left out"
  to the caption.
- **The scope gives no distances and the subtitle no period (C/E).** *Fix:* add "records 1930–2022" to the
  subtitle.
- **Works well:** aligned dots by area with n in the label, medians only where n ≥ 5, an honest
  "screening grouping, not hydrogeologic regions" caption, and the medians are correct (27 / 51 / 116 / 201
  / 375).

### formation_properties__transmissivity_drawdown_ft2_per_day (77)
- **An unhedged comparison built on 4 wells, one counted twice (B/C).** "The Ojo Alamo median (57.5) is
  below the median of all tests (100)" uses 5 values. Two of them (40 and 222) are two rows for the same
  1957 test at the Cuba school well. Taking one value per well gives a median of about 94, essentially equal
  to 100, and the 5 values straddle 100 (40–222). *Fix:* compute medians per well (the median of each
  well's values, then across wells), and phrase the result as "Ojo Alamo values (4 wells) fall within the
  county spread; too few to say it differs".
- **"Tests" and "values" are mixed (B/H).** The annotation says "median of all 117 tests", but 117 counts
  reported values (rows), as the chart's own "values · wells" labels distinguish. *Fix:* "median of all 117
  reported values".
- **The title is a topic plus two unrelated facts (A).** "Transmissivity (from drawdown): values within
  Madera Limestone span 4+ orders…; the Ojo Alamo median…". *Fix:* lead with one takeaway, for example
  "Transmissivity varies more within formations than between them: Madera values span almost 5 orders of
  magnitude".
- **Weak titles for the other app measures (A/F).** Specific capacity: "Ojo Alamo median (0.55) is below
  the median of all tests (0.6)"; hydraulic conductivity: "medians range from 1.92 to 16" (no units).
  *Fix:* say "about the same as" when the difference is within the IQR or n < 5, and always print the
  units.
- **Small layout issues (D).** The subtitle has double parentheses ("(from drawdown) (ft²/day)") and wraps
  at a hyphen ("Cuba-" / "area"); the single San Jose dot sits on the dotted all-tests line. *Fix:* rename
  the label to "Transmissivity, drawdown method", set `break_on_hyphens=False` in `_wrap`, and give the
  dotted line `layer="below"` with a thinner dash.
- **Works well:** the round-1 false headline is gone, the all-tests median is correct (100 from 117 values;
  94 values with a formation), medians are drawn only with ≥3 wells, the log ticks are clean (0.01 … 10k),
  and the caption is written per measure.

### cuba_area_map (86)
- **The 50 km ring is cut off (D).** The top of the 50 km ring runs off the frame under the legend, and
  the 25 km and 50 km labels sit on the ring lines. *Fix:* zoom to about 8.0 or center at the Cuba latitude
  so all three rings fit; nudge labels outward with `textposition="bottom right"`.
- **Labels collide (D).** "Jemez Springs" crosses the 50 km ring, and the "Cuba" label touches the
  school-well dots. *Fix:* use left/right positions per town, and draw the Cuba marker as a hollow ring under
  the data.
- **Possible double count, disclosed only on another chart (B).** The "16 wells" include 'Cuba Independent
  Rural School Well No 1' and '21.1W.28.143', which the Ojo Alamo caption says may be the same well.
  *Fix:* add "(two records may be the same well)" to the finding.
- **Works well:** every number is correct (16 wells, 1957–1979; 1 log at 21 km in 2018; 10 wells with a
  one-time level; 17.8 ft at 0.71 km; WL-0062 at 38.5 km with 2 readings in 2017). "No well there is
  measured repeatedly" is the right claim now, and the rings work as a scale.

### cuba_nearest_records (81)
- **The second half of the title is factually wrong, and hand-typed (B/I).** "The only closer records are
  one-time well tests (1950s-70s), one well log, and a stream gage." Within 38.5 km of Cuba there are 29
  tested wells from 1948–1987, 3 well logs (21, 29 and 31 km), and 5 surface-water sites: the Rio Puerco gage,
  plus Sulphur Creek at 33.0 km, Redondo Creek at 33.5, Jemez R. below East Fork at 35.1 and Rio Guadalupe at
  Box Canyon at 36.5. The chart itself shows the 33-km surface-water bar. *Fix:* compute the clause, for
  example `f"closer records are one-time tests at {n_t} wells ({_years(...)}), {n_l} well logs, and {n_s}
  surface-water sites"`, or limit it to the 25 km Cuba area, where the current wording is true.
- **The bar label and finding disagree (B/H).** The bar label rounds to "1 km · 1957", while the finding
  and the Cuba map say 0.7 km. *Fix:* use `:.1f` when the distance is under 5 km.
- **Irrelevant source item (E).** The footer cites the county outline, which isn't drawn. *Fix:* use
  `ALL_SOURCES.split("; county")[0]`, as `coverage_timeline` does.
- **Works well:** a clean horizontal bar chart with the 25 km band labeled above the bars, "a short bar only
  means a site is close" (exemplary), and verified values (0.7, 2, 21, 33, 38, 65 km).

### ojo_alamo_vs_san_jose (83)
- **"8 wells" contradicts the caption (B).** The caption says two Ojo Alamo names may be one well. *Fix:*
  "8 test events at 7–8 wells", or count wells by location and depth.
- **Imprecise location of the published values (C).** The caption says "near Lindrith, about 50 km north
  of Cuba". Lindrith is about 33 km NNW of Cuba; the study area (T23–25N, R2–4W) lies about 30–60 km away.
  Table 1 also doesn't place Stone et al.'s (1983) two tests near Lindrith; that report covers the whole
  basin. *Fix:* "Blandford et al. study area west of Lindrith, about 35–55 km north of Cuba", and label the
  Stone et al. range "San Juan Basin (Stone et al. 1983)".
- **Overlapping dots (D).** In the depth panel the three shallow Ojo Alamo values (10, 18 and 24 ft) overlap
  at the left of a 0–600 ft axis. The first two panel titles nearly touch. *Fix:* use a log depth axis or
  label the shallow cluster; shorten the panel title to "Depth to water (ft)".
- **Hard-coded current year (I).** The caption computes `2026 - year`, so it goes wrong in 2027. *Fix:*
  `date.today().year`.
- **Works well:** an honest title ("too few to describe either formation"), test events counted correctly
  (7 + 1), dataset 6 used for real (9.4 and 4–11 m²/d converted correctly to 101 and 43–118 ft²/day,
  checked against Table 1), and n per panel.

### rio_puerco_visits (89)
- **The month panel hides two visits (B/D).** The three October no-flow visits (2019, 2020 and 2024) plot
  as one marker, so the panel shows 4 hollow circles for 6 visits. *Fix:* stack repeated months vertically
  (y = 0, −1, −2 ft³/s offsets inside the −4 band), or label "×3".
- **Two markers overlap (D).** The Aug 2020 and Oct 2020 circles overlap in the date panel. *Fix:* reduce
  the hollow marker size to 11, or widen the figure.
- **Works well:** this follows brief 4 exactly: dots only, no measurable flow marked with hollow circles,
  "not a continuous record", a seasonal panel added, a hedged hypothesis, and all numbers correct (4 flowing
  visits in Apr–May at 6.89–20.4 ft³/s; 6 no-flow visits from Aug to Mar; gage 2.3 km away).

### rio_grande_quality (87)
- **The period in the title belongs to one parameter only (B).** "(2003-2026)" is the specific-conductance
  record; the pH record covers 2004–2025. *Fix:* "conductance 2003–2026, pH 2004–2025", or use the
  overlapping years.
- **"Stays fresh" has no reference on the chart (D/A).** The guideline (about 700–900 µS/cm) is only in the
  caption, and the axis tops out at 375, so the static figure doesn't show what "fresh" means. *Fix:* add a
  right-edge note "drinking-water taste guideline ≈ 700–900 µS/cm (off scale)", or a dashed line with the
  axis extended.
- **Inconsistent tick format (D).** pH ticks read "7.5, 8, 8.5". *Fix:* `tickformat=".1f"`.
- **Works well:** isolated months are now visible, the DO and turbidity panels moved to the table, the
  5–95% ranges are consistent, the geothermal explanation is now a Hypothesis, the guideline is cited, and
  all numbers are correct (221–342; 7.8–8.3; median 294; +0.2 per year, p = 0.74; Sulphur Creek
  4,210–5,000 µS/cm, pH 2.2–2.3).

### canal_seasonal (89)
- **The subtitle touches the right edge (D).** "…years with" ends 3 px from the edge of the 1,400-px image,
  and "data" wraps alone onto the next line. A font fallback would clip it. *Fix:* use a narrower wrap
  width in `static()` (see placitas).
- **The hover shows "month 6" (F).** *Fix:* pass the month name in `customdata`.
- **The tie to research question 6 is indirect (A).** The caption is honest about it; a one-line note that
  the Cochiti canals serve Pueblo and acequia-type irrigation, if documented, would strengthen it.
- **Works well:** the start year is now computed (2001), n is shown under each month, the winter caveat is
  quantified (8–14 vs 24 years), there are separate panels instead of overlapping labels, and the numbers
  are correct (86.3 ft³/s in June).

### bernalillo_river_vs_well (86)
- **Missing ticks (D).** The main-well depth panel shows only "40" and "50", while values reach about
  57 ft, so the bottom third of the panel is unlabeled. *Fix:* `dtick=5` on rows 2 and 3, column 1.
- **Separate y-scales aren't stated (D).** Main well spans about 17 ft, Well A about 3.5 ft, and the two
  scatter y-ranges differ fourfold. The rubric asks for panels with separate scales to say so. *Fix:* add
  "y-scales differ between panels" to the caption, or print the span in each panel title.
- **The rounding reads as borderline significance (B).** The Bonferroni p is 2 × 0.027 = 0.054, printed
  as "0.05". *Fix:* `:.3f`.
- **Layout (D).** The top-right cell is empty, and the title wraps mid-expression ("(ρ = / +0.54"). *Fix:*
  put the ρ summary or a reading guide in the empty cell, and use a non-breaking space in "ρ = +0.54".
- **Works well:** the chart now shows its own finding (Δ-vs-Δ scatters with ρ, n and p), lines break at the
  2007–08 gap, the title is hedged, "shallower" is gone, the statistics are in the table, and the numbers
  are correct (ρ = +0.54, n = 17, permutation p = 0.027; +0.12, p = 0.58; gage 41 km away).

### coverage_timeline (84)
- **"4 sites" against a legend that counts wells (B/H).** The title says levels are recorded "at 4 sites",
  but the heatmap counts `site_id` (9 wells), so the USGS row is colored "5-9 sites". *Fix:* count
  locations (`site_group`) for the USGS row, or call the legend "wells/sites with records".
- **"Every year only since 1998" is slightly off (B).** 1998 has only the 3 Lincoln wells (one site); all 4
  sites start in 1999. "4" is hand-typed. *Fix:* compute the first year with all sites reporting.
- **Color meaning (D/H).** The count ramp reuses the water-level blue for every data type, including
  streamflow and tests. *Fix:* use a neutral gray ramp for counts, so blue keeps meaning "water level".
- **The title is three lines long (D).** *Fix:* trim to "Groundwater levels are monitored yearly only since
  1999, at 4 eastern sites; the Cuba area has no water-level monitoring or water-quality records".
- **Works well:** the county and Cuba-area blocks are explicit, the hover names the row, "no records" is
  written into empty rows, and the NMBGMR periods (1997–1999 and 2016–2019) and the 9 Cuba-area years are
  correct.

### evidence_matrix (85)
- **‡ is unexplained in the static export (D/E).** The footer defines † but not ‡. *Fix:* append
  "‡ image-only map plate, not yet digitized" to the source line, or put both keys under the legend.
- **Low contrast in dark mode (D).** "Limited" (#184f95) and "Moderate" (#256abf) are hard to tell apart
  on #0e1117. *Fix:* widen the dark ramp steps, or add a symbol or pattern for Strong.
- **Edge spacing (D).** The rotated "OSE aquifer tests†" header ends about 10 px from the right edge.
  *Fix:* `margin.r=60`.
- **Works well:** the color legend and its word-to-color mapping, honest † and ‡ notes, both findings
  correctly labeled *Insufficient data*, and ratings that match the briefs.

### aquifer_sensitivity_classes (86)
- **Low analytical value (A).** Counts of polygons answer no research question; the caption itself says a
  tiny "High" and a large "Less" polygon count the same. `Shape__Area` gives unitless *relative* shares
  without needing units (all rows share one CRS, apparently degrees²). *Fix:* add a second bar for "share of
  listed area", with the caveat "in map units; shares only".
- **The research-question link is thin (A).** Brief 3 says "Q9 only if validated". *Fix:* tie it to RQ 8 as
  a documented gap, and keep it last on the page.
- **Works well:** honest about the missing geometry, follows the brief-3 "do not map from CSV alone"
  caveat, correct counts (613 = 152 / 339 / 122), and clean design.

## Suite scores

### G. Coverage of questions and planned outputs: 25 / 30
- **Present:** the county map, a Cuba-area map and nearest-record view, time series (hydrographs, trends,
  Placitas), comparisons by area (`depth_by_area`) and by aquifer unit (`formation_properties`,
  `ojo_alamo_vs_san_jose`), and coverage views (timeline and evidence matrix). Dataset 3 now appears, and
  dataset 6's published values are used. Gaps for research questions 3, 5 and 6 are shown honestly (Cuba
  info box, page warnings, Insufficient-data findings). `docs/findings.md` now has a real bottom line and a
  per-question table.
- **Still missing: any geologic or aquifer-unit view of the Cuba area (−3).** The proposal promised a
  geologic-region layer and an Ojo Alamo / San Jose extent view. Brief 5 asks to "extract/attribute aquifer
  depth, thickness and well-location maps"; brief 6 suggests the Cuba Mesa thickness and head maps. Neither
  is shown, not even as an attributed figure. *Fix:* add one annotated figure: a crop of the HA-720-B plate
  or the Blandford et al. Fig. 8 head map, with Cuba marked and the source credited.
- **The RQ9 indicator table has a wrong value (−1).** "Water-level change, full record: −13 to +15 ft since
  1999" multiplies the Sen slope by the span. The measured first-to-last annual-mean change is −16.0 to
  +7.8 ft (Sandia +7.8, not +15). *Fix:* report measured changes (first vs last annual mean per well), or
  rename the row to "trend × years".
- Water quality by area exists only for rivers (disclosed). Acequias are represented only by context
  (disclosed) (−1).

### H. Consistency across charts: 16 / 20
- **Good:** color meanings are now reserved and documented (data types, well shades, formation
  ochre/violet, trend red/blue/gray). Finding labels and caption structure are the same everywhere,
  "repeated water-level record" is used consistently, and the distances agree (38, 65–95 and 90 km).
- **"Cuba area" has two definitions (−1.5).** It means 25 km everywhere except `depth_by_area` and the
  well-depth scope (nearest town within 20 km), which produces "7 wells with a recorded level" in one chart
  against "10 wells" in the Cuba map.
- **"Site" means a well in one place and a location in another (−1).** The coverage title's "4 sites"
  sits next to a legend counting 9 wells. "Tests" and "values" are used interchangeably in the formation
  chart.
- **Small mismatches (−1).** "1 km" vs "0.7 km"; footer x-offsets differ between charts (33 px vs 83–88 px);
  blue is used for water level, rising trend and counts (documented, but three meanings for one hue);
  orange "aquifer tests" and ochre "Ojo Alamo" are close hues for related data.
- **Ad hoc scope strings (−0.5):** "Cuba and surroundings (within 60 km)", "Cuba and the nearest site in
  each dataset" and "Unknown extent". They are clear, but not the constants.

### I. Reproducibility and code quality: 25 / 30
- **Good:** everything a fresh clone needs is staged (`analysis/`, the GeoJSON, figures, docs), and nothing
  is left unstaged or untracked. `requirements.txt` has version floors that match the APIs used
  (`go.Scattermap`, `st.context.theme`, `width="stretch"`). Paths come from `__file__`, and raw data are
  untouched (`git diff --cached -- data` shows only the new GeoJSON). The promised "Data preparation inside
  the analysis code" section exists, dead code and stale references are gone, and the round-1 latent
  formation bugs are fixed. The code is well documented, and every chart builds in both themes for every
  selectbox option in about 6 s total.
- **About 10 hand-typed facts remain in titles, captions or scopes (−3), and one is wrong:**
  `cuba_nearest_records` ("(1950s-70s), one well log, and a stream gage"). The others: "of 9 monitored
  wells", "the 9 USGS monitoring wells", "four sites", "four points" (hydrographs, trends); "at 4 sites"
  (coverage); "and one stream gage" (Cuba map); "about 50 km north of Cuba" and `2026 -` (Ojo Alamo); "about
  every two months" (Placitas); "Questions 3, 5, and 6" (evidence findings). This breaks the module's own
  rule ("Numbers in titles, captions, and findings are computed from the data").
- **Small documentation drift (−1).** The Data sources page lists the aquifer tests as
  `ose_aquifer_test_wells.csv`, but the charts read `data/clean/aquifer_tests.csv`. `docs/analysis.md`
  links to a "score history" that doesn't exist yet (`analysis/review/score_history.md`).
- **Untested floor (−1).** `pandas>=2.0` is declared, but the code was only run on pandas 3.0.5. *Fix:*
  test once on pandas 2.2, or set the floor to what was tested. No unit tests cover `stats.py` (an MK/Sen
  test against known values would take 10 lines).

### J. Integration: 17 / 20
- **Good:** every chart is on its matching page, with takeaway, subtitle, scope, caption, labeled findings,
  table and CSV download (`show_chart`). The page intros now describe what is actually shown (County map,
  Water quality). Static exports exist for all 17 charts (PDF without text for LaTeX, PNG with text for
  slides and docs), along with `figure_index.csv` and `analysis_figures.tex`. `docs/analysis.md` embeds
  every figure from generated blocks, and `report.tex` includes figures 1 and 2 (the PDF is picked up first
  by `\graphicspath`).
- **The static exports drop keys that live only in the caption (−1):** † in Placitas, ‡ in the evidence
  matrix, and the "stays fresh" guideline reference. Subtitles wrap to the right edge (canal, Placitas).
- **The generated LaTeX captions are missing a period (−0.5).** In `analysis_figures.tex` the subtitle and
  "Scope:" run together ("outline = Sandoval County Scope: …"), and the method caption isn't included.
  *Fix:* `rstrip('.') + '.'` on the subtitle, and add `c.caption`.
- **The report draft isn't merged (−1).** `analysis_draft.tex` holds the Results text, but `report.tex`'s
  Results sections are still "[RQ1 (Fig. 2).]" placeholders. One sentence in the draft states a hypothesis
  as fact: "a 1990s baseline that was still recovering from pumping".
- **The app couldn't be verified visually this round (−0.5)** because of the harness bug above. Re-shoot
  the screenshots after fixing `prep_round.sh`.

**Suite score = 25 + 16 + 25 + 17 = 83.**

## Overall

- Average chart score: **84.4** (sum 1,434 / 17)
- Suite score: **83**
- **Overall = 0.7 × 84.4 + 0.3 × 83 = 84.0**

## Top 10 fixes (ordered by expected overall gain)

1. **Compute every remaining hand-typed fact, starting with the wrong `cuba_nearest_records` clause**
   (29 tested wells from 1948–1987, 3 logs and 5 surface-water sites are closer than 38 km), then "9 wells",
   "4 sites", "four points", "one stream gage", "about 50 km" and `2026 -`. (I +2, chart B +6: about +0.85)
2. **Add one geologic or aquifer-unit context figure for Cuba:** an attributed crop of the HA-720-B Ojo
   Alamo plate or the Blandford et al. head or thickness map, with Cuba and the 25 km ring marked. (G +2–3:
   about +0.6 to +0.9)
3. **Use one "Cuba area" everywhere:** have `depth_by_area` use the 25 km `CUBA_RADIUS_KM` for Cuba and
   count wells with any recorded level (10, not 7); fix the "7 in the Cuba area" scope in the well-depth
   chart; hedge the shallowest/deepest-area title. (H +1.5, chart +6: about +0.7)
4. **Finish the static exports:** in-figure † and ‡ keys and a guideline note for Rio Grande; a narrower
   subtitle wrap (`width/8.3`) and `break_on_hyphens=False`; one footer anchor; periods in the
   `analysis_figures.tex` captions; merge `analysis_draft.tex` into `report.tex`'s Results. (J +1.5, D +1 on
   about 5 charts: about +0.65)
5. **Make "site" mean one thing:** count locations (or relabel the legend "wells") in `coverage_timeline`,
   compute "since 1999 at all 4 sites", and use "values", not "tests", in the formation chart. Disclose the 3
   county-map sites outside the outline. (H +1, charts +4: about +0.45)
6. **Fix the RQ9 indicator table and the Sandia trend note:** use measured first-to-last changes (−16.0 to
   +7.8 ft), and add a caption note that Sandia's full-record slope averages a fall and a rise. (G +1,
   trends +2: about +0.4)
7. **Formation chart:** use per-well medians (Ojo Alamo ≈ 94 vs 100), replace "is below" with a hedged
   statement for n < 5 or differences within the IQR, give a single-takeaway title, fix the subtitle
   punctuation, and require units and a meaningful difference in the other measures' auto-titles. (about
   +0.25)
8. **Well depth vs water:** headline the within-source ρ (0.63–0.64), reword away from the causal phrasing,
   fix the diagonal label's angle and position, clean up the legend. (about +0.2)
9. **Bernalillo:** `dtick=5` on the depth panels, "y-scales differ" in the caption, Bonferroni p to 3
   decimals, use the empty top-right cell. (about +0.16)
10. **Map and marker polish:** fit the full 50 km ring and offset the ring and town labels (Cuba map);
    label Placitas and Rio Rancho and add a 25 km scale bar (county map); stack the three October visits
    in the Rio Puerco month panel. (about +0.2)

Also needed before round 3, though it doesn't change the score: fix `prep_round.sh` so the app
screenshots are fresh, and add `analysis/review/score_history.md`.

## Numeric spot-checks

All checks were recomputed with my own code from the CSVs: haversine distances, pyproj (EPSG:26913 →
4269) for UTM, my own Sen's slope, Mann-Kendall with SciPy's normal CDF, `scipy.stats.spearmanr`, and my
own permutation test. I did not use the project's loaders. Scripts:
`/tmp/claude-0/-home-claude/cb544c04-d0fc-5e58-9d80-1aab23dbcf8f/scratchpad/grader2/v1.py` to `v4.py`.

| # | Claim (chart) | Recomputed | Match |
|---|---|---|---|
| 1 | 272 sites; 96 / 154 / 22; 85% east of 106.75° W; 18 within 25 km, none monitoring (county map) | 272; 96 / 154 / 22; 85.3%; 18 (17 tests or logs, 1 gage); also 3 sites lie outside the county outline | Yes (3 outside undisclosed) |
| 2 | 5 of 9 wells falling, 3 rising, 1 no trend; Sandia +13 ft since 2007; 65–95 km; equal 37 ft span (hydrographs) | 5 / 3 / 1; 2007 annual mean 492.05 → 2025 478.84 = 13.2 ft; 65.2–95.2 km; max range 34.7 × 1.08 = 37.5 | Yes |
| 3 | 2016–25: 4 of 7 falling, only Sandia rose; Lincoln −0.40 to −0.36; Bernalillo −0.52; Sandia +0.57 / +0.72 (trends) | 4 of 7; Sandia Well and Well A rising; −0.403 to −0.360; −0.522; +0.572 / +0.722 | Yes |
| 4 | 5 wells in both 1997–1998 and 2018–2019; 3 within 5 ft; PC-014 +51; PC-025 −57; 80 ft early rise; 82 of 87; T vs S/T; about 90 km (Placitas) | 5; 3; +50.9; −57.2; 138.9 → 58.6 = 80.4; 82 of 87; T / S,T; 90.6–92.5 km | Yes |
| 5 | Spearman ρ = 0.73; 181 wells; IQR 41–240; medians 53 / 165 / 240; water column 142; 2 flowing (well depth) | 0.730; 181; 41.2–240.0; 52.8 / 164.7 / 240; 141.8; 2. **Within-type ρ only 0.64 / 0.63 / 0.60** | Numbers yes; headline ρ inflated by pooling |
| 6 | Area medians 27 / 51 / 116 / 201 / 375; "Cuba area has only 7 wells with a recorded level, 10–446 ft, 1957–1978" (depth by area) | 27 / 51 / 116 / 201 / 375; 7 wells with depth **and** level, 10–445.5 ft, 1957–1978; but **8 wells within 20 km and 10 within 25 km have a level** | Partly |
| 7 | Median of all 117 = 100; Ojo Alamo 57.5 from 5 values at 4 wells; Alluvium 2,760; Point Lookout 6.2; Madera 4+ orders (formation) | 100.0 (94 with a formation: 73.5); OA 40 / 57 / 57.5 / 164 / 222, 4 wells; 2,759.5; 6.2; 4.79 orders; **per-well OA median ≈ 94** | Yes (comparison fragile) |
| 8 | 16 wells with tests 1957–1979, 1 log, 1 gage within 25 km; 10 wells with a level, 1957–1978; 18 ft at 0.7 km; WL-0062 38 km, 2 readings in 2017 (Cuba map) | 16; 1957–1979; SJ 04288 at 21.1 km; 10; 1957–1978; 17.8 ft at 0.71 km; 38.5 km, 2 readings | Yes |
| 9 | "Only closer records are one-time tests (1950s–70s), one well log, and a stream gage" (nearest records) | Within 38.5 km: 29 tested wells, **1948–1987**; **3** well logs; **5** surface-water sites | **No** |
| 10 | 8 test events at 8 wells (7 OA, 1 SJ), 1953–1977, 1–45 km; OA 18–24 ft within 5 km, 10–604 ft at 19–45 km; Smelser 9 km, 51 / 206 / 100; published 43–118 ft²/day (Ojo Alamo) | 7 + 1 events; 7 + 1 well keys; 1953–1977; 0.7–44.9 km; 17.8 / 24; 10–604 at 19.5–44.9 km; 8.8 km, 51 / 206 / 100; Table 1: 9.4 and 4–11 m²/d → 101 and 43–118 | Yes |
| 11 | Flow on all 4 visits in Apr–May, none of 6 from Aug to Mar; 6.89–20.4 ft³/s; gage 2 km (Rio Puerco) | Flowing: Apr 2019, May 2020, Apr 2021, Apr 2024 (6.89–20.4); dry: Oct, Aug, Oct, Oct, Dec, Mar; 2.26 km | Yes |
| 12 | SC 221–342 (90% of months), pH 7.8–8.3, 2003–2026; median 294; +0.2 per year, p = 0.74; Sulphur Creek 4,210–5,000, pH 2.2–2.3; 73 km (Rio Grande) | 221.1–342.1; 7.79–8.34; SC 2003–2026 but **pH 2004–2025**; 293.8; +0.225, p = 0.735; 4,210–5,000, 2.24–2.32; 72.5 km | Yes (period applies to SC only) |
| 13 | Canals Mar–Nov, zero Dec–Feb, peak 86 ft³/s in Jun, 2001–2025, winter n 8–14 vs 24 (canals) | Same; peak 86.3 (Cochiti East Side, June) | Yes |
| 14 | Well A ρ = +0.54, n = 17, p = 0.027; main ρ = +0.12, p = 0.57; depths 31 / 52 ft; gage 41 km; 87 km (Bernalillo) | 0.539, 17, permutation p 0.027 (t-test 0.026); 0.124, p 0.58; 31.1 / 52.3; 40.8; 87.2; 2007–08 missing | Yes |
| 15 | Levels every year since 1998 at 4 sites; NMBGMR 1997–1999 and 2016–2019; no Cuba-area WQ (coverage) | 1998: only Lincoln (3 wells, 1 site); all 4 sites from 1999; NMBGMR years match; 0 WQ rows within 25 km | Mostly |
| 16 | 613 polygons: 152 / 339 / 122 (sensitivity) | 613; High 152, Mod 339, Less 122; columns OBJECTID, SENSITIVITY, Shape__Area, Shape__Length only | Yes |
| 17 | Indicator table: "−13 to +15 ft since 1999" (Data sources page, RQ9) | Measured first-to-last annual mean change −16.0 to +7.8 ft (Sandia +7.8) | **No** |
