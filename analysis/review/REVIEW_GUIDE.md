# Review guide for Micah

Everything for your part of the project (analysis code and visualizations) is finished and merged
with the team's latest work on `main`. This page covers what was done, how to check it, what to tell
teammates, your slide and video, and how the work gets into the shared repository.

## 1. What was done, in one paragraph

A new `analysis/` package turns the team's data into 15 charts and figures covering all six research
questions. Each chart is one Python function that returns the figure **plus** its takeaway title,
caption, scope (Cuba vs county), labeled findings (Measured / Hypothesis / Insufficient data), and
the data behind it. The same functions feed the Streamlit pages, the report figures, and the docs
site, so every number matches everywhere. The charts were graded against a rubric built from the
proposal and Dylan's plotting guide and improved over several graded rounds (section 6).

**Pictograph versions.** Following Petar's idea, every chart was looked at for small pictograms,
and six got a pictograph version: Placitas wells drawn as to-scale cross-sections, a Cuba-area map
of well pictograms sized by transmissivity, pictogram stems for the nearest records, river-visit
drops, Harvey balls for the evidence matrix, and unit squares for aquifer sensitivity. The app and
slide images use them; the LaTeX report keeps the plain versions; a **Pictograph charts** switch in
the app's sidebar flips between the two. Reasons for each chart are in `docs/analysis.md`, section
"Pictograph versions".

**Merged with the team's narrowed research questions.** While this work was in review, Petar
narrowed the questions from nine to six (water quality, acequias, and groundwater-river links were
dropped; the old Q8 and Q9 are now Q5 and Q6) and removed the Water quality and Acequias app pages.
Everything here now follows that: research-question numbers in the charts, app, docs, and report;
the evidence matrix shows the six questions; and the three charts that only answered dropped
questions (Rio Grande water quality, canal seasonal flow, Bernalillo river vs well) are out of the
app, docs, report, and figure exports. Their code stays in `analysis/charts.py` as
`OUT_OF_SCOPE_CHARTS` in case those questions come back.

**The headline result:** the data can't confirm or rule out severe depletion of Cuba's aquifer. Wells
near Cuba have only one-time water levels from 1957-1979 aquifer tests; the nearest well measured
more than once is 38 km away. Where wells are monitored (Rio Rancho to Cochiti), 5 of 9 wells fell
over their records and the Sandia site has risen about 13 ft since 2007.

## 2. Check it yourself

1. **Run the app** from the repo folder:
   ```
   python -m pip install -r requirements.txt
   python -m streamlit run ProjectApp.py
   ```
   Click through County map, Groundwater levels, Wells and aquifers, Cuba case study, and Data
   sources. Each chart has a takeaway, caption, labeled findings, and a "Data behind this chart"
   table. Flip the **Pictograph charts** switch in the sidebar to compare the two versions.
