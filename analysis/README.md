# analysis/

Analysis code and charts for the project (lead: Micah Watkins). Every chart in the Streamlit app,
the report, and the documentation site comes from a function in `charts.py`, so the numbers match
everywhere. The full write-up, with every chart, is on the docs site's
[Analysis and visualizations](../docs/analysis.md) page.

## Files

| File | What it does |
|---|---|
| `data.py` | Loads every dataset into the shared column format (`site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`). Uses James's cleaned files where they exist; does minimal preparation of raw files that aren't cleaned yet (never edits them). |
| `stats.py` | Annual means, Sen's slope, Mann-Kendall test, Spearman correlation, permutation p-value. Only numpy. |
| `theme.py` | Colors and the shared Plotly look, in light and dark versions. Says what each color means. |
| `icons.py` | Small flat pictograms (well, well log, water-table symbol, stream gage, drop, Harvey ball) for the pictograph versions of six charts, as SVG or PNG. States the rules they follow. |
| `charts.py` | One function per chart. Each returns a `Chart` with the figure, a takeaway title, caption, scope, labeled findings, and the data behind it. `ALL_CHARTS` lists the 15 charts in order; `OUT_OF_SCOPE_CHARTS` lists 3 charts for research questions the team dropped (not shown anywhere). |
| `st_helpers.py` | `show_chart(...)`: shows a chart on a Streamlit page with its caption, findings, and data table. The only file here that imports Streamlit. |
| `export_figures.py` | Writes `report/figures/*.pdf` (no baked-in text, for LaTeX), `report/figures/*.png` and `docs/figures/*.png` (with title and caption, for slides and docs), `report/analysis_figures.tex`, and `figure_index.csv`. |
| `write_docs.py` | Rewrites the generated chart sections of `docs/analysis.md` and `docs/findings.md` from the charts. |
| `review/` | The grading rubric and each review round's report. |

## Common tasks

**Show a chart on an app page** (Meckrem):

```python
from analysis import charts
from analysis.st_helpers import show_chart

show_chart(charts.rio_puerco_visits)
show_chart(charts.formation_properties, metric="specific_capacity_gpm_per_ft")   # charts with options
```

Don't call `st.set_page_config` in a page; `ProjectApp.py` already does.

**Use a chart outside the app:**

```python
from analysis import charts
c = charts.groundwater_trends()
c.fig.show()            # interactive
print(c.title)          # takeaway
print(c.data.head())    # data behind it
```

**Remake the report and docs figures after changing a chart** (from the repository root):

```
pip install kaleido
python -m analysis.export_figures
python -m analysis.write_docs
```

**Swap in a newly cleaned file** (James): change the body of the matching loader in `data.py`
(`load_nmbgmr_levels`, `load_rio_puerco`, or `load_well_logs`) to `pd.read_csv(CLEAN / "new_file.csv")`.
The charts don't need to change, because the loaders already return the shared column names.

**Pictograph or plain:** the six charts in `charts.PICTOGRAPH_CHARTS` take `pictograph=True` (default; used by the
app and `docs/figures/`) or `pictograph=False` (the plain version used in `report/figures/`). In the app, the
"Pictograph charts" switch in the sidebar (`ProjectApp.py`) picks one for every page.

**Add a new chart:** write a function in `charts.py` that returns a `Chart` (copy a short one such as
`aquifer_sensitivity_classes`), add it to `ALL_CHARTS`, call `show_chart` on a page, and add it to
`PAGE` in `write_docs.py`. Compute every number in the title and findings from the data rather than
typing it in.

## Conventions

- Depth-to-water axes are flipped, so up means a higher water table. Trend charts report
  water-level change, so negative means the water table is falling.
- Every chart says whether it describes Cuba, the Cuba area (within 25 km), or Sandoval County.
- Findings use the proposal's labels: Measured, Hypothesis, Insufficient data.
- No lines between spot measurements or across gaps; small samples show their n.
- Colors: blue = water-level records, orange = well construction and aquifer tests, aqua = surface
  water; ochre/violet = Ojo Alamo/San Jose; red/blue/gray = falling/rising/no clear trend.
- Pictograms: one pictogram = one real thing or one fixed unit; sizes only through stated classes with a
  key; standard hydrology symbols where one exists (▽ water table, well casing, cone of depression, waves).
