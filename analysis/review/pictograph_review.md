# Pictograph review: six pictograph charts plus the full suite

Independent review against `analysis/review/RUBRIC.md` (criteria A-F per chart, G-J for the suite), plus
a pictograph check (P1-P4, 0-10 each) for the six charts in `charts.PICTOGRAPH_CHARTS`. Materials:
the 18 static exports, the 6 plain and 6 dark renders, the 7 app screenshots, `figure_text.json`, and the
code. I recomputed numbers from the CSVs with my own scripts (pandas, pyproj, haversine), not the
project's loaders, except where I was checking the chart's own output (pictogram displacement).

Environment allowances applied: blank interactive maps in the app screenshots, the white background on
the dark static map, and the uncommitted state were not penalized. `docs/figures/*.png` and
`report/figures/*.png` are pixel-identical to the review renders, so the exports are current.

## Summary

| | Score |
|---|---|
| Average chart score (18 charts) | **84.8** / 100 (1,527 / 18) |
| Suite score (G 27 + H 15 + I 25 + J 17) | **84** / 100 |
| **Overall = 0.7 × 84.83 + 0.3 × 84** | **84.6** |
| Average pictograph check (6 charts) | **28.8 / 40** (173 / 240) |

In one sentence: the Harvey balls, the waffle, and the Rio Puerco drops are real improvements that look
scientific, but the Cuba-area pictograph map gives up positional accuracy on a chart whose whole message
is distance. It moves 22 of 55 symbols, and 3 of them cross a distance ring. Its symbols are 4-7 km across
on the ground, and it breaks the project's "orange = aquifer tests" color rule on the same page as the
next chart. That map, plus a dark-theme contrast problem in the Placitas cross-sections, is why the
pictograph round scores slightly below rounds 3 and 4 (86.3 / 86.0).

## Per-chart scores

P = pictograph version (what the app, docs, and slides show; the report uses the plain version).

| Chart key | P? | A (15) | B (25) | C (15) | D (20) | E (10) | F (10) | Total |
|---|:-:|---:|---:|---:|---:|---:|---:|---:|
| county_coverage_map | | 13 | 23 | 13 | 15 | 9 | 9 | **82** |
| groundwater_hydrographs | | 14 | 24 | 15 | 17 | 9 | 10 | **89** |
| groundwater_trends | | 14 | 23 | 15 | 18 | 9 | 10 | **89** |
| placitas_remeasured | **P** | 12 | 21 | 14 | 15 | 9 | 8 | **79** |
| well_depth_vs_water | | 12 | 22 | 14 | 15 | 9 | 10 | **82** |
| depth_by_area | | 13 | 22 | 14 | 17 | 9 | 10 | **85** |
| formation_properties__transmissivity_drawdown_ft2_per_day | | 11 | 21 | 14 | 17 | 9 | 9 | **81** |
| cuba_area_map | **P** | 12 | 17 | 13 | 11 | 9 | 9 | **71** |
| cuba_nearest_records | **P** | 14 | 24 | 14 | 18 | 9 | 10 | **89** |
| ojo_alamo_depth_map | | 14 | 23 | 14 | 17 | 10 | 8 | **86** |
| ojo_alamo_vs_san_jose | | 13 | 23 | 15 | 16 | 9 | 10 | **86** |
| rio_puerco_visits | **P** | 15 | 23 | 15 | 17 | 10 | 9 | **89** |
| rio_grande_quality | | 14 | 24 | 15 | 16 | 9 | 10 | **88** |
| canal_seasonal | | 13 | 24 | 15 | 18 | 10 | 10 | **90** |
| bernalillo_river_vs_well | | 14 | 22 | 14 | 16 | 9 | 10 | **85** |
| coverage_timeline | | 14 | 24 | 14 | 18 | 9 | 10 | **89** |
| evidence_matrix | **P** | 13 | 20 | 13 | 18 | 9 | 10 | **83** |
| aquifer_sensitivity_classes | **P** | 12 | 22 | 12 | 18 | 10 | 10 | **84** |
| **Average** | | | | | | | | **84.8** |

