# Project report

LaTeX source for the project report, styled to match the project proposal (two columns, Palatino, navy headings).

| File | Contents |
|---|---|
| `report.tex` | The report |
| `references.bib` | Bibliography (BibTeX) |
| `figures/` | Chart images made by `analysis/export_figures.py`: plain PDFs for the report, PNGs with titles for slides |
| `analysis_figures.tex` | A ready-made figure block for every chart, also made by `export_figures.py` |

Every section of the report is written. Two orange notes in brackets mark paragraphs to update when the remaining datasets are cleaned and when the app is finished.

## Editing and building

**Overleaf (easiest):** zip this `report` folder, then in Overleaf choose **New Project → Upload Project**. When you're done, download the source (**Menu → Download → Source**) and replace the files here.

**On your own computer** with a TeX distribution installed:

```
latexmk -pdf report.tex
```

## Adding a figure

The charts come from `analysis/charts.py`. Running `python -m analysis.export_figures` from the repository root (see the main README) remakes `figures/` and `analysis_figures.tex`. To add a chart to the report, copy its block from `analysis_figures.tex` into `report.tex` and shorten the caption. Use `figure*` for a chart across both columns; most charts are too detailed to read at single-column width.

For an image that isn't a chart, save it in `figures/` and add:

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{your-figure-name}
  \caption{What it shows. Source.}
  \label{fig:your-label}
\end{figure*}
```

## Switches

At the top of `report.tex`:

- `\draftnotesfalse` hides the orange notes.
- `\roughdraftfalse` removes the red ROUGH DRAFT stamp and sets the date to the final due date.
- `\coverpagetrue` adds a cover page matching the proposal's.

## Publishing the PDF

The documentation site links to `docs/files/project_report_draft.pdf`. After rebuilding, copy the new PDF there, commit, push, and run `mkdocs gh-deploy`.
