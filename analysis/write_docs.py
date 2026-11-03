"""Write the chart sections of the documentation from the charts themselves.

Run from the repository root (after ``python -m analysis.export_figures``):

    python -m analysis.write_docs

It rewrites only the part of each page between the markers

    <!-- BEGIN GENERATED: ... -->
    <!-- END GENERATED: ... -->

in ``docs/analysis.md`` and ``docs/findings.md``. Everything outside the markers is
normal hand-written Markdown, so teammates can edit those parts freely. Generating
the chart sections means the titles, numbers, scopes, and findings in the docs always
match the charts, the app, and the report figures.
"""

from __future__ import annotations

import re

from . import charts
from .data import ROOT

DOCS = ROOT / "docs"

# Which app page each chart is on, and which findings section it feeds.
PAGE = {
    "county_coverage_map": ("County map", "Data gaps and monitoring coverage"),
    "groundwater_hydrographs": ("Groundwater levels", "Groundwater levels"),
    "groundwater_trends": ("Groundwater levels", "Groundwater levels"),
    "placitas_remeasured": ("Groundwater levels", "Groundwater levels"),
    "well_depth_vs_water": ("Wells and aquifers", "Wells and aquifer units"),
    "depth_by_area": ("Wells and aquifers", "Wells and aquifer units"),
    "formation_properties__transmissivity_drawdown_ft2_per_day": ("Wells and aquifers", "Wells and aquifer units"),
    "cuba_area_map": ("Cuba case study", "Cuba case study"),
    "cuba_nearest_records": ("Cuba case study", "Cuba case study"),
    "ojo_alamo_depth_map": ("Cuba case study", "Cuba case study"),
    "ojo_alamo_vs_san_jose": ("Cuba case study", "Cuba case study"),
    "rio_puerco_visits": ("Cuba case study", "Cuba case study"),
    "coverage_timeline": ("Data sources", "Data gaps and monitoring coverage"),
    "evidence_matrix": ("Data sources", "Data gaps and monitoring coverage"),
    "aquifer_sensitivity_classes": ("Data sources", "Data gaps and monitoring coverage"),
}
SECTION_ORDER = ["Groundwater levels", "Wells and aquifer units", "Cuba case study", "Data gaps and monitoring coverage"]
SECTION_RQS = {"Groundwater levels": "1", "Wells and aquifer units": "2", "Cuba case study": "3 and 4",
               "Data gaps and monitoring coverage": "5 and 6"}


def _replace_block(path, name: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = f"<!-- BEGIN GENERATED: {name} -->", f"<!-- END GENERATED: {name} -->"
    block = f"{start}\n<!-- Written by `python -m analysis.write_docs`; edit the chart code, not this block. -->\n\n{body.strip()}\n\n{end}"
    if start in text:
        text = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


def _slug(heading: str) -> str:
    """The anchor MkDocs (Python-Markdown toc) gives a heading."""
    value = re.sub(r"[^\w\s-]", "", heading).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def build(chart_list=None):
    fns = list(chart_list or charts.ALL_CHARTS)
    built = [fn() for fn in fns]
    name = {c.key: fn.__name__ for c, fn in zip(built, fns)}  # chart key -> function name
    number = {c.key: i for i, c in enumerate(built, start=1)}
    link = {k: f"{number[k]}. {name[k]}" for k in name}  # section heading text

    # --- docs/analysis.md: overview table + one section per chart ---------------
    rows = ["| # | Chart | Research questions | App page | Takeaway |", "|---|---|---|---|---|"]
    for i, c in enumerate(built, start=1):
        page = PAGE.get(c.key, ("", ""))[0]
        rows.append(f"| {i} | [{name[c.key]}](#{_slug(link[c.key])}) | "
                    f"{', '.join(str(q) for q in c.rqs)} | {page} | {c.title} |")
    sections = []
    for i, c in enumerate(built, start=1):
        findings = "\n".join(f"- **{lab}:** {txt}" for lab, txt in c.findings)
        sections.append(
            f"### {link[c.key]}\n\n"
            f"![{c.title}](figures/{c.key}.png)\n\n"
            f"**Takeaway:** {c.title}.\n\n"
            f"| | |\n|---|---|\n"
            f"| Research questions | {', '.join(str(q) for q in c.rqs)} |\n"
            f"| What is plotted | {c.subtitle} |\n"
            f"| Scope | {c.scope} |\n"
            f"| Data | {c.source} |\n"
            f"| App page | {PAGE.get(c.key, ('', ''))[0]} |\n"
            f"| Code | `charts.{name[c.key]}()` in `analysis/charts.py` |\n\n"
            f"**How to read it and method:** {c.caption}\n\n"
            f"**Findings:**\n\n{findings}\n"
        )
    _replace_block(DOCS / "analysis.md", "chart index", "\n".join(rows))
    _replace_block(DOCS / "analysis.md", "chart sections", "\n\n".join(sections))

    # --- docs/findings.md: findings grouped by topic ----------------------------
    by_section = {s: [] for s in SECTION_ORDER}
    for c in built:
        sec = PAGE.get(c.key, ("", "Data gaps and monitoring coverage"))[1]
        for lab, txt in c.findings:
            by_section[sec].append((lab, txt, c))
    out = []
    for sec in SECTION_ORDER:
        items = by_section[sec]
        if not items:
            continue
        order = {"Measured": 0, "Hypothesis": 1, "Insufficient data": 2}
        items.sort(key=lambda t: order.get(t[0], 3))
        lines = [f"- **{lab}:** {txt} *(chart {number[c.key]}: [{name[c.key]}](analysis.md#{_slug(link[c.key])}))*"
                 for lab, txt, c in items]
        out.append(f"## {sec}\n\nResearch question{'s' if 'and' in SECTION_RQS[sec] else ''} "
                   f"{SECTION_RQS[sec]}.\n\n" + "\n".join(lines))
    _replace_block(DOCS / "findings.md", "findings by topic", "\n\n".join(out))
    return built


if __name__ == "__main__":
    build()
    print("Updated the generated blocks in docs/analysis.md and docs/findings.md")