Pictograph rows average 82.5 (495 / 6); plain rows average 86.0 (1,032 / 12).

---

## Pictograph checks

### 1. cuba_area_map: P1 4 · P2 6 · P3 4 · P4 4 = **18 / 40**

**P1 Integrity (4/10).**
- **Displaced symbols cross the distance rings.** The relaxation (`_relax`) moves 22 of 55 symbols off
  their own footprint (the caption says so). The median shift is 2.0 km and the largest is **8.2 km**: ER 4,
  really 12.2 km from Cuba, is drawn at 20.1 km. Three symbols land on the wrong side of a ring.
  SH-4 and Geothermal Hole GT-2 are 29.8 km away but drawn at 23.8 and 23.3 km, *inside* the 25-km
  "Cuba area" ring. Prod Well No 3 (11.7 km) is drawn at 6.5 km, inside the 10-km ring. A reader
  counting symbols inside the 25-km ring gets 19 sites, but the title says 17 (15 + 1 + 1). That is the
  worst failure a distance map can have.
  *Fix:* collapse co-located wells into one symbol with a count ("×5 Prod Wells, 1971", "×8 at the
  SH/WW site"). Where you still nudge, cap the shift at about 1 km and forbid crossing any ring the site
  isn't inside.
- **The symbols are sized in kilometres on the ground** (3.8-7.4 km across, so each covers 11-43 km²).
  The 10-km ring is only 20 km across, so the five Prod Wells and ER 4 (true positions within about 1 km
  of each other) fill most of the 10-25 km band south of Cuba. *Fix:* use fixed-pixel symbols (about
  20 px), or at least halve the km sizes.
- **Size encodes a variable the title and findings never mention.** The title and findings are about
  record type and repeated measurement. Transmissivity has no finding, yet the largest, most
  prominent marks on the Cuba page are five 1971 production wells with no recorded formation
  (733-5,508 ft²/day). They suggest "productive aquifer next to Cuba" with no finding or hedge. The docs
  call this the "how good is the well" map, which is a different question from its title.
  *Fix:* drop size on this map and leave transmissivity to the hover, the table, and `formation_properties`.
  If you keep it, add a Measured finding with those numbers and their age.
- **The size classes are hard to tell apart and their labels overlap.** Adjacent diameters differ by only
  1.23-1.26×. "Not recorded" (hollow) is the same size as "under 10". The key labels "10-100" and
  "100-1,000" share the value 100, and the only San Jose well (Smelser, exactly 100 ft²/day) sits on that
  boundary (the code puts it in 100-1,000). *Fix:* use 3 classes with at least 1.5× diameter steps, labeled
  "<10", "10 to <100", "≥100" (or similar).
- **The color meaning changes.** Everywhere else, including the next chart on the Cuba page (an orange
  OSE aquifer-test badge), orange = well construction and aquifer tests. On this map, aquifer tests are
  gray, ochre, or violet, and only well logs are orange. That makes six colored categories, against the
  theme's own three-color rule. Under simulated deuteranopia, Ojo Alamo ochre vs well-log orange is
  ΔE ≈ 10 and San Jose violet vs water-level blue is ΔE ≈ 12, so the glyphs have to carry the difference,
  and they are about 10 px. *Fix:* keep orange for every well record and show formation as a colored ring
  or inner dot (ochre / violet / none).

**P2 Tone (6/10).** The cone-of-depression glyph is a nice hydrologic touch. But white-glyph badges on
discs read like a points-of-interest or transit map, and the leader-line "asterisks" over the gray clusters
look like scratches. It is the least "scientific figure"-like chart in the suite, and the one most out of
place next to the plain county map.

**P3 Legibility (4/10).**
- The leader lines are Scattermap traces, so they draw *on top of* the image-layer symbols and cross
  neighboring symbols (visible star shapes about 12 km S and about 30 km SE). *Fix:* draw them as a map
  line layer under the symbols, or drop them once co-located wells are merged.
- The "Cuba" label is overlapped by two hollow symbols, and the Cuba dot is half covered. "Jemez Springs"
  sits under a large gray symbol, and "San Ysidro" touches a hollow one. *Fix:* draw the town marker as a
  ring above the symbols, and place labels with a halo in clear space.
- White glyph on the "context" gray badge: contrast 2.0:1. The glyphs (about 10 px on the slide, 3-4 px
  at report width) are unreadable at 7 in.
- The hover targets are sized in pixels for the starting zoom, but the symbols scale with zoom. After
  zooming in, only the centers respond to hover; after zooming out, targets overlap their neighbors.

**P4 Value (4/10).** Showing formation and separating tests from logs is useful; round 4 asked for
formation colors. But the plain map could carry both (formation color plus a distinct marker for logs)
without moving anything. The plain county map was kept plain for "pictograms would hide each other",
and the same reasoning applies here. **Recommendation:** make the plain map, with formation colors
added, the default everywhere, or rebuild the pictograph with the fixes above.

### 2. cuba_nearest_records: P1 8 · P2 8 · P3 8 · P4 7 = **31 / 40**

- **P1 (8).** Each badge is centered on the true distance, stems start at 0, and exact labels sit beside each
  badge. All six distances check out. The badge is about 4 km wide on the axis, so the 0.7 and 2.3 km
  badges spill below zero (the axis starts at -3) and hide their stems; the labels keep it honest.
  *Fix:* draw a zero line, or shrink the badges to about 0.6 row height.
- **P2 (8).** A lollipop with badges is a clean, accepted form. It is a little app-icon-like, but restrained.
- **P3 (8).** Readable in both themes. The legend shows plain colored dots, not the four glyphs, so glyph
  meaning lives only in the caption. *Fix:* show the four badges in the legend, or drop the legend (the
  rows are already labeled).
- **P4 (7).** The glyph repeats information already in the row label and color. Harmless, with little gain
  over the bars.

### 3. placitas_remeasured: P1 6 · P2 9 · P3 6 · P4 6 = **27 / 40**

- **P1 (6).**
  - All depths and levels verify: 220 / 580 / 165 / 300 / 420 ft, and the changes match. Casing to the
    bottom agrees with `CasingDepth` for 4 of 5 wells (PC-014 has no casing depth).
  - (a) The biggest visual mass is the blue "water in the well" column (well depth minus the 2018-19
    level). That is not the title's quantity, and it reads like a bar of "how much water each well has":
    PC-019 looks best supplied. The caption disclaims this, but the mark still dominates.
  - (b) The ▽ markers are *centered* on the level. The hydrogeologic convention the chart cites puts the
    apex on the water line, so each symbol hangs about 6 ft below the level it marks.
  - (c) The 0-600 ft axis is set by the deepest well, so the 1997-98 ranges of 3-4 ft (PC-019, PC-055,
    PC-014) shrink to 1-4 px dashes floating beside the wells, and PC-002's hollow ▽ is hidden behind the
    filled one. The "range vs change" check the caption promises can't be seen for 3 of 5 wells.
  - (d) The legend swatch for the range is a horizontal bar, but on the chart it's a vertical bar.
  - *Fix:* lighten or outline the water column and call it "water column above the well bottom". Anchor
    the ▽ apex on the level. Print "1997-98 range 3 ft" under each change label, as the plain version does.
    Use a vertical legend glyph. Optionally stop the axis about 1.5× above the deepest water level and mark
    the well bottoms with "▼ 580 ft".
- **P2 (9).** Well cross-sections are a familiar scientific idiom, and this is the most "engineering
  drawing"-like chart in the set. Good tone.
- **P3 (6).** Contrast of the 1997-98 hollow ▽ against the water column is **1.42:1 in light and 1.18:1 in
  dark**, and 2.3:1 against the dark background. So PC-025's baseline marker, the visual evidence for
  "unstable baseline", is nearly invisible in dark mode. The light and dark themes also swap which blue
  means "older". *Fix:* give the old-period ▽ an ink-colored outline (or a white halo in light / dark halo
  in dark) so it is at least 3:1 everywhere, and keep "older = hollow" as the only cue.
- **P4 (6).** Comparing each level with its well depth is real added context (stress, RQ9). But the change,
  which is the title's message, is harder to read than in the dumbbell. Keep it with the fixes, or show the
  dumbbell with small cross-sections beside it.

### 4. rio_puerco_visits: P1 8 · P2 7 · P3 8 · P4 8 = **31 / 40**

- **P1 (8).** One equal-sized drop = one visit. The drop's round body is anchored on the measured value
  (`y = value + 0.62h`, `yanchor="top"`), and I confirmed it on the render: Apr 2019 body center ≈ 19.5 vs
  19.4. The month counts verify (Mar 1 dry, Apr 3 flowing, May 1 flowing, Aug 1, Oct 3, Dec 1 dry).
  - The tip extends 0.6 drop-heights above the value, so a reader who reads the top of a mark (as with
    bars) overestimates.
  - The anchor only holds while the 200-day box is wider than the drop is tall. In a narrow column or on
    a phone, `sizing="contain"` shrinks the drop and re-centers it, which moves the body off the value.
  - *Fix:* compute `sizex` from the plot width (or use about 400 days) so the height always fills `h`.
- **P2 (7).** The teardrop is the most clip-art-like glyph in the set, but it is flat, one color, and equal
  size on real axes, and filled vs hollow for flow vs no flow is apt.
- **P3 (8).** Clear in both themes. The Aug/Oct 2020 and Dec 2025/Mar 2026 drops touch, which the
  month labels placed above and below offset. The left x axis runs empty to Dec 2026.
  *Fix:* end the axis about 3 months after the last visit.
- **P4 (8).** The month panel as a unit chart (1 drop = 1 visit) makes "spring only" countable at a glance.
  It is better than the plain right panel. Keep.

### 5. evidence_matrix: P1 8 · P2 9 · P3 8 · P4 9 = **34 / 40**

- **P1 (8).** The Harvey fill (0, ⅓, ⅔, full) suggests ratios ("Moderate = twice Limited") that an ordinal
  rating doesn't have. That is standard practice, and the key is accurate. Blank (not assessed) is kept
  apart from None (empty ball), which is good. The content problems carry over from earlier rounds:
  Q4 "Strong" for an undigitized plate, and "the brief's own word" when brief 2 actually says "Strongest fit
  (partial)".
- **P2 (9).** Harvey balls are the standard qualitative-assessment symbol in engineering and policy
  tables. Neutral gray, consistent.
- **P3 (8).** The balls read well at slide size and in dark mode. The 10.5-px words under each ball are small.
- **P4 (9).** Clearly better than four close grays (Limited and Moderate were hard to tell apart). Keep.

### 6. aquifer_sensitivity_classes: P1 9 · P2 8 · P3 8 · P4 7 = **32 / 40**

- **P1 (9).** Largest-remainder rounding verified: polygons 24.8 / 55.3 / 19.9% give 25 / 55 / 20 squares,
  and area 47.5 / 36.0 / 16.5% gives 48 / 36 / 16. The squares and the labels agree. A small risk: a 10 × 10
  grid titled "Share of listed area" can read as a gridded *map*, on a chart whose point is that nothing can
  be mapped. "One square = 1%" in the subtitle mitigates it.
- **P2 (8).** A plain waffle in the project's gray ramp, darker = more sensitive. Fine.
- **P3 (8).** Clear in both themes (I checked: the cell colors are uniform). The "(map units)" qualifier from
  the plain panel title was dropped.
- **P4 (7).** Better for the part-to-whole message, slightly worse than bars for comparing the two panels.
  The labels compensate. Keep.

**Average pictograph check: 28.8 / 40** (18, 31, 27, 31, 34, 32).

---

## The decision table in docs/analysis.md

- **cuba_area_map should not have become a pictograph as built.** The table keeps the county map plain
  because "pictograms would hide each other". Here they had to be moved apart (22 of 55, up to 8 km,
  3 across rings), which is the same problem solved worse. The good part, formation colors, belongs in the
  *plain* map. Note too that the table says "titles and findings are identical". True, but the report's map
  now carries less information (no formation, no test/log split) than the slide and docs version.
- **placitas_remeasured is defensible but borderline.** The cross-section answers "how does the level
  compare with the well?" better than the title's "how much did it change?" Keep it with the fixes, or pair
  it with the dumbbell.
- **cuba_nearest_records:** it adds little, but it does no harm.
- **rio_puerco_visits, evidence_matrix, aquifer_sensitivity_classes:** good choices, all standard forms.
- **Kept plain, correctly:** every reason in the table holds (hydrographs, trends, canal, river quality,
  Bernalillo, formations). The ojo_alamo_vs_san_jose reasoning ("pictograms would make so few tests look
  more substantial") is especially sound.
- **One candidate that was missed (optional, low risk):** depth_by_area and well_depth_vs_water could use
  the ▽ water-table symbol as their depth-to-water marker. That extends the one hydrologic symbol
  consistently, with no change in position or size. It is not needed for the score.

---

## The 12 plain charts (brief, little changed since round 4)

- **county_coverage_map 82.** The town labels "Bernalillo" and "Rio Rancho" are covered by dots, and
  "Cuba" sits on the county line. The absence claim in the title is unqualified ("none of those is a
  monitoring well" → add "in the collected data").
- **groundwater_hydrographs 89.** Strong. Well A dashed is hard to see where it coincides with Well.
- **groundwater_trends 89.** Good. The indicator table elsewhere says "High at these wells" while this
  caption says the p-values are optimistic (counted under H).
- **well_depth_vs_water 82.** The "water level at the bottom of the well" label sits on a well-log square.
  The title's pooled IQR (41-241 ft) pools record types the caption says not to compare. The title runs to
  3 lines.
- **depth_by_area 85.** Two Placitas tests plot below 0 ft (flowing artesian) with no note in this chart's
  caption (the note is only in well_depth_vs_water). The title is 3 lines.
- **formation_properties 81.** The title is jargon ("2.6-order spread between formation medians"). The
  likely duplicate Madera pair at 0.2 ft²/day is still counted as two values. The Ojo Alamo finding is now
  correct (94.2 is inside 27.5-988).
- **ojo_alamo_depth_map 86.** A good attributed reference crop. As a static image it has no hover (F).
- **ojo_alamo_vs_san_jose 86.** The caption's "49-73 years old" comes from `date.today()` and will drift.
  "7-8 wells" in the title is awkward.
- **rio_grande_quality 88.** The "for scale: EPA taste guideline..." note touches the late-2018 peak.
- **canal_seasonal 90.** Clean.
- **bernalillo_river_vs_well 85.** "ρ = +0.12, n = 22, p = 0.57" touches a dot. The title doesn't carry
  the Bonferroni hedge that the findings give (p = 0.053).
- **coverage_timeline 89.** The subtitle says 1925-2026 while the county map says 1926-2026. The title's
  absence claim is unqualified, although the chart itself says "no records in the collected data".

---

## Suite scores

### G. Coverage of questions and planned outputs: 27 / 30
All planned outputs exist (county map, Cuba-area view, time series, area and aquifer comparisons, coverage
view), and the questions without data are shown as gaps (evidence matrix, coverage timeline, "Insufficient
data" findings). The pictographs neither add nor remove coverage. *Deductions:* there are still no
geologic-region or acequia layers on the maps (data not collected, stated honestly). RQ4 can't be answered
quantitatively, and the evidence matrix still rates it Strong.

### H. Consistency across charts: 15 / 20
New with the pictographs:
1. **Orange = aquifer tests is broken on the Cuba-area pictograph map**, directly above a chart where the
   aquifer-test badge is orange. Gray, which elsewhere means de-emphasized context, is here the most
   prominent mark.
2. **The Placitas old/new blues swap between themes** (old = light in light mode, dark in dark mode), and
   the old marker becomes nearly invisible.
3. **App and docs vs report:** the slide and docs Cuba map shows formation and transmissivity; the report's
   does not. The decision table's "same numbers" is true, but "same content" is not.

Carried over: Q4 Strong in the evidence matrix vs Insufficient data in ojo_alamo_vs_san_jose and
`findings.md`; indicator-table confidence "High" vs the trends caveat; 2 km (Rio Puerco scope) vs 2.3 km
(nearest records); 1925 vs 1926; absence claims qualified in some titles and not others.

*Fixes:* restore orange for well records on the map; give the Placitas old marker one theme-independent
cue (hollow with an ink outline); use one rounding rule for distances and one data-derived start year; add
"in the collected data" to every absence title; reconcile Q4.

### I. Reproducibility and code quality: 25 / 30
Good:
- `icons.py` is a small, well-documented geometry module with stated rules and cached data URIs.
- `PICTOGRAPH_CHARTS` and a single `pictograph=` flag drive both versions, and titles and findings are
  provably identical (I built every chart both ways).
- The relaxation is seeded, so it is deterministic. The README and docs explain the switch. Stats tests pass.

Deductions:
- `charts.py` grew to 2,559 lines, and the plain/pictograph branches use an opaque idiom
  (`for ... in (rows if not pictograph else [])`) in four functions, which is hard for a teammate to follow.
- `_relax` is an O(n² × 400) pure-Python loop (cuba_area_map takes about 1 s per build). The waffle adds
  200 shapes one at a time (about 2 s per build).
- Pillow is an implicit dependency (it comes with Streamlit, but `charts.cuba_area_map` needs it outside
  the app too).
- Carried over: `date.today()` in a caption, and hand-typed counts on the Data sources page ("30 monitoring
  sites ... 1926 to 2026", "456 ... 87 wells", "613").

*Fixes:* split the pictograph builders into `analysis/charts_picto.py` (or plain `if/else` blocks); batch
the shapes with one `update_layout(shapes=[...])`; vectorize the relaxation or replace it with count
badges; add `pillow` to `requirements.txt`; compute the Data sources counts; use the data's years in the
ojo_alamo_vs_san_jose caption.

### J. Integration: 17 / 20
The sidebar "Pictograph charts" switch drives all six charts on every page (through `get_chart`). The docs
and slides get pictograph PNGs and the report gets plain PDFs; all exports match the code pixel for pixel.
`docs/analysis.md` has the decision table, and `docs/streamlit-app.md` and `analysis/README.md` mention the
switch.

*Deductions:*
- The report still lists "County boundary" under datasets to collect.
- `REVIEW_GUIDE.md` and `score_history.md` don't mention the pictograph round (the guide still describes
  the round-3 version and omits `icons.py`).
- The interactive pictograph map's hover targets don't follow zoom.
- The report's Cuba map content differs from the slides, with no note in the report.

---

## Overall

- Average chart score: **84.8** (1,527 / 18)
- Suite score: **84** (27 + 15 + 25 + 17)
- **Overall = 0.7 × 84.83 + 0.3 × 84 = 84.6**
- Average pictograph check: **28.8 / 40** (cuba_area_map 18, cuba_nearest_records 31,
  placitas_remeasured 27, rio_puerco_visits 31, evidence_matrix 34, aquifer_sensitivity_classes 32)

## Top 10 fixes (ordered by expected gain in the overall score)

1. **Rebuild or retire the Cuba-area pictograph map (about +0.8).** Use fixed-pixel symbols (no km
   sizing). Merge co-located wells into one symbol with a count instead of relaxing, and cap any nudge at
   about 1 km with no ring crossings. Drop transmissivity sizing (or use 3 classes with at least 1.5× steps,
   non-overlapping labels, and a matching finding). Keep orange for all well records and show formation as
   a ring. Draw leader lines under the symbols. Clear the Cuba, Jemez Springs, and San Ysidro labels. Or
   simply add formation colors to the plain map and use that everywhere.
2. **Consistency sweep (about +0.7).** Add "in the collected data" to every absence title (county map,
   Cuba map, coverage timeline, nearest records). Use 2.3 km everywhere for the Rio Puerco gage and one
   data-derived start year (1926). Change the indicator-table confidence to "Moderate (9-10 years; p-values
   optimistic)". Compute the Data sources page counts.
3. **Code pass on the pictograph additions (about +0.5).** Replace the `x if not pictograph else []` loops
   with explicit branches or a separate module, batch the waffle shapes, vectorize or remove `_relax`, add
   `pillow` to `requirements.txt`, and replace `date.today()` with the data's years.
4. **Placitas cross-section (about +0.3).** Give the 1997-98 ▽ an outline with at least 3:1 contrast in both
   themes (now 1.42:1 and 1.18:1) and the same meaning in both. Anchor the ▽ apex on the level. Print the
   1997-98 range as text under each label. Use a vertical legend glyph. Lighten the water column, rename it
   "water column above the well bottom", and consider cropping the axis with well bottoms marked as arrows.
5. **Evidence matrix content (about +0.3).** Mark the Q4 cells for dataset 5 as conditional (‡, not
   digitized; for example a dashed ball). Reconcile them with ojo_alamo_vs_san_jose. Change "the brief's own
   word" to "short form of the brief's rating", with the exact phrase in hover. Name Q1, Q2, Q4, and Q8 in the
   "best supported" clause.
6. **Clear the remaining text/mark collisions (about +0.3).** County map town labels (on top, with a halo),
   the Bernalillo ρ label, the well-depth "bottom of the well" label, and the Rio Grande "for scale" note.
7. **Integration notes (about +0.3).** Remove "County boundary" from the report's to-collect list. Add a
   pictograph section to `REVIEW_GUIDE.md` and a row to `score_history.md`. If the report keeps a plain Cuba
   map without formation colors, say in the report that the slide version adds them (or add them to the plain map).
8. **Nearest-records and Rio Puerco polish (about +0.1).** Put the glyph badges in the nearest-records
   legend, or drop the legend. Make the drop anchor width-independent (`sizex` from the plot width) and end
   the Rio Puerco axis after the last visit.
9. **Rescope aquifer sensitivity (about +0.1).** State that the listed area totals about 30.9 square degrees,
   about New Mexico's area, so the shares are probably statewide (scope: "probably statewide; no locations").
   Restore "(map units)" on the right waffle.
10. **Formation chart title in plain words (about +0.1).** For example: "Transmissivity varies more within
    some formations (about 60,000-fold in the Madera Limestone) than between formation medians (about
    400-fold)". Merge or flag the duplicate Madera pair.

## Numeric spot-checks (own code from the CSVs)

| # | Claim (chart) | Recomputed | Match |
|---|---|---|---|
| 1 | **Rio Puerco (P):** 4 flowing visits all in Apr-May, 6 dry Aug-Mar; month panel stacks Mar 1, Apr 3, May 1, Aug 1, Oct 3, Dec 1; flows 6.89-20.4 ft³/s | Local dates from `data4_channel-measurements.csv`: Apr 2019 19.4, May 2020 20.4, Apr 2021 6.89, Apr 2024 20.2; dry Oct 2019, Aug 2020, Oct 2020, Oct 2024, Dec 2025, Mar 2026; by month Mar 1 / Apr 3 / May 1 / Aug 1 / Oct 3 / Dec 1 | yes |
| 2 | **Waffle (P):** 613 polygons (152 / 339 / 122); squares 25 / 55 / 20 and 48 / 36 / 16 | 24.80 / 55.30 / 19.90% → 25 / 55 / 20; area 47.54 / 35.98 / 16.49% → largest remainder 48 / 36 / 16; total area 30.89 units (≈ New Mexico in square degrees) | yes |
| 3 | **Placitas (P):** well depths 220 / 580 / 165 / 300 / 420 ft; PC-025 −57.2, PC-019 −1.5, PC-002 +1.0, PC-055 +3.4, PC-014 +50.9 ft; n 9→1, 8→1, 1→3, 8→1, 9→1; † on PC-025, PC-002, PC-055 | `WellDepth` 220 / 580 / 165 / 300 / 420; means 87.82→30.59, 169.08→167.63, 139.45→140.42, 207.53→210.90, 57.86→108.72; same n; R flags on PC-002 (1), PC-025 (1), PC-055 (8 of 8); PC-025 1997-98 range 58.6-138.9 (80.4 ft) | yes |
| 4 | **Cuba map (P):** 15 test wells within 25 km (1957-1979); "27 of 41 tested wells on the map have a value"; size classes | 41 test wells within 60 km, 27 with transmissivity; classes <10: 5, 10-100: 5, 100-1,000: 9, ≥1,000: 8, not recorded: 14. Examples: Cuba Independent Rural School Well No 1 (0.71 km, Ojo Alamo, 131 → 100-1,000); Smelser (8.8 km, San Jose, exactly 100 → class boundary); Prod Wells 1-5 (11.7-12.5 km, no formation, 5,508 / 1,811 / 733 / 1,510 / 2,299). 15 wells within 25 km, 1957-08 to 1979-05 | yes (but 100 sits on the key's class boundary) |
| 5 | **Cuba map (P):** "where one no longer covers its true location (22 of 55)" | 22 of 55 (from the chart's own table); max shift 8.18 km (ER 4: true 12.2 km, drawn 20.1 km); SH-4 and GT-2 (29.8 km) drawn at 23.8 / 23.3 km, inside the 25-km ring; Prod Well No 3 (11.7 km) drawn at 6.5 km, inside the 10-km ring | caption yes; map position no |
| 6 | **Nearest records (P):** 0.7 km (1957), 2.3 km Rio Puerco, 21 km log (2018), 33 km surface-water statistics (2024), 38 km WL-0062 (2 readings, 2017), 65 km USGS well | 0.71; 2.26; 21.08 (SJ 04288 POD1, 2018); 32.96 (Sulphur Cr, last 2024-11); 38.48 (WL-0062, Sep and Dec 2017; pyproj UTM 13N); 65.22 (Dome Road) | yes |
| 7 | **Evidence matrix (P):** no dataset above Limited for Q3, 5, 6, 7; words from the briefs | Max level per question: Q3 1, Q5 1, Q6 1, Q7 1 (all others ≥ 2). Brief 2 says "Strongest fit (partial)" (shown as "Best fit"); brief 1 says "Strong at monitored wells; limited countywide" (shown as "Strong") | title yes; "brief's own word" partly no |
| 8 | Rio Grande specific conductance: 90% of months 221-342 µS/cm, median 294; pH 7.8-8.3 | p5 221.1, p95 342.1, median 293.8 (266 monthly means, 2003-09 to 2026-02); pH monthly medians p5 7.80, p95 8.30 (2004-10 to 2025-08) | yes |
| 9 | Sandia site rose 13 ft since 2007 | Annual means (≥9 months): 492.05 (2007) → 478.84 (2025) = 13.2 ft; Well A 13.25 ft | yes |

Contrast and color checks used above: white glyph on the gray badge 2.03:1. Placitas 1997-98 ▽ on the
water column 1.42:1 (light) and 1.18:1 (dark). Deuteranopia (Machado 2009) ΔE: ochre vs orange 9.8,
violet vs blue 12.1.
