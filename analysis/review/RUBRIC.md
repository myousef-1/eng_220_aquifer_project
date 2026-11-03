# Visualization grading rubric

Written for this project because the course didn't provide a chart rubric. It turns the
project's own rules into scores, so every chart is judged against what the team already
agreed on:

- the **project proposal** (`project_notes/project_proposal.pdf`): planned outputs, and labeling
  each finding as *Measured*, *Hypothesis*, or *Insufficient data*;
- **Dylan's plotting guide and dataset briefs** (`docs/files/`): every caption must say whether
  it describes Cuba, Sandoval County, or the wider region; increasing depth to water means a
  falling water table; spot visits are not continuous records; don't mix monthly and yearly
  USGS statistics; and so on;
- **James's cleaning conventions** (`docs/data-cleaning.md`);
- standard data-visualization practice (clear form, labeled axes and units, accessible colors,
  no dual axes, no clutter).

A grader scores each chart on criteria A-F (100 points per chart) and the set as a whole on
criteria G-J (100 points). **Overall score = 0.7 × average chart score + 0.3 × suite score.**

## Score levels (used for every criterion)

| Level | Share of the points | Meaning |
|---|---|---|
| Excellent | 100% | No issues a careful reviewer would raise |
| Good | 75% | Minor issues that don't mislead |
| Fair | 50% | A noticeable problem a reader would trip over |
| Poor | 25% | A serious problem: misleading, confusing, or missing something required |
| Missing | 0% | Not done, or wrong |

Graders may give in-between scores. Every deduction must name the specific problem and a fix.

## Per-chart criteria (100 points)

### A. Answers a research question (15)
- The chart is tied to at least one of the nine research questions.
- The title states the takeaway as a sentence a reader can repeat, not just a topic.
- The chart type fits the question (trend → time series, comparison → aligned dots or bars,
  where → map, before/after → dumbbell, and so on).

### B. Data accuracy and honest representation (25)
- Numbers in the title, subtitle, caption, and findings match the data (graders should
  spot-check by running the code).
- Correct subset, units, and statistic; monthly, calendar-year, and water-year USGS rows are
  never mixed.
- No invented data: no lines between spot visits, no interpolation across gaps, no smoothing
  presented as measurement.
- Depth to water is shown so "up" or the axis label makes clear what a bigger number means.
- Sample sizes are visible where they're small; off-scale or excluded points are disclosed.
- Statistical claims (trends, correlations) state the method and are hedged appropriately.

### C. Scope and uncertainty labeling (15)
- Says plainly whether the chart describes Cuba itself, the Cuba area, Sandoval County, or
  the wider region, and how far from Cuba the data are when that matters.
- Carries the caveats from Dylan's brief for that dataset.
- Findings use the proposal's labels correctly: a *Hypothesis* is never stated as fact, and
  questions the data can't answer are marked *Insufficient data*.

### D. Visual design and readability (20)
- Axis titles with units; readable tick labels; legend or direct labels for every series.
- No overlapping or clipped text; nothing important hidden behind other marks.
- Colors are consistent with the rest of the project, colorblind-safe, and carry meaning
  (not decoration); no more categories than the eye can track.
- No dual-axis charts. Panels with separate scales say so.
- Readable when shrunk to report width (about 7 inches).

### E. Caption and annotation quality (10)
- The subtitle says what is plotted (variable, units, place, period).
- The caption explains how to read the chart, the method, and its limits, in plain language.
- The source is named precisely enough to find the file in the repository.

### F. Interactivity and app readiness (10)
- Hover tooltips give the exact value, date, and site.
- A data table and download are available (so no value is reachable only by hover).
- Works in the app's light and dark themes.

## Suite criteria (100 points)

### G. Coverage of the project's questions and planned outputs (30)
- The proposal's planned outputs exist where data allow: county map, Cuba-area view,
  time series for repeated measurements, summary comparisons by area or aquifer unit,
  and a data-coverage view.
- Research questions without data are addressed honestly (shown as gaps) rather than skipped.

### H. Consistency across charts (20)
- The same colors, terms, and scope labels mean the same thing everywhere.
- The same caption structure and finding labels on every chart.

### I. Reproducibility and code quality (30)
- Runs from a fresh clone with the packages in `requirements.txt`; paths built from the file's
  location (as the README asks); no hand-typed numbers in titles or captions.
- Readable, documented code that a teammate can follow and change.
- Raw data never edited; any preparation done in code is documented.

### J. Integration (20)
- Charts appear on the matching Streamlit pages with captions, findings, and data tables.
- Static exports exist for the report, slides, and docs site.

## Stopping rule for the improvement loop

Grade, fix, and re-grade for at most 5 rounds. Stop early if the overall score reaches 95, or
if a round improves the overall score by less than 1 point. Each round's full report is saved
in this folder as `round_<n>.md`, and `score_history.md` summarizes them.