2. **Skim the docs page** `docs/analysis.md` (or run `mkdocs serve` and open "3. Analysis and
   visualizations"), then `docs/findings.md` for the bottom line.
3. **Look at the figures:** `docs/figures/` has the app versions with titles (pictographs where
   they exist; good for slides), and `report/figures/` has the plain versions for the LaTeX report.
4. **Open the slide deck** `docs/files/beneath_the_mesa_slides.pptx`: slide 10 (yours) and the
   "Analyze" line on slide 7 are filled in.
5. Optional: `python -m analysis.test_stats` checks the trend statistics against known answers.

## 3. What changed, file by file

**New (yours):**

| File | What it is |
|---|---|
| `analysis/data.py` | Loads every dataset into the team's shared column format; minimal prep of raw files not yet cleaned |
| `analysis/stats.py`, `analysis/test_stats.py` | Sen's slope, Mann-Kendall, Spearman, permutation test; and checks |
| `analysis/theme.py` | Colors (color-blind checked) and the Plotly look, light and dark |
| `analysis/icons.py` | The pictograms (well, well log, water-table symbol, stream gage, drop, Harvey ball) and the rules they follow |
| `analysis/charts.py` | The 15 charts (`ALL_CHARTS`); six have `pictograph=True/False`; three out-of-scope charts kept as `OUT_OF_SCOPE_CHARTS` |
| `analysis/st_helpers.py` | `show_chart()` for app pages (follows the sidebar switch) |
| `analysis/export_figures.py`, `analysis/write_docs.py` | Regenerate report/docs figures and the chart sections of the docs |
| `analysis/README.md` | How teammates use the module |
| `analysis/assets/ha720b_fig5_cuba_area.jpg` | Crop of the USGS Ojo Alamo map around Cuba (public domain) |
| `analysis/review/` | Rubric, review reports, score history, this guide, and `round_4_changes.diff` (reference only) |
| `analysis/figure_index.csv` | Every chart's title, scope, findings, and source in one table |
| `data/sandoval_county_boundary.geojson` | County outline for the maps (US Census via plotly/datasets) |
| `docs/figures/*.png`, `report/figures/*.pdf, *.png`, `report/analysis_figures.tex` | Exported figures |

**Edited in teammates' areas (worth a heads-up, see section 4):**

| File | Change |
|---|---|
| `ProjectApp.py` (Meckrem) | One sidebar switch, "Pictograph charts"; the team's removal of the Water quality and Acequias pages is kept |
| `app_pages/*.py` (Meckrem) | "Coming soon" placeholders replaced with charts, using the team's new page intros and research-question numbers |
| `requirements.txt` (Meckrem) | Version floors: `streamlit>=1.50`, `plotly>=6.0`, `numpy>=1.24`, `pandas>=2.0`, `pillow>=10.1` |
| `docs/analysis.md`, `docs/findings.md` | Written in full, for the six research questions |
| `docs/streamlit-app.md` (Meckrem) | "What the app shows" table; the pictograph switch |
| `docs/team.md`, `docs/timeline.md` | Your contribution paragraph; a three-quarter checkpoint line for the analysis |
| `docs/data-cleaning.md` (James), `docs/data-collection.md` (Dylan) | One paragraph on the in-code prep; the county boundary file and its source |
| `report/report.tex`, `report/references.bib` (Petar) | Merged with Petar's rewrite of the Data sections. Figures 1-3 added (plain versions); the Analysis methods; Results for RQ1-RQ6 (including a new "Groundwater-Stress Indicators" subsection for RQ6); the Limitations list combines Petar's dropped-questions text with the analysis's own limits; your line in Team Contributions. Two references added (Helsel et al. 2020, Ritchie et al. 2019); Petar's fuller entries for Thorn 1990 and Blandford 2025 are kept. Compiles cleanly. |
| `docs/files/beneath_the_mesa_slides.pptx` (Petar) | Slide 10 (yours) filled in with a chart; the "Analyze" line on slide 7 |

## 4. Things to tell teammates

- **Petar:** the report merge keeps your rewritten Data and Data Cleaning sections; Results now
  cover RQ1-RQ6 in the new numbering, with the Rio Puerco visits as surface-water context in the
  Cuba case study. The abstract, Discussion, and Conclusions placeholders are still yours; the
  numbers for them are in `docs/findings.md`. Slide 10 and the slide 7 "Analyze" line are filled;
  `docs/files/beneath_the_mesa_slides.pdf` wasn't re-exported, so re-export it from PowerPoint
  after the remaining slides are done. The app and slide images use the pictograph versions of six
  charts; the report keeps the plain versions.
- **Meckrem:** every page calls `show_chart(...)`; restyle freely. `ProjectApp.py` has one new
  sidebar switch for the pictograph charts. Your report section ("Interactive Dashboard") still has
  its placeholder for describing each page; `docs/streamlit-app.md` has a page table you can use.
- **James:** `analysis/data.py` does minimal prep of datasets 2, 4, and 7 until you clean them;
  swapping in a cleaned file means changing one loader (see `analysis/README.md`). Data issues found
  along the way: the formation typo `NACIEMIENTO` is still in the cleaned file; well log
  **SJ 04455 POD1** has a northing that puts it ~80 km north of its legal description (likely a
  typo); aquifer test **RG-54556x** lists water at 458 ft in a 30 ft well (left out of charts); two
  Ojo Alamo test records ("Cuba Independent Rural School Well No 1" and "21.1W.28.143") look like the
  same well; the Smelser Well test (BIA-(RF)-033-2(10)) is entered twice with slightly different
  coordinates (the loader merges rows with the same name and date within 1 km); and two Madera
  tests may be duplicates under different names ("Rock Springs Well" / "San Pedro Creek Estates, Rock
  Springs Well", and "Campbell Ranch Well 4" / "San Pedro Creek Estates, Well 4").
- **Dylan:** dataset 5 (the Ojo Alamo plate) is shown as a labeled crop on the Cuba page; dataset 6's
  Table 1 transmissivity values are compared with the San Jose test. The evidence matrix carries your
  briefs' ratings over to the six new questions (Q1-Q4 unchanged, Q8 -> Q5, Q9 -> Q6).

## 5. Decisions you may want to change

| Decision | Where to change it |
|---|---|
| "Cuba area" = within 25 km of the village center | `CUBA_RADIUS_KM` in `analysis/charts.py` |
| Recent trend window = 2016-2025 | `groundwater_trends(recent_start=..., recent_end=...)` |
| Years need 9+ months of data to count in trends | `MIN_MONTHS_PER_YEAR` in `analysis/stats.py` |
| Area groups = nearest of 7 towns within 20 km | `AREA_ANCHORS`, `AREA_RADIUS_KM` in `analysis/charts.py` |
| The Sandia recovery hypothesis cites the San Juan-Chama project (Ritchie et al. 2019, USGS SIM 3435) | finding text in `groundwater_hydrographs()` |
| Which charts have pictographs; pictograph by default in the app | `PICTOGRAPH_CHARTS` in `analysis/charts.py`; the switch's `value=True` in `ProjectApp.py` |
| Cuba map: 3 transmissivity size classes, wells within 1 km share a pictogram, nudges of at most 1 km | `T_CLASSES`, `GROUP_KM`, `MAX_NUDGE_KM` in `analysis/charts.py` |
| Charts left out after the questions were narrowed | `OUT_OF_SCOPE_CHARTS` in `analysis/charts.py` (move one back into `ALL_CHARTS` to show it again) |

After any change: `python -m analysis.export_figures` then `python -m analysis.write_docs`.

## 6. How the charts were graded

No course rubric for charts existed, so one was written from the project's own rules (proposal,
Dylan's plotting guide and briefs, James's conventions) plus standard chart practice:
`analysis/review/RUBRIC.md`. Each round a fresh reviewer graded every chart blind, and the charts
were fixed from the feedback. Scores are in `analysis/review/score_history.md`:

| Round | Overall (out of 100) |
|---|---|
| 1 | 72.0 |
| 2 | 84.0 |
| 3 | 86.3 |
| 4 | 86.0 |
| Pictograph review (one pass, as agreed) | 84.6, then fixed (not re-graded) |

After round 4 the round-3 files (the top score) were kept, and the round-4 fixes for real errors
were brought back with the pictograph work. The pictograph review was hardest on the first Cuba-area
pictograph map, which was rebuilt from its feedback; its other top fixes were applied too. The
reviews used the original nine research questions; the charts have since been renumbered to the six.

## 7. Your slide and your video

**Slide 10 is filled in** (what I did, how I did it, what I learned, and the nearest-records chart
with a caption), and slide 7's "Analyze" step says "Trend statistics and 15 charts with labeled
findings". Edit the wording in PowerPoint if you'd like it in your own voice.

**Talking points for your video** (due Nov 15, about your part):

1. My job: turn the cleaned data into charts that answer our research questions, for the app, the
   report, and the docs site.
2. How: Python, pandas, and Plotly. One function per chart returns the figure together with its
   takeaway, caption, scope, and labeled findings, so every number matches everywhere. Trends use
   Sen's slope and the Mann-Kendall test.
3. Show two charts: the nearest-records chart (the Cuba data gap: the nearest repeated water-level
   record is 38 km away) and the groundwater hydrographs (5 of 9 monitored wells falling; Sandia up
   about 13 ft since 2007). Flip the pictograph switch in the app to show the pictograph versions.
4. What I learned: being honest with thin data. Every chart says whether it describes Cuba or the
   rest of the county, and every finding is labeled measured, hypothesis, or insufficient data.

## 8. Getting it into the shared repository

The work goes in as a **branch and pull request** in GitHub Desktop, so Petar and Meckrem can see
the changes to their files before it lands on `main`. The step-by-step version is in the chat; in
short:

1. GitHub Desktop: **Branch > Stash all changes**, then **Fetch origin** and **Pull origin**, so
   your `main` matches the team's.
2. **Branch > New branch**: `analysis-visualizations`.
3. The final files are copied into the folder (they already include the team's latest changes).
4. In the Changes tab, write the summary "Add analysis code, charts, and app pages", then **Commit
   to analysis-visualizations**.
5. **Publish branch**, then **Create Pull Request**, and paste the prepared description.
6. After the pull request is merged on GitHub, switch back to `main` in GitHub Desktop and **Pull
   origin**. You can then discard the old stash (Branch > the stash list, or leave it; it's only a
   backup).

After the merge, the live app updates within a minute or two. Petar redeploys the docs site with
`mkdocs gh-deploy`.
