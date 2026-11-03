"""Small helpers so each Streamlit page can show a chart in one line.

    from analysis import charts
    from analysis.st_helpers import show_chart

    show_chart(charts.groundwater_hydrographs)

``show_chart`` builds the chart (cached, so it's built once per theme), then
shows: the takeaway as a heading, what is plotted, the interactive chart, the
scope and caption, the findings with their Measured / Hypothesis /
Insufficient data labels, and a data table with a CSV download.

This file is the only part of ``analysis/`` that imports Streamlit, so the
chart code also runs outside the app (for the report figures).
"""

from __future__ import annotations

import inspect

import streamlit as st

from . import charts

FINDING_BADGE = {
    "Measured": ":blue-badge[Measured]",
    "Hypothesis": ":orange-badge[Hypothesis]",
    "Insufficient data": ":gray-badge[Insufficient data]",
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}


def is_dark() -> bool:
    """True when the viewer is using Streamlit's dark theme."""
    try:
        return st.context.theme.type == "dark"
    except Exception:  # older Streamlit versions don't have st.context.theme
        return False


def _plotly_kwargs(alt_text: str) -> dict:
    """Arguments that differ between Streamlit versions: newer versions take
    width="stretch" and alt text; older ones (e.g. 1.50) use use_container_width."""
    params = inspect.signature(st.plotly_chart).parameters
    kw = {"width": "stretch"} if "width" in params else {"use_container_width": True}
    if "alt" in params:
        kw["alt"] = alt_text
    return kw


@st.cache_resource(show_spinner="Building chart...")
def _build(name: str, dark: bool, kwargs: tuple) -> charts.Chart:
    fn = getattr(charts, name)
    kw = dict(kwargs)
    if name in ("county_coverage_map", "cuba_area_map"):
        kw.setdefault("basemap", "carto-darkmatter" if dark else "carto-positron")
    return fn(dark=dark, **kw)


def get_chart(chart_fn, **kwargs) -> charts.Chart:
    if chart_fn.__name__ in charts.PICTOGRAPH_CHARTS:  # follows the "Pictograph charts" switch in the sidebar
        kwargs.setdefault("pictograph", st.session_state.get("pictograph", True))
    return _build(chart_fn.__name__, is_dark(), tuple(sorted(kwargs.items())))


def show_chart(chart_fn, show_findings: bool = True, **kwargs) -> charts.Chart:
    """Show a chart with its takeaway, caption, findings, and data table."""
    c = get_chart(chart_fn, **kwargs)
    st.subheader(c.title)
    st.caption(c.subtitle)
    st.plotly_chart(c.fig, theme=None, config=PLOTLY_CONFIG, key=f"chart_{c.key}",
                    **_plotly_kwargs(f"{c.title}. {c.subtitle}"))
    st.caption(f"**Scope: {c.scope}.** {c.caption} *Source: {c.source}.*")
    if show_findings and c.findings:
        st.markdown("\n".join(f"- {FINDING_BADGE.get(label, label)} {text}" for label, text in c.findings))
    with st.expander("Data behind this chart"):
        st.dataframe(c.data, hide_index=True, width="stretch")
        st.download_button("Download as CSV", c.data.to_csv(index=False).encode("utf-8"),
                           file_name=f"{c.key}.csv", mime="text/csv", key=f"dl_{c.key}")
    return c


def finding_legend():
    """One line explaining the three finding labels (from the proposal)."""
    st.caption(
        f"{FINDING_BADGE['Measured']} a pattern the data show directly · "
        f"{FINDING_BADGE['Hypothesis']} a possible explanation the data fit but don't prove · "
        f"{FINDING_BADGE['Insufficient data']} a question these records can't answer yet"
    )
