"""Every chart in the project, one function per chart.

How to use a chart
------------------
Each function returns a ``Chart``: the Plotly figure plus the text that has to
travel with it (headline, what is plotted, caption with scope and caveats,
the findings it supports, and the data behind it)::

    from analysis import charts
    c = charts.groundwater_hydrographs()
    c.fig          # the interactive Plotly figure (use in Streamlit)
    c.title        # one-line takeaway, written from the data
    c.caption      # how to read it, method, caveats
    c.scope        # Cuba / Cuba area / Sandoval County, and distance from Cuba
    c.findings     # [("Measured", "..."), ("Hypothesis", "..."), ...]
    c.data         # the table behind the chart (for a table view or download)
    c.static()     # a copy with title and caption baked in, for PNG/PDF export

In Streamlit, ``analysis.st_helpers.show_chart`` shows a Chart with its caption,
findings, and a data table in one call.

Rules every chart follows (from the proposal and Dylan's plotting guide)
    * Say whether it describes Cuba, the Cuba area, or Sandoval County, and how
      far the data are from Cuba.
    * Depth to water is "feet below land surface": a bigger number is a LOWER
      water table. Depth axes are flipped so "up" means a higher water table.
    * Plot measurements, don't invent them: no lines drawn between spot visits,
      no lines across gaps, and small samples are labeled with their n.
    * Use one interval type at a time from the USGS statistics (monthly OR yearly).
    * Numbers in titles, captions, and findings are computed from the data.
    * Findings carry the proposal's labels: Measured, Hypothesis, Insufficient data.

Pictograph versions
    Six charts can draw small flat pictograms (a well, a stream gage, a river
    visit, a rating ball) instead of plain dots or bars: ``PICTOGRAPH_CHARTS``.
    They take ``pictograph=True`` (the default, used by the app and the slide /
    docs images); ``pictograph=False`` gives the plain version, used for the
    LaTeX report. Both versions are built from the same numbers. See
    ``analysis/icons.py`` for the rules the pictograms follow.

``ALL_CHARTS`` at the bottom lists every chart in display order. ``OUT_OF_SCOPE_CHARTS``
lists three charts for research questions the team dropped; they aren't shown anywhere.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import data as d
from . import icons
from . import stats as st_
from .theme import (
    DATA_TYPE_ORDER,
    LINE_WIDTH,
    MARKER_RING,
    MARKER_SIZE,
    RAMP_DARK,
    RAMP_LIGHT,
    data_type_color,
    palette,
    template_name,
)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CUBA_RADIUS_KM = 25  # analysis choice: "Cuba area" = within 25 km of the village center

SCOPE_CUBA = "Cuba (measured at Cuba)"
SCOPE_CUBA_AREA = f"Cuba area (within {CUBA_RADIUS_KM} km of Cuba)"
SCOPE_COUNTY = "Sandoval County, not Cuba"
SCOPE_COUNTY_ALL = "Sandoval County, including the Cuba area"
SCOPE_PROJECT = "Whole project (all datasets)"

FILES = {
    "gw": "data/clean/groundwater_levels_monthly.csv",
    "tests": "data/clean/aquifer_tests.csv",
    "nmbgmr": "data/clean/groundwater_levels_nmbgmr.csv",
    "sens": "data/clean/aquifer_sensitivity.csv",
    "rio_puerco": "data/clean/streamflow_measurements.csv",
    "logs": "data/clean/well_logs.csv",
    "usgs": "data/water_flow_data_sandoval_county_sources.csv (dataset 1)",
    "boundary": "data/sandoval_county_boundary.geojson (US Census Bureau, via plotly/datasets)",
}
ALL_SOURCES = (f"{FILES['gw']}, {FILES['tests']}, {FILES['nmbgmr']}, {FILES['logs']}, "
               f"{FILES['usgs']}, {FILES['rio_puerco']}; county outline: {FILES['boundary']}")


# ---------------------------------------------------------------------------
# The Chart object
# ---------------------------------------------------------------------------
@dataclass
class Chart:
    key: str
    title: str                      # the takeaway, as a sentence
    subtitle: str                   # what is plotted, with units
    caption: str                    # how to read it, method, caveats
    scope: str                      # Cuba / Cuba area / county / project, with distance
    rqs: tuple                      # research questions this chart helps answer
    findings: list                  # [(label, text)], label in Measured/Hypothesis/Insufficient data
    fig: go.Figure
    data: pd.DataFrame
    source: str
    height: int = 520

    def static(self, width: int = 1000, with_text: bool = True) -> go.Figure:
        """A copy of the figure for images, always in the light theme.

        ``with_text=True`` bakes in the title, subtitle, scope, and source (for the
        slides and docs). ``with_text=False`` leaves them out, for the LaTeX report,
        where the caption is written in LaTeX. Text wrapping is computed from
        ``width``, so other widths don't clip."""
        p = palette(False)
        fig = go.Figure(self.fig)
        if not with_text:
            fig.update_layout(template=template_name(False), width=width, height=self.height, font=dict(size=15))
            return fig
        m = fig.layout.margin
        base_t = m.t if m.t is not None else 50
        base_b = m.b if m.b is not None else 60
        base_l = m.l if m.l is not None else 70
        title = _wrap(self.title, int(width / 11.2))
        subtitle = _wrap(self.subtitle, int(width / 8.3))
        title_h = 27 * (title.count("<br>") + 1) + 20 * (subtitle.count("<br>") + 1) + 30
        foot = _wrap(f"Scope: {self.scope}.  Source: {self.source}", int(width / 6.4))
        foot_h = 17 * (foot.count("<br>") + 1) + 22
        fig.update_layout(
            template=template_name(False),
            width=width,
            height=self.height + title_h + foot_h,
            margin=dict(t=base_t + title_h, b=base_b + foot_h, l=base_l),
            font=dict(size=15),
            title=dict(
                text=(f"<b>{title}</b><br><span style='font-size:14.5px;color:{p['ink2']}'>{subtitle}</span>"),
                x=0, xref="container", xanchor="left", y=1, yref="container", yanchor="top",
                pad=dict(l=22, t=18), font=dict(size=19.5, color=p["ink"]),
            ),
        )
        # The footer is placed relative to the plot area, whose left edge can move when
        # Plotly widens the margin for long tick labels; measure it so every footer
        # starts at the same distance from the image edge.
        plot_left = _plot_left_px(fig, base_l)
        fig.add_annotation(
            text=f"<span style='color:{p['muted']}'>{foot}</span>",
            xref="paper", yref="paper", x=0, y=0, xshift=-(plot_left - 22), yshift=-(base_b + 6),
            xanchor="left", yanchor="top", showarrow=False, align="left", font=dict(size=12),
        )
        return fig


def _plot_left_px(fig: go.Figure, default: float) -> float:
    """Left edge (px) of the plot area after Plotly's automatic margins. Needs the
    image exporter (kaleido); falls back to the requested margin without it."""
    if any(t.type == "scattermap" for t in fig.data):
        return default
    try:
        import re as _re
        svg = fig.to_image(format="svg").decode("utf-8", "ignore")
        # each x axis has a clip rectangle whose x is the left edge of its plot area
        xs = [float(v) for v in _re.findall(r'class="axesclip" id="[^"]*x\d*"><rect x="([\d.]+)"', svg)]
        return min(xs) if xs else default
    except Exception:
        return default


def _sig(v: float, n: int = 3) -> str:
    """Number with n significant digits, written out (2,760 not 2.76e+03; 0.0123 not 1.23e-02)."""
    if v == 0 or not np.isfinite(v):
        return f"{v:g}"
    digits = max(n - 1 - int(np.floor(np.log10(abs(v)))), 0)
    out = f"{round(v, digits):,.{digits}f}"
    return out.rstrip("0").rstrip(".") if "." in out else out


def _wrap(text: str, width: int) -> str:
    return "<br>".join(textwrap.wrap(text, width=width, break_on_hyphens=False)) if text else ""


def _ring(dark: bool) -> dict:
    return dict(width=MARKER_RING, color=palette(dark)["surface"])


def _base_layout(fig: go.Figure, dark: bool, height: int, **kw) -> go.Figure:
    fig.update_layout(template=template_name(dark), height=height, **kw)
    return fig


def _km_range(lat, lon) -> str:
    """'65-95 km' style distance range from Cuba, rounded to 5 km."""
    dist = d.distance_km(lat, lon)
    lo, hi = np.nanmin(dist), np.nanmax(dist)
    r5 = lambda v: int(5 * round(v / 5)) if v >= 5 else max(1, int(round(v)))  # noqa: E731
    return f"{r5(lo)}-{r5(hi)} km" if r5(hi) - r5(lo) > 5 else f"about {r5(np.nanmean(dist))} km"


def _years(series) -> str:
    y = pd.Series(series).dropna().astype(int)
    return f"{y.min()}" if y.min() == y.max() else f"{y.min()}-{y.max()}"


def _month_list(months) -> str:
    """Month names in calendar order, starting after the longest gap so a winter
    run stays together: [1, 2, 12] -> 'Dec, Jan, Feb'."""
    ms = sorted(int(m) for m in months)
    gaps = [(ms[(i + 1) % len(ms)] - ms[i]) % 12 for i in range(len(ms))]
    start = (int(np.argmax(gaps)) + 1) % len(ms)
    return ", ".join(MONTHS[m - 1] for m in ms[start:] + ms[:start])


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _left_align_titles(fig: go.Figure, color: str, size: float = 14):
    """Left-align make_subplots panel titles over their own panels."""
    names = sorted((k for k in fig.layout if k.startswith("xaxis")), key=lambda k: int(k[5:] or 1))
    titles = [a for a in fig.layout.annotations]
    for a, k in zip(titles, names):
        a.update(x=fig.layout[k].domain[0], xanchor="left", font=dict(size=size, color=color))


def _break_gaps(df: pd.DataFrame, xcol: str, step, max_step) -> pd.DataFrame:
    """Insert an empty row wherever consecutive x values are further apart than
    ``max_step``, so Plotly breaks the line there instead of drawing across a gap."""
    df = df.sort_values(xcol).reset_index(drop=True)
    gaps = df[xcol].diff() > max_step
    if not gaps.any():
        return df
    breaks = df.loc[gaps, [xcol]].copy()
    breaks[xcol] = breaks[xcol] - step
    return pd.concat([df, breaks]).sort_values(xcol).reset_index(drop=True)


# ---------------------------------------------------------------------------
# RQ1: Groundwater levels
# ---------------------------------------------------------------------------
SITE_ORDER = ["Lincoln Middle School", "Bernalillo site", "Sandia site", "Dome Road well"]
SITE_PLACE = {
    "Lincoln Middle School": "Rio Rancho",
    "Bernalillo site": "Bernalillo",
    "Sandia site": "Sandia Pueblo area",
    "Dome Road well": "near Cochiti",
}


def _well_style(dark: bool) -> dict:
    """Wells at one site: shades of the water-level blue plus a line style, so
    two nearly identical lines can both be seen."""
    p = palette(dark)
    return {
        "Well": dict(color=p["blue"], dash="solid"),
        "Well A": dict(color=p["blue_dark"], dash="dash"),
        "Well B": dict(color=p["blue_light"], dash="solid"),
    }


def groundwater_hydrographs(dark: bool = False) -> Chart:
    p = palette(dark)
    gw = d.load_groundwater_levels()
    names = gw.drop_duplicates("site_id").set_index("site_id")
    trends = st_.well_trends(gw).join(names[["site_group", "well"]], on="site_id")
    ann = st_.annual_means(gw).join(names[["site_group", "well"]], on="site_id")
    sandia = ann[(ann["site_group"] == "Sandia site") & (ann["well"] == "Well")].set_index("year")["value"]
    peak_year = int(sandia.idxmax())
    recovery = sandia.max() - sandia.iloc[-1]
    n_fall = int((trends["trend"] == "Declining").sum())
    n_rise = int((trends["trend"] == "Rising").sum())
    n_none = int((trends["trend"] == "No clear trend").sum())
    n_wells, n_sites = gw["site_id"].nunique(), gw["site_group"].nunique()

    def _wells_text(trend: str) -> str:
        """'all 3 at Lincoln Middle School, Bernalillo site Well, ...' for one trend class."""
        parts = []
        for site in SITE_ORDER:
            t = trends[trends["site_group"] == site]
            hit = t[t["trend"] == trend]
            if hit.empty:
                continue
            if len(hit) == len(t) and len(t) > 1:
                parts.append(f"all {len(t)} at {site}")
            elif len(t) == 1:
                parts.append(site)
            else:
                parts.append(", ".join(f"{site} {w}" for w in hit["well"]))
        return "; ".join(parts)

    falling_txt, rising_txt = _wells_text("Declining"), _wells_text("Rising")

    # every panel gets the same vertical span, so slopes can be compared across panels
    rng = gw.groupby("site_group")["depth_to_water_ft"].agg(["min", "max"])
    span = float((rng["max"] - rng["min"]).max() * 1.08)

    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.15, horizontal_spacing=0.09,
                        subplot_titles=[f"{s} ({SITE_PLACE[s]})" for s in SITE_ORDER])
    styles = _well_style(dark)
    shown = set()
    for i, site in enumerate(SITE_ORDER):
        r, c = i // 2 + 1, i % 2 + 1
        for well in ["Well", "Well A", "Well B"]:
            g = gw[(gw["site_group"] == site) & (gw["well"] == well)]
            if g.empty:
                continue
            g = _break_gaps(g, "date", pd.Timedelta(days=1), pd.Timedelta(days=75))
            fig.add_trace(go.Scatter(
                x=g["date"], y=g["depth_to_water_ft"], mode="lines", name=well, legendgroup=well,
                showlegend=well not in shown, connectgaps=False,
                line=dict(color=styles[well]["color"], width=LINE_WIDTH, dash=styles[well]["dash"]),
                customdata=g[["site_name"]].fillna("").to_numpy(),
                hovertemplate="%{customdata[0]}<br>%{x|%b %Y}: <b>%{y:.1f} ft</b> below land<extra></extra>",
            ), row=r, col=c)
            shown.add(well)
        mid = (rng.loc[site, "min"] + rng.loc[site, "max"]) / 2
        fig.update_yaxes(range=[mid + span / 2, mid - span / 2], row=r, col=c, tickformat=",.0f", dtick=10)
    fig.update_yaxes(title_text="Depth to water (ft)", col=1)
    _left_align_titles(fig, p["ink2"])
    _base_layout(fig, dark, 600, hovermode="closest",
                 legend=dict(title_text="Same location, different depths:  ", y=1.13),
                 margin=dict(t=95, l=80))

    data = gw[["site_id", "site_name", "site_group", "well", "latitude", "longitude", "date", "depth_to_water_ft"]]
    title = (f"{n_fall} of {n_wells} monitored wells fell over their records and {n_rise} rose; the Sandia site "
             f"has risen {recovery:.0f} ft since {peak_year}")
    findings = [
        ("Measured", f"Full-record trends (Mann-Kendall p < 0.05): falling: {falling_txt}; rising: {rising_txt}; "
                     f"{n_none} with no clear trend."),
        ("Measured", f"At the Sandia site the water level fell until {peak_year}, then rose about {recovery:.0f} ft "
                     f"by {int(sandia.index.max())}."),
        ("Hypothesis", f"The Sandia-site recovery after {peak_year} matches the timing of the San Juan-Chama Drinking "
                       "Water Project (2008), after which the Albuquerque water utility pumped less groundwater; USGS "
                       "mapped 30-40 ft rises across the Albuquerque area by 2016 (Ritchie et al. 2019, SIM 3435). "
                       "These data alone can't show the cause."),
        ("Insufficient data", f"None of these wells are near Cuba ({_km_range(gw['latitude'], gw['longitude'])} away), "
                              "so they say nothing direct about Cuba's aquifer."),
    ]
    return Chart(
        key="groundwater_hydrographs",
        title=title,
        subtitle=(f"Monthly mean depth to water at the {n_wells} USGS monitoring wells ({n_sites} sites), "
                  f"{_years(gw['year'])}. Axis flipped: up = higher water table."),
        caption=(f"Each panel is one monitoring site. Wells marked A or B are at the same spot but measured at a "
                 f"different depth, so they are drawn separately; at Lincoln Middle School and the Sandia site, "
                 f"Well and Well A nearly coincide (Well A is dashed). Every panel spans the same {span:.0f} ft, so "
                 "steepness can be compared across panels. Lines break where months are missing. These are "
                 f"water-level indicators at {n_sites} sites, not measures of how much water is left."),
        scope=(f"{SCOPE_COUNTY}: {n_sites} sites between Rio Rancho and Cochiti, "
               f"{_km_range(gw['latitude'], gw['longitude'])} from Cuba"),
        rqs=(1, 5, 6),
        findings=findings,
        fig=fig,
        data=data,
        source=f"USGS Water Data statistics, parameter 72019, cleaned by J. Wauneka ({FILES['gw']})",
        height=600,
    )


def groundwater_trends(dark: bool = False, recent_start: int = 2016, recent_end: int = 2025) -> Chart:
    p = palette(dark)
    gw = d.load_groundwater_levels()
    names = gw.drop_duplicates("site_id").set_index("site_id")[["site_group", "well", "site_name"]]
    full = st_.well_trends(gw).join(names, on="site_id")
    full["period"] = "Full record"
    recent = st_.well_trends(gw, recent_start, recent_end).join(names, on="site_id")
    rec_label = f"{recent_start}-{recent_end}"
    recent["period"] = rec_label
    tbl = pd.concat([full, recent], ignore_index=True)
    order = {s: i for i, s in enumerate(SITE_ORDER)}
    well_o = {"Well": 0, "Well A": 1, "Well B": 2}
    full = full.assign(o=full["site_group"].map(order) * 10 + full["well"].map(well_o)).sort_values("o")
    full["row"] = full["site_group"] + " · " + full["well"]
    tbl["row"] = tbl["site_group"] + " · " + tbl["well"]
    rows = full["row"].tolist()
    row_index = {r: i for i, r in enumerate(rows)}
    ticktext = [f"{r}  <span style='color:{p['muted']}'>{int(a)}-{int(b)}</span>"
                for r, a, b in zip(full["row"], full["first_year"], full["last_year"])]

    color = {"Rising": p["rise"], "Declining": p["fall"], "No clear trend": p["muted"], "Not enough data": p["muted"]}
    offsets = {"Full record": -0.17, rec_label: 0.17}
    symbols = {"Full record": "circle", rec_label: "diamond"}
    fig = go.Figure()
    fig.add_vline(x=0, line=dict(color=p["axis"], width=1.5))
    for period in offsets:
        sub = tbl[(tbl["period"] == period) & tbl["level_slope_ft_per_yr"].notna()]
        for _, r_ in sub.iterrows():  # 95% interval whiskers
            yy = row_index[r_["row"]] + offsets[period]
            fig.add_trace(go.Scatter(x=[r_["ci_low"], r_["ci_high"]], y=[yy, yy], mode="lines",
                                     line=dict(color=color[r_["trend"]], width=1.5), hoverinfo="skip",
                                     showlegend=False))
        for trend in ["Declining", "No clear trend", "Rising"]:
            s = sub[sub["trend"] == trend]
            if s.empty:
                continue
            fig.add_trace(go.Scatter(
                x=s["level_slope_ft_per_yr"], y=s["row"].map(row_index) + offsets[period], mode="markers",
                name=f"{period}: {trend.lower()}", showlegend=False,
                marker=dict(symbol=symbols[period], size=MARKER_SIZE + 2, color=color[trend], line=_ring(dark)),
                customdata=s[["row", "first_year", "last_year", "n_years", "ci_low", "ci_high", "p_value", "trend"]].to_numpy(),
                hovertemplate=("<b>%{customdata[0]}</b><br>" + period + " (%{customdata[1]}-%{customdata[2]}, "
                               "%{customdata[3]} years)<br>Trend: <b>%{x:+.2f} ft/yr</b> (%{customdata[7]})<br>"
                               "95% interval: %{customdata[4]:+.2f} to %{customdata[5]:+.2f}<br>"
                               "Mann-Kendall p = %{customdata[6]:.3f}<extra></extra>"),
            ))
    # explain every missing recent marker
    have_recent = set(recent.dropna(subset=["level_slope_ft_per_yr"])["site_id"])
    for _, r_ in full.iterrows():
        if r_["site_id"] in have_recent:
            continue
        nrec = recent.loc[recent["site_id"] == r_["site_id"], "n_years"]
        note = (f"no data after {int(r_['last_year'])}" if nrec.empty or nrec.iloc[0] == 0
                else f"only {int(nrec.iloc[0])} recent years")
        fig.add_annotation(x=0.03, y=row_index[r_["row"]] + offsets[rec_label], text=note, showarrow=False,
                           xanchor="left", font=dict(size=11.5, color=p["muted"]))
    # legend keys: hollow shape = period, filled square = trend color
    for period in offsets:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=period,
                                 marker=dict(symbol=symbols[period] + "-open", size=MARKER_SIZE + 2,
                                             color=p["ink2"], line=dict(width=2))))
    for trend, label in [("Declining", "Falling"), ("No clear trend", "No clear trend"), ("Rising", "Rising")]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=label,
                                 marker=dict(symbol="square", size=MARKER_SIZE + 2, color=color[trend])))
    lim = np.nanmax(np.abs(tbl[["ci_low", "ci_high"]].to_numpy())) * 1.15
    fig.update_xaxes(range=[-lim, lim], title_text="Water-level trend (ft per year)", tickformat="+.1f")
    fig.update_yaxes(tickvals=list(range(len(rows))), ticktext=ticktext, range=[len(rows) - 0.4, -1.1],
                     showgrid=False)
    fig.add_annotation(x=-lim * 0.97, y=-0.85, text="◀ water table falling", showarrow=False, xanchor="left",
                       font=dict(size=12.5, color=p["ink2"]))
    fig.add_annotation(x=lim * 0.97, y=-0.85, text="water table rising ▶", showarrow=False, xanchor="right",
                       font=dict(size=12.5, color=p["ink2"]))
    _base_layout(fig, dark, 540, legend=dict(y=1.04), margin=dict(l=280, t=60))

    rec = recent.dropna(subset=["level_slope_ft_per_yr"])
    falling_recent = [s for s in SITE_ORDER if s in set(rec.loc[rec["trend"] == "Declining", "site_group"])]
    rising_recent = [s for s in SITE_ORDER if s in set(rec.loc[rec["trend"] == "Rising", "site_group"])]
    flat_recent = [s for s in SITE_ORDER if s in set(rec.loc[rec["trend"] == "No clear trend", "site_group"])]
    lincoln = full[full["site_group"] == "Lincoln Middle School"]["level_slope_ft_per_yr"]
    bern = full[(full["site_group"] == "Bernalillo site") & (full["well"] == "Well")].iloc[0]
    sandia = full[(full["site_group"] == "Sandia site") & (full["well"] == "Well")].iloc[0]
    sandia_r = rec[(rec["site_group"] == "Sandia site") & (rec["well"] == "Well")]
    title = (f"In {rec_label}, {int((rec['trend'] == 'Declining').sum())} of {len(rec)} wells were still falling "
             f"({' and '.join(falling_recent)}); only the {' and '.join(rising_recent)} wells rose")
    findings = [
        ("Measured", f"Full-record trends at Lincoln Middle School: {lincoln.min():+.2f} to {lincoln.max():+.2f} ft/yr "
                     "(water table falling)."),
        ("Measured", f"Bernalillo site main well: {bern['level_slope_ft_per_yr']:+.2f} ft/yr over the full record, "
                     f"no clear trend in {rec_label}" + (f" (also no clear trend: {', '.join(s for s in flat_recent if s != 'Bernalillo site')})" if len(flat_recent) > 1 else "") + "."),
        ("Measured", f"Sandia site well: {sandia['level_slope_ft_per_yr']:+.2f} ft/yr over the full record and "
                     f"{sandia_r['level_slope_ft_per_yr'].iloc[0]:+.2f} ft/yr in {rec_label}."),
    ]
    data = tbl[["site_id", "site_name", "period", "first_year", "last_year", "n_years", "level_slope_ft_per_yr",
                "ci_low", "ci_high", "p_value", "trend", "total_change_ft"]].round(3)
    return Chart(
        key="groundwater_trends",
        title=title,
        subtitle=(f"Sen's slope of annual mean water level per well: whole record (circles) vs {rec_label} "
                  "(diamonds); whiskers = 95% interval; gray years = each well's record"),
        caption=("Trend = Sen's slope of annual means (years with at least 9 months of data). Sen's slope assumes "
                 "one direction, so a record that fell and then rose, like the Sandia site (see the hydrographs), "
                 "gets one average slope. Color shows the "
                 "Mann-Kendall test: red = falling, blue = rising, gray = no clear trend (p ≥ 0.05). Sign is "
                 "flipped from depth so that negative = water table falling. Both the p-values and the intervals "
                 "assume each year is independent; groundwater years aren't (a low year tends to follow a low "
                 "year), so both look more certain than they are. Records differ in length (see the years by "
                 "each well)."),
        scope=(f"{SCOPE_COUNTY}: the same {gw['site_id'].nunique()} USGS wells, "
               f"{_km_range(gw['latitude'], gw['longitude'])} from Cuba"),
        rqs=(1, 6),
        findings=findings,
        fig=fig,
        data=data,
        source=f"USGS Water Data statistics, parameter 72019 ({FILES['gw']}); annual means, Sen's slope, Mann-Kendall test (analysis/stats.py)",
        height=540,
    )


def _placitas_dumbbells(fig: go.Figure, agg: pd.DataFrame, rows: list, dark: bool, e_lab: str, l_lab: str):
    """Plain version of placitas_remeasured: early-period range bar, averages, and an arrow per well."""
    p = palette(dark)
    c_old, c_new = p["blue_light"], p["blue_dark"]
    for i, (sid, r_) in enumerate(agg.iterrows()):
        fig.add_trace(go.Scatter(x=[r_["min_early"], r_["max_early"]], y=[i, i], mode="lines",
                                 line=dict(color=_rgba(p["blue"], 0.45 if dark else 0.28), width=9), hoverinfo="skip",
                                 showlegend=i == 0, name=f"Range of {e_lab} readings", legendgroup="range"))
        fig.add_annotation(x=r_["mean_late"], y=i, ax=r_["mean_early"], ay=i, xref="x", yref="y", axref="x",
                           ayref="y", showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                           arrowcolor=p["muted"], text="", standoff=7, startstandoff=7)
        direction = "deeper" if r_["change_ft"] > 0 else "shallower"
        fig.add_annotation(x=max(r_["max_early"], r_["mean_late"]), y=i, xshift=14, xanchor="left",
                           text=(f"{abs(r_['change_ft']):.1f} ft {direction}  "
                                 f"<span style='color:{p['muted']}'>n = {int(r_['count_early'])} → {int(r_['count_late'])}"
                                 f"{f'; {e_lab} range {r_.range_early:.0f} ft' if r_['count_early'] > 1 else ''}</span>"),
                           showarrow=False, font=dict(size=12.5, color=p["ink2"]))
    for per, lab, col in [("early", e_lab, c_old), ("late", l_lab, c_new)]:
        fig.add_trace(go.Scatter(
            x=agg[f"mean_{per}"], y=list(range(len(rows))), mode="markers", name=f"Average, {lab}",
            marker=dict(size=MARKER_SIZE + 3, color=col, line=_ring(dark)),
            customdata=np.column_stack([agg.index, agg[f"count_{per}"], agg[f"min_{per}"], agg[f"max_{per}"],
                                        agg["well_depth_ft"].fillna(-1)]),
            hovertemplate=("<b>%{customdata[0]}</b> (well %{customdata[4]:.0f} ft deep)<br>" + lab +
                           ": average <b>%{x:.1f} ft</b> from %{customdata[1]} reading(s)<br>"
                           "range %{customdata[2]:.1f}-%{customdata[3]:.1f} ft<extra></extra>"),
        ))
    fig.update_yaxes(tickvals=list(range(len(rows))), ticktext=rows, autorange="reversed", showgrid=False)
    fig.update_xaxes(title_text="Depth to water (ft below land surface)  →  deeper", rangemode="tozero",
                     range=[0, agg[["max_early", "mean_late"]].max().max() * 1.6])


def _placitas_wells_section(fig: go.Figure, agg: pd.DataFrame, rows: list, dark: bool, e_lab: str, l_lab: str):
    """Pictograph version of placitas_remeasured: each well as a to-scale cross-section
    (casing to the well bottom, today's water column, and the water-table symbol ▽ for
    both periods, its tip on the water level), with the early-period range beside it."""
    p = palette(dark)
    c_old, c_new = p["blue"], p["blue_dark"]   # open ▽ = older period, filled ▽ = recent (both >= 3:1 on the surface)
    half = 0.11  # casing half-width (x units; not to scale)
    bottom = float(agg["well_depth_ft"].max())
    y_top, y_bot = -bottom * 0.02, bottom * 1.07
    plot_px = 600 - 170 - 60                    # plot-area height set in placitas_remeasured
    tri = 15                                    # marker size (px)
    tip = (tri / 2) * (y_bot - y_top) / plot_px  # half a marker, in feet, so the tip sits on the level
    fill = _rgba(p["blue"], 0.38 if dark else 0.22)
    rng_col = _rgba(p["blue"], 0.6 if dark else 0.45)
    for i, (sid, r_) in enumerate(agg.iterrows()):
        wd = r_["well_depth_ft"]
        # water now: from the latest level down to the well bottom
        fig.add_shape(type="rect", x0=i - half, x1=i + half, y0=r_["mean_late"], y1=wd, line_width=0,
                      fillcolor=fill, layer="below")
        # casing walls and bottom
        fig.add_shape(type="path", path=f"M{i - half},0 L{i - half},{wd} L{i + half},{wd} L{i + half},0",
                      line=dict(color=p["ink2"], width=1.6))
        # early-period range, as a bar beside the casing
        if r_["count_early"] > 1:
            fig.add_shape(type="line", x0=i - half - 0.07, x1=i - half - 0.07, y0=r_["min_early"], y1=r_["max_early"],
                          line=dict(color=rng_col, width=7))
        # change arrow, beside the casing
        if abs(r_["change_ft"]) >= 3:
            fig.add_annotation(x=i + half + 0.09, y=r_["mean_late"], ax=i + half + 0.09, ay=r_["mean_early"], xref="x",
                               yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1.1,
                               arrowwidth=1.6, arrowcolor=p["muted"], text="")
        direction = "deeper" if r_["change_ft"] > 0 else "shallower"
        flag = "†" if "†" in rows[i] else ""
        extra = f"; {e_lab[:4]}-{e_lab[-2:]} range {r_['range_early']:.0f} ft" if r_["count_early"] > 1 else ""
        fig.add_annotation(x=i, y=0, yshift=12, yanchor="bottom", showarrow=False, align="center",
                           text=(f"<b>{sid}{flag}</b><br>{abs(r_['change_ft']):.1f} ft {direction}<br>"
                                 f"<span style='color:{p['muted']};font-size:11px'>n = {int(r_['count_early'])} → "
                                 f"{int(r_['count_late'])}{extra}</span>"),
                           font=dict(size=12.5, color=p["ink2"]))
        fig.add_annotation(x=i, y=wd, yshift=-4, yanchor="top", showarrow=False, text=f"{wd:.0f} ft",
                           font=dict(size=11, color=p["muted"]))
    # land surface
    fig.add_shape(type="line", x0=-0.6, x1=len(agg) - 0.4, y0=0, y1=0, line=dict(color=p["ink2"], width=2))
    fig.add_annotation(x=-0.6, y=0, xanchor="left", yanchor="bottom", showarrow=False, text="land surface",
                       font=dict(size=11, color=p["muted"]))
    # water-table symbols (tip on the level) with hover
    for per, lab, col, open_ in [("early", e_lab, c_old, True), ("late", l_lab, c_new, False)]:
        fig.add_trace(go.Scatter(
            x=list(range(len(agg))), y=agg[f"mean_{per}"] - tip, mode="markers", name=f"Water table, average {lab}",
            marker=dict(symbol="triangle-down-open" if open_ else "triangle-down", size=tri, color=col,
                        line=dict(width=2.5 if open_ else 1, color=col if open_ else p["surface"])),
            customdata=np.column_stack([agg.index, agg[f"count_{per}"], agg[f"min_{per}"], agg[f"max_{per}"],
                                        agg["well_depth_ft"], agg[f"mean_{per}"]]),
            hovertemplate=("<b>%{customdata[0]}</b> (well %{customdata[4]:.0f} ft deep)<br>" + lab +
                           ": average <b>%{customdata[5]:.1f} ft</b> below land from %{customdata[1]} reading(s)<br>"
                           "range %{customdata[2]:.1f}-%{customdata[3]:.1f} ft<extra></extra>"),
        ))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Range of {e_lab} readings",
                             marker=dict(symbol="line-ns-open", size=16, color=rng_col, line=dict(width=6, color=rng_col))))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Water in the well, {l_lab}",
                             marker=dict(symbol="square", size=13, color=fill)))
    fig.update_xaxes(visible=False, range=[-0.65, len(agg) - 0.35])
    fig.update_yaxes(title_text="Depth below land surface (ft)", range=[y_bot, y_top], zeroline=False)
    fig.update_layout(legend=dict(y=1.2, yanchor="bottom", x=0, traceorder="normal"))


def placitas_remeasured(dark: bool = False, pictograph: bool = True) -> Chart:
    p = palette(dark)
    nm = d.load_nmbgmr_levels().dropna(subset=["depth_to_water_ft"])
    nm["y"] = nm["date"].dt.year
    early, late = nm["y"] <= 1999, nm["y"] >= 2016
    nm["period"] = np.where(early, "early", np.where(late, "late", None))
    both = nm.groupby("site_id")["period"].nunique()
    ids = both[both == 2].index
    sub = nm[nm["site_id"].isin(ids) & nm["period"].notna()]
    e_lab, l_lab = _years(sub.loc[sub["period"] == "early", "y"]), _years(sub.loc[sub["period"] == "late", "y"])
    agg = sub.groupby(["site_id", "period"])["depth_to_water_ft"].agg(["mean", "min", "max", "count"]).unstack()
    agg.columns = [f"{a}_{b}" for a, b in agg.columns]
    agg["change_ft"] = agg["mean_late"] - agg["mean_early"]
    agg["range_early"] = agg["max_early"] - agg["min_early"]
    flagged = sub[(sub["period"] == "early") & (sub["level_status"] == "R")].groupby("site_id").size()
    agg["early_readings_flagged_R"] = flagged.reindex(agg.index).fillna(0).astype(int)
    meta = nm.drop_duplicates("site_id").set_index("site_id")[["well_depth_ft", "latitude", "longitude"]]
    agg = agg.join(meta).sort_values("change_ft")
    meth = d.load_nmbgmr_levels()
    meth = meth[meth["site_id"].isin(ids)]
    meth["late"] = meth["date"].dt.year >= 2016
    meth_e = "/".join(sorted(meth.loc[~meth["late"], "measurement_method"].dropna().unique()))
    meth_l = "/".join(sorted(meth.loc[meth["late"], "measurement_method"].dropna().unique()))
    rows = [f"{sid}{'†' if agg.loc[sid, 'early_readings_flagged_R'] > 0 else ''}" for sid in agg.index]
    gaps = (sub[sub["period"] == "early"].sort_values("date").groupby("site_id")["date"].diff().dt.days.dropna())
    typical_gap = int(round(gaps.median())) if len(gaps) else None

    fig = go.Figure()
    if pictograph:
        _placitas_wells_section(fig, agg, rows, dark, e_lab, l_lab)
    else:
        _placitas_dumbbells(fig, agg, rows, dark, e_lab, l_lab)
    if any("†" in r for r in rows):
        fig.add_annotation(x=1, y=0, xref="paper", yref="paper", xanchor="right", yanchor="bottom", showarrow=False,
                           text=f"† a {e_lab} reading was flagged R (recently pumped)",
                           yshift=-40 if pictograph else 0, font=dict(size=11.5, color=p["muted"]))
    _base_layout(fig, dark, 600 if pictograph else 400,
                 margin=dict(l=90, t=170, b=60) if pictograph else dict(l=90, t=60))

    n = len(agg)
    small = int((agg["change_ft"].abs() <= 5).sum())
    big, rec = agg.loc[agg["change_ft"].idxmax()], agg.loc[agg["change_ft"].idxmin()]
    dist = _km_range(agg["latitude"], agg["longitude"])
    title = (f"Of {n} Placitas wells measured in {e_lab} and {l_lab}, {small} changed ≤5 ft; {big.name} is "
             f"{big['change_ft']:.0f} ft deeper and {rec.name} {abs(rec['change_ft']):.0f} ft shallower (unstable baseline)")
    findings = [
        ("Measured", f"{small} of {n} re-measured wells are within 5 ft of their {e_lab} average."),
        ("Measured", f"{big.name} is {big['change_ft']:.0f} ft deeper than in {e_lab} (well {big['well_depth_ft']:.0f} ft deep; "
                     f"{int(big['count_late'])} recent reading)."),
        ("Measured", f"{rec.name} is {abs(rec['change_ft']):.0f} ft shallower, but its {e_lab} readings rose steadily by "
                     f"{rec['range_early']:.0f} ft after a first reading flagged R, so its {e_lab} average is not a "
                     "stable baseline."),
        ("Insufficient data", f"{n} wells, mostly with a single recent reading, can't establish an area-wide trend."),
    ]
    out = agg.reset_index().rename(columns={"index": "site_id"}).round(2)
    return Chart(
        key="placitas_remeasured",
        title=title,
        subtitle=((f"Each well drawn to scale: casing down to the well bottom, water standing in it now, and the water "
                   f"table (▽) in {e_lab} and {l_lab}; NMBGMR wells measured in both periods") if pictograph else
                  (f"Average depth to water per period for NMBGMR wells measured in both periods; shaded bar = range "
                   f"of the {e_lab} readings; n = readings per period")),
        caption=(f"The {e_lab} readings were taken about every {typical_gap} days (median gap), so the shaded bar shows how much a well "
                 f"varied then; a change smaller than that range may just be seasonal. † = at least one {e_lab} "
                 "reading carries LevelStatus R (in USGS coding, 'recently pumped'), which can make the water level "
                 f"read deeper than normal. The measuring method also changed between periods (code {meth_e} in "
                 f"{e_lab}, {meth_l} in {l_lab}; T is electric tape and S steel tape in USGS coding). Wells measured "
                 f"in only one period ({nm['site_id'].nunique() - n} of {nm['site_id'].nunique()}) can't show change "
                 "and are left out."
                 + (" The well drawings are cross-sections to vertical scale (casing width is not to scale); the blue "
                    f"fill is the water column above the well bottom at the {l_lab} reading, a rough guide to how much "
                    "drawdown a well can take, not a measure of the aquifer." if pictograph else "")),
        scope=f"Placitas area of Sandoval County, {dist} from Cuba (not Cuba)",
        rqs=(1, 5),
        findings=findings,
        fig=fig,
        data=out,
        source=f"NM Bureau of Geology and Mineral Resources groundwater levels ({FILES['nmbgmr']}, prepared in analysis/data.py)",
        height=600 if pictograph else 400,
    )


# ---------------------------------------------------------------------------
# RQ2: Wells and aquifer units
# ---------------------------------------------------------------------------
AREA_ANCHORS = {
    f"Cuba area (≤{CUBA_RADIUS_KM} km)": ["Cuba"],
    "Jemez Springs-San Ysidro": ["Jemez Springs", "San Ysidro"],
    "Cochiti-Peña Blanca": ["Cochiti"],
    "Placitas": ["Placitas"],
    "Bernalillo-Rio Rancho": ["Bernalillo", "Rio Rancho"],
}
AREA_RADIUS_KM = 20  # for the other towns; Cuba uses CUBA_RADIUS_KM so "Cuba area" means the same everywhere
CUBA_GROUP = f"Cuba area (≤{CUBA_RADIUS_KM} km)"


def assign_area(lat, lon) -> np.ndarray:
    """Nearest anchor town within its radius (25 km for Cuba, 20 km for the others),
    else 'Elsewhere in county'."""
    names, dists = [], []
    for area, towns in AREA_ANCHORS.items():
        radius = CUBA_RADIUS_KM if area == CUBA_GROUP else AREA_RADIUS_KM
        for t in towns:
            la, lo = d.TOWNS[t]
            dist = d.distance_km(lat, lon, la, lo)
            names.append(area)
            dists.append(np.where(dist <= radius, dist, np.inf))
    dists = np.vstack(dists)
    best = np.array(names)[dists.argmin(axis=0)]
    return np.where(np.isfinite(dists.min(axis=0)), best, "Elsewhere in county")


def _one_point_per_well(need_well_depth: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Depth to water (and well depth), one row per well, from the three record types.
    Returns (usable rows, rows excluded as impossible). With need_well_depth=False,
    wells without a recorded depth are kept too (for charts that only use the level)."""
    req = ["depth_to_water_ft", "well_depth_ft"] if need_well_depth else ["depth_to_water_ft"]
    nm = d.load_nmbgmr_levels().dropna(subset=req)
    nm1 = nm.groupby("site_id").agg(name=("site_name", "first"), well_depth_ft=("well_depth_ft", "first"),
                                     depth_to_water_ft=("depth_to_water_ft", "median"),
                                     latitude=("latitude", "first"), longitude=("longitude", "first"),
                                     year=("date", lambda s: s.dt.year.min()), n=("date", "size")).reset_index()
    nm1["name"] = nm1["name"].fillna(nm1["site_id"])
    nm1["record_type"] = "NMBGMR wells, median reading"
    nm1["note"] = nm1["n"].astype(str) + " reading(s), first " + nm1["year"].astype(str)

    at = d.load_aquifer_tests().dropna(subset=req).sort_values("date")
    at1 = at.groupby("well_key").first().reset_index().rename(columns={"site_name": "name"})
    at1["name"] = at1["name"].fillna("(unnamed well)")
    at1["record_type"] = "OSE aquifer tests, level at test"
    at1["note"] = at1["formation_short"].fillna("formation not recorded") + ", tested " + at1["year"].astype(str)

    wl = d.load_well_logs().dropna(subset=["depth_to_first_water_ft"])
    wl1 = pd.DataFrame({"name": wl["site_name"].fillna(wl["site_id"]), "well_depth_ft": wl["borehole_depth_ft"],
                        "depth_to_water_ft": wl["depth_to_first_water_ft"], "latitude": wl["latitude"],
                        "longitude": wl["longitude"], "year": wl["date"].dt.year,
                        "record_type": "OSE well logs, water first found",
                        "note": "drilled " + wl["date"].dt.year.astype(str)})
    cols = ["name", "record_type", "well_depth_ft", "depth_to_water_ft", "latitude", "longitude", "year", "note"]
    allw = pd.concat([nm1[cols], at1[cols], wl1[cols]], ignore_index=True)
    allw["water_column_ft"] = allw["well_depth_ft"] - allw["depth_to_water_ft"]
    allw["distance_from_cuba_km"] = d.distance_km(allw["latitude"], allw["longitude"])
    allw["area"] = assign_area(allw["latitude"].fillna(0), allw["longitude"].fillna(0))
    allw.loc[allw["latitude"].isna(), "area"] = "Location not mapped"
    impossible = allw["depth_to_water_ft"] > allw["well_depth_ft"] + 1  # water can't be below the well bottom
    return allw[~impossible].reset_index(drop=True), allw[impossible].reset_index(drop=True)


RECORD_STYLE = {  # record type -> (data-type color slot, symbol)
    "NMBGMR wells, median reading": ("blue", "circle"),
    "OSE aquifer tests, level at test": ("orange", "diamond"),
    "OSE well logs, water first found": ("orange", "square-open"),
}


def well_depth_vs_water(dark: bool = False, max_depth_ft: float = 1300) -> Chart:
    p = palette(dark)
    allw, bad = _one_point_per_well()
    shown = allw[allw["well_depth_ft"] <= max_depth_ft]
    off = allw[allw["well_depth_ft"] > max_depth_ft]
    flowing = allw[allw["depth_to_water_ft"] < 0]
    ymax = max(shown["depth_to_water_ft"].max(), 600) * 1.05

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, max_depth_ft], y=[0, max_depth_ft], mode="lines",
                             line=dict(color=p["axis"], width=1.5), hoverinfo="skip", showlegend=False))
    # horizontal label with a pointer, so it reads correctly at any chart width
    fig.add_annotation(x=ymax * 0.55, y=ymax * 0.55, ax=95, ay=35, text="water level at the bottom of the well",
                       showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=p["muted"], xanchor="left",
                       font=dict(size=12, color=p["muted"]))
    fig.add_annotation(x=max_depth_ft * 0.72, y=ymax * 0.22, text="more water above the well bottom ↑",
                       showarrow=False, font=dict(size=12, color=p["muted"]))
    for label, (slot, sym) in RECORD_STYLE.items():
        s = shown[shown["record_type"] == label]
        n_off = int((off["record_type"] == label).sum())
        name = f"{label} ({len(s)} shown" + (f", {n_off} off-chart)" if n_off else ")")
        fig.add_trace(go.Scatter(
            x=s["well_depth_ft"], y=s["depth_to_water_ft"], mode="markers", name=name,
            marker=dict(size=MARKER_SIZE + (1 if "open" in sym else 0), color=p[slot], symbol=sym,
                        line=dict(width=2, color=p[slot]) if "open" in sym else _ring(dark), opacity=0.9),
            customdata=s[["name", "note", "water_column_ft", "area"]].to_numpy(),
            hovertemplate=("<b>%{customdata[0]}</b> (%{customdata[3]})<br>Well depth %{x:,.0f} ft · water at %{y:,.0f} ft"
                           "<br>%{customdata[2]:,.0f} ft of water column · %{customdata[1]}<extra></extra>"),
        ))
    fig.update_xaxes(title_text="Well (or borehole) depth, ft", range=[0, max_depth_ft], tickformat=",")
    fig.update_yaxes(title_text="Depth to water (ft below land, deeper ↓)", range=[ymax, -40], tickformat=",")
    if len(off):
        fig.add_annotation(x=1, y=0, xref="paper", yref="paper", xanchor="right", yanchor="bottom",
                           text=f"{len(off)} wells deeper than {max_depth_ft:,.0f} ft are off the chart (see table)",
                           showarrow=False, font=dict(size=12, color=p["muted"]))
    _base_layout(fig, dark, 520, margin=dict(t=80), legend=dict(y=1.03))

    per = allw.groupby("record_type").agg(n=("name", "size"), median_dtw=("depth_to_water_ft", "median"))
    rhos = {k: st_.spearman(g["well_depth_ft"], g["depth_to_water_ft"]) for k, g in allw.groupby("record_type") if len(g) >= 10}
    pooled = st_.spearman(allw["well_depth_ft"], allw["depth_to_water_ft"])
    q1, q3 = allw["depth_to_water_ft"].quantile([0.25, 0.75])
    title = (f"Where water is deeper, wells are drilled deeper (ρ = {min(rhos.values()):.2f}-{max(rhos.values()):.2f} "
             f"within the {len(rhos)} larger record types), but half of {len(allw)} wells have water {q1:.0f}-{q3:.0f} ft down")
    findings = [
        ("Measured", "Median depth to water by record type: " + "; ".join(
            f"{k.split(',')[0]} {v['median_dtw']:.0f} ft (n={int(v['n'])})" for k, v in per.iterrows()) + "."),
        ("Measured", "Spearman ρ between well depth and depth to water: " + "; ".join(
            f"{k.split(',')[0]} {r:.2f}" for k, r in rhos.items()) + f" (all records pooled: {pooled:.2f}, inflated "
            "because the record types differ in depth). Record types with fewer than 10 wells aren't tested."),
        ("Measured", f"Median water column above the well bottom: {allw['water_column_ft'].median():.0f} ft. "
                     f"{len(flowing)} wells had water above land surface when tested (flowing artesian; plotted above 0)."),
        ("Insufficient data", "Only the aquifer tests record the formation; the NMBGMR and well-log files don't, so "
                              "this chart can't say which aquifer each well uses."),
    ]
    bad_txt = (f" {len(bad)} record was left out because its water level is deeper than the well itself "
               f"({bad['name'].iloc[0]}: {bad['well_depth_ft'].iloc[0]:.0f} ft well, water at "
               f"{bad['depth_to_water_ft'].iloc[0]:.0f} ft), likely a data-entry error.") if len(bad) else ""
    n_cuba = int((allw["distance_from_cuba_km"] <= CUBA_RADIUS_KM).sum())
    return Chart(
        key="well_depth_vs_water",
        title=title,
        subtitle=f"One point per well: well depth vs depth to water, from three record types, {_years(allw['year'])}",
        caption=("Points far above the diagonal have a lot of water standing above the well bottom; points near it "
                 "have little. Colors follow the project's data types (blue = water-level records, orange = well "
                 "construction and tests). The three sources measure water differently (a 1997-2019 measurement, "
                 "the level on the day of an aquifer test, the depth where water was first hit while drilling), so "
                 "treat them as context, not one comparable series." + bad_txt),
        scope=f"{SCOPE_COUNTY_ALL} (most wells are around Placitas and Cochiti; {n_cuba} within {CUBA_RADIUS_KM} km of Cuba)",
        rqs=(2,),
        findings=findings,
        fig=fig,
        data=pd.concat([allw.assign(excluded=""), bad.assign(excluded="water deeper than well")]).round(1),
        source=f"NMBGMR groundwater levels ({FILES['nmbgmr']}), NM OSE aquifer tests ({FILES['tests']}), NM OSE well logs ({FILES['logs']})",
        height=520,
    )


def depth_by_area(dark: bool = False) -> Chart:
    p = palette(dark)
    allw_all, _ = _one_point_per_well(need_well_depth=False)
    unmapped = allw_all[allw_all["area"] == "Location not mapped"]
    allw = allw_all[allw_all["area"] != "Location not mapped"].copy()
    order = (allw.groupby("area")["depth_to_water_ft"].median().sort_values().index.tolist())
    counts = allw.groupby("area").size()
    rng = np.random.default_rng(220)
    allw["y"] = allw["area"].map({a: i for i, a in enumerate(order)}) + rng.uniform(-0.2, 0.2, len(allw))
    fig = go.Figure()
    for label, (slot, sym) in RECORD_STYLE.items():
        s = allw[allw["record_type"] == label]
        fig.add_trace(go.Scatter(
            x=s["depth_to_water_ft"], y=s["y"], mode="markers", name=label,
            marker=dict(size=MARKER_SIZE, color=p[slot], symbol=sym, opacity=0.85,
                        line=dict(width=2, color=p[slot]) if "open" in sym else _ring(dark)),
            customdata=np.column_stack([s["name"], s["area"], s["well_depth_ft"].map(lambda v: f"{v:,.0f} ft" if pd.notna(v) else "not recorded"),
                                        s["note"]]),
            hovertemplate=("<b>%{customdata[0]}</b> (%{customdata[1]})<br>water at <b>%{x:,.0f} ft</b> · well depth "
                           "%{customdata[2]}<br>%{customdata[3]}<extra></extra>"),
        ))
    med = allw.groupby("area")["depth_to_water_ft"].median()
    big = [a for a in order if counts[a] >= 5]
    fig.add_trace(go.Scatter(x=[med[a] for a in big], y=[order.index(a) for a in big], mode="markers",
                             name="Median (areas with ≥5 wells)",
                             marker=dict(symbol="line-ns", size=26, line=dict(width=2.5, color=p["ink"])),
                             hovertemplate="%{text}: median %{x:.0f} ft<extra></extra>", text=big))
    ticktext = [f"{a}  <span style='color:{p['muted']}'>n={counts[a]}</span>" for a in order]
    fig.update_yaxes(tickvals=list(range(len(order))), ticktext=ticktext, autorange="reversed", showgrid=False)
    fig.update_xaxes(title_text="Depth to water (ft below land surface)  →  deeper", rangemode="tozero")
    _base_layout(fig, dark, 120 + 50 * len(order), margin=dict(l=250, t=80), legend=dict(y=1.06))

    shallow, deep = med[big].idxmin(), med[big].idxmax()
    dg = allw[allw["area"] == deep]
    n_tests_deep = int((dg["record_type"] == "OSE aquifer tests, level at test").sum())
    cuba = allw[allw["area"] == CUBA_GROUP]
    title = (f"Among recorded wells, depth to water was smallest around {shallow} (median {med[shallow]:.0f} ft) and "
             f"largest around {deep} (median {med[deep]:.0f} ft; {n_tests_deep} of {len(dg)} are aquifer tests from "
             f"{_years(dg.loc[dg['record_type'].str.startswith('OSE aquifer'), 'year'])})")
    findings = [
        ("Measured", "Median depth to water by area (areas with ≥5 wells): " + "; ".join(f"{a} {med[a]:.0f} ft" for a in big) + "."),
        ("Measured", f"Cuba area: {len(cuba)} wells with a recorded level, {cuba['depth_to_water_ft'].min():.0f}-"
                     f"{cuba['depth_to_water_ft'].max():.0f} ft to water, all recorded {_years(cuba['year'])}."),
        ("Insufficient data", "Areas mix record types and decades; differences may reflect different aquifers, "
                              "land elevations, and dates, not just place."),
    ]
    return Chart(
        key="depth_by_area",
        title=title,
        subtitle=(f"Depth to water for each well with a recorded level, {_years(allw['year'])}, grouped by the nearest town; "
                  "black tick = area median"),
        caption=(f"Areas are a simple screening grouping: each well goes to the nearest of seven towns within "
                 f"{AREA_RADIUS_KM} km ({CUBA_RADIUS_KM} km for Cuba, to match the project's Cuba area), otherwise "
                 "'Elsewhere in county'. They are not hydrogeologic regions. One point per well, including wells "
                 "without a recorded well depth; medians are shown only where an area has at least 5 wells. "
                 f"{len(unmapped)} well{'s' if len(unmapped) != 1 else ''} without a usable location "
                 f"{'are' if len(unmapped) != 1 else 'is'} left out."),
        scope=SCOPE_COUNTY_ALL,
        rqs=(2, 3),
        findings=findings,
        fig=fig,
        data=allw.drop(columns="y").round(2),
        source=f"NMBGMR groundwater levels ({FILES['nmbgmr']}), NM OSE aquifer tests ({FILES['tests']}), NM OSE well logs ({FILES['logs']})",
        height=120 + 50 * len(order),
    )


# metric -> (label, unit, log axis, what it means, tick values)
FORMATION_METRICS = {
    "transmissivity_drawdown_ft2_per_day": (
        "Transmissivity, drawdown method", "ft²/day", True,
        "Transmissivity is how easily water moves through the full thickness of the aquifer; higher means a "
        "more productive aquifer.", [0.01, 0.1, 1, 10, 100, 1000, 10000]),
    "specific_capacity_gpm_per_ft": (
        "Specific capacity", "gpm per ft of drawdown", True,
        "Specific capacity is how much a well yields per foot the water level drops while pumping; higher means a "
        "more productive well.", [0.01, 0.1, 1, 10, 100]),
    "hydraulic_conductivity_ft_per_day": (
        "Hydraulic conductivity", "ft/day", True,
        "Hydraulic conductivity is how easily water moves through the rock itself, regardless of thickness.",
        [1e-6, 1e-4, 0.01, 1, 100, 10000]),
    "depth_to_water_ft": (
        "Depth to water at test", "ft below land surface", False,
        "Depth to water is the level on the day of the test; a negative value means the well was flowing "
        "(water above land surface).", None),
    "well_depth_ft": (
        "Well depth", "ft", True, "Well depth is how deep the tested well was drilled.", [30, 100, 300, 1000, 3000, 10000]),
}
FOCUS_FORMATIONS = {"Ojo Alamo Sandstone": "ojo_alamo", "San Jose Formation": "san_jose"}


def _tick_text(v: float) -> str:
    if v >= 1000:
        return f"{v / 1000:g}k"
    return f"{v:g}"


def formation_properties(metric: str = "transmissivity_drawdown_ft2_per_day", dark: bool = False,
                         min_wells: int = 3) -> Chart:
    p = palette(dark)
    label, unit, logx, meaning, ticks = FORMATION_METRICS[metric]
    tests = d.load_aquifer_tests()
    allvals = tests.dropna(subset=[metric])
    if logx:
        allvals = allvals[allvals[metric] > 0]
    # medians are taken per well first (a well tested twice counts once), then across wells
    per_well_all = allvals.groupby("well_key")[metric].median()
    county_median = per_well_all.median()
    q25, q75 = per_well_all.quantile([0.25, 0.75])
    at = allvals.dropna(subset=["formation_short"])
    per_well = at.groupby(["formation_short", "well_key"])[metric].median().reset_index()
    stats = at.groupby("formation_short").agg(values=(metric, "size"), wells=("well_key", "nunique"))
    stats["median"] = per_well.groupby("formation_short")[metric].median()
    keep = stats[(stats["values"] >= 3) | stats.index.isin(FOCUS_FORMATIONS)].copy()
    keep["has_median"] = keep["wells"] >= min_wells
    keep = pd.concat([keep[keep["has_median"]].sort_values("median", ascending=False),
                      keep[~keep["has_median"]].sort_values("values", ascending=False)])
    rows = keep.index.tolist()
    sub = at[at["formation_short"].isin(rows)].copy()
    row_i = {f: i for i, f in enumerate(rows)}
    rng = np.random.default_rng(220)  # fixed seed: the same jitter every run
    sub["y"] = sub["formation_short"].map(row_i) + rng.uniform(-0.22, 0.22, len(sub))

    fig = go.Figure()
    fig.add_vline(x=county_median, line=dict(color=p["muted"], width=1, dash="dot"), layer="below")
    fig.add_annotation(x=np.log10(county_median) if logx else county_median, y=1, yref="paper", yanchor="bottom",
                       text=f"median of all {len(per_well_all)} tested wells: {_sig(county_median)}", showarrow=False,
                       font=dict(size=12, color=p["ink2"]))
    groups = [("Other formations", p["context"], ~sub["formation_short"].isin(FOCUS_FORMATIONS))]
    groups += [(f, p[slot], sub["formation_short"] == f) for f, slot in FOCUS_FORMATIONS.items()]
    for name, color, mask in groups:
        s = sub[mask]
        if s.empty:
            continue
        fig.add_trace(go.Scatter(
            x=s[metric], y=s["y"], mode="markers", name=name,
            marker=dict(size=MARKER_SIZE + (0 if name == "Other formations" else 2), color=color, line=_ring(dark)),
            customdata=np.column_stack([s["site_name"].fillna("(unnamed)"), s["formation_short"], s["year"],
                                        s["distance_from_cuba_km"]]),
            hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]}, tested %{customdata[2]}<br>"
                           f"{label}: " + "<b>%{x:,.3~r}</b> " + unit + "<br>%{customdata[3]:.0f} km from Cuba<extra></extra>"),
        ))
    withm = keep[keep["has_median"]]
    fig.add_trace(go.Scatter(
        x=withm["median"], y=[row_i[f] for f in withm.index], mode="markers", name=f"Median of wells (≥{min_wells} wells)",
        marker=dict(symbol="line-ns", size=26, line=dict(width=2.5, color=p["ink"])), text=withm.index,
        hovertemplate="%{text}<br>median of wells %{x:,.3~r} " + unit + "<extra></extra>",
    ))
    ticktext = [f"{f}  <span style='color:{p['muted']}'>{int(keep.loc[f, 'values'])} value"
                f"{'s' if keep.loc[f, 'values'] != 1 else ''} · {int(keep.loc[f, 'wells'])} "
                f"well{'s' if keep.loc[f, 'wells'] != 1 else ''}</span>" for f in rows]
    fig.update_yaxes(tickvals=list(range(len(rows))), ticktext=ticktext, autorange="reversed", showgrid=False)
    xaxis = dict(title_text=f"{label} ({unit})" + ("  · log scale" if logx else ""), type="log" if logx else "linear")
    if ticks:
        xaxis.update(tickvals=ticks, ticktext=[_tick_text(t) for t in ticks])
    fig.update_xaxes(**xaxis)
    _base_layout(fig, dark, 130 + 38 * len(rows), margin=dict(l=330, t=80), legend=dict(y=1.08))

    top, bottom = withm["median"].idxmax(), withm["median"].idxmin()
    short = label.split(",")[0]  # "Transmissivity, drawdown method" -> "Transmissivity" for the headline
    if logx:
        within = (sub[sub["formation_short"].isin(withm.index)].groupby("formation_short")[metric]
                  .agg(lambda v: np.log10(v.max() / v.min())))
        widest = within.idxmax()
        between = np.log10(withm["median"].max() / withm["median"].min())
        n_more = int((within > between).sum())
        if n_more:
            fold = lambda orders: f"{float(f'{10 ** orders:.2g}'):,.0f}"  # noqa: E731  (2.65 orders -> "450")
            title = (f"{short} varies widely inside formations: in {n_more} of {len(within)}, values span a wider range "
                     f"than the formation medians do ({fold(between)}-fold), up to {fold(within.max())}-fold in the {widest}")
        else:
            title = (f"{short}: formation medians span {between:.1f} orders of magnitude, from {_sig(withm['median'].min())} "
                     f"({bottom}) to {_sig(withm['median'].max())} {unit} ({top})")
    else:
        title = (f"{short}: formation medians range from {_sig(withm['median'].min())} ({bottom}) to "
                 f"{_sig(withm['median'].max())} {unit} ({top}), and values overlap widely")
    oa = per_well[per_well["formation_short"] == "Ojo Alamo Sandstone"][metric]
    if len(oa):
        oa_med = oa.median()
        inside = q25 <= oa_med <= q75
        where = "inside" if inside else ("below" if oa_med < q25 else "above")
        oa_find = ("Measured", f"Ojo Alamo: median of {len(oa)} wells {_sig(oa_med)} {unit}, {where} the middle half of "
                   f"all tested wells ({_sig(q25)}-{_sig(q75)})"
                   + (f"; with {len(oa)} wells, too few to say it differs." if len(oa) < 5 else "."))
    else:
        oa_find = ("Insufficient data", "No Ojo Alamo test recorded this measurement.")
    findings = [
        ("Measured", f"Median of all {len(per_well_all)} tested wells with a value: {_sig(county_median)} {unit} "
                     f"(middle half {_sig(q25)}-{_sig(q75)}; {len(per_well_all) - per_well['well_key'].nunique()} wells "
                     "have no recorded formation)."),
        ("Measured", f"Among formations with ≥{min_wells} tested wells, the highest median is {top} "
                     f"({_sig(withm.loc[top, 'median'])} {unit}) and the lowest is {bottom} "
                     f"({_sig(withm.loc[bottom, 'median'])} {unit})."),
        oa_find,
        ("Insufficient data", "Most formations have fewer than 10 tested wells, many tested in the 1970s; a single new "
                              "test can move a median a lot."),
    ]
    data = sub[["site_name", "formation", "formation_short", "date", metric, "latitude", "longitude",
                "distance_from_cuba_km"]].sort_values(["formation_short", metric])
    return Chart(
        key=f"formation_properties__{metric}",
        title=title,
        subtitle=(f"{label} ({unit}) from each aquifer test, by geologic formation (formations with at least 3 values, "
                  "plus the two Cuba-area formations); black tick = median of wells; dotted line = median of all wells"),
        caption=(f"{meaning} Each dot is one reported value; a well tested more than once (or reported on two rows "
                 f"for the same day) has more than one dot, so the gray label counts values and wells. Medians are "
                 f"taken per well first, so a well tested twice counts once, and are drawn only for formations with "
                 f"at least {min_wells} tested wells. Wells without a recorded formation "
                 f"({len(per_well_all) - per_well['well_key'].nunique()} of the {len(per_well_all)} wells with a value) "
                 f"count only in the all-wells median. Tests span {_years(tests['year'])}."),
        scope=SCOPE_COUNTY_ALL,
        rqs=(2, 4),
        findings=findings,
        fig=fig,
        data=data.round({metric: 6, "latitude": 5, "longitude": 5, "distance_from_cuba_km": 1}),
        source=f"NM Office of the State Engineer aquifer tests, cleaned by J. Wauneka ({FILES['tests']})",
        height=130 + 38 * len(rows),
    )


# ---------------------------------------------------------------------------
# Maps (RQ1, RQ3, RQ5)
# ---------------------------------------------------------------------------
def _circle(lat0: float, lon0: float, radius_km: float, n: int = 120):
    """Lat/lon points on a circle of radius_km around (lat0, lon0)."""
    brg = np.linspace(0, 2 * np.pi, n)
    r = radius_km / 6371.0
    la0, lo0 = np.radians(lat0), np.radians(lon0)
    la = np.arcsin(np.sin(la0) * np.cos(r) + np.cos(la0) * np.sin(r) * np.cos(brg))
    lo = lo0 + np.arctan2(np.sin(brg) * np.sin(r) * np.cos(la0), np.cos(r) - np.sin(la0) * np.sin(la))
    return np.degrees(la), np.degrees(lo)


def _map_points_traces(fig: go.Figure, pts: pd.DataFrame, dark: bool, size: int = 9):
    # water-level records drawn last, so the rarer sites sit on top of the many aquifer-test dots
    for dtype in ["Well construction and aquifer tests", "Surface-water stations", "Water-level records"]:
        s = pts[pts["data_type"] == dtype]
        if s.empty:
            continue
        fig.add_trace(go.Scattermap(
            lat=s["latitude"], lon=s["longitude"], mode="markers", name=f"{dtype} ({len(s)})",
            legendrank=DATA_TYPE_ORDER.index(dtype),
            marker=dict(size=size, color=data_type_color(dtype, dark), opacity=0.8),
            customdata=s[["name", "dataset", "first_year", "last_year", "detail", "distance_from_cuba_km"]].to_numpy(),
            hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Records: %{customdata[2]}-%{customdata[3]}"
                           "<br>%{customdata[4]}<br>%{customdata[5]:.0f} km from Cuba<extra></extra>"),
        ))


def _map_layout(fig: go.Figure, dark: bool, center: dict, zoom: float, basemap: str | None, height: int):
    p = palette(dark)
    fig.update_layout(
        template=template_name(dark), height=height,
        map=dict(style=basemap or "white-bg", center=center, zoom=zoom,
                 layers=[dict(source=d.load_county_boundary(), type="line", color=p["boundary"],
                              line=dict(width=2), below="traces")]),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, bgcolor="rgba(0,0,0,0)"),
    )


def _town_traces(fig: go.Figure, dark: bool, names: dict):
    """names: {town: textposition}. Town dots go under the data; labels are offset."""
    p = palette(dark)
    for town, pos in names.items():
        la, lo = d.TOWNS[town]
        fig.add_trace(go.Scattermap(
            lat=[la], lon=[lo], mode="markers+text", text=[town], textposition=pos,
            textfont=dict(size=14 if town == "Cuba" else 12.5, color=p["ink"]),
            marker=dict(size=10 if town == "Cuba" else 6, color=p["ink"]),
            name=town, hoverinfo="text", showlegend=False,
        ))


def county_coverage_map(dark: bool = False, basemap: str | None = None, split_lon: float = -106.75) -> Chart:
    p = palette(dark)
    pts = d.load_monitoring_points().dropna(subset=["latitude"])
    fig = go.Figure()
    pts["inside_county"] = d.in_county(pts["latitude"], pts["longitude"])
    # 25 km scale bar in the empty southwest corner of the county
    bar_lat, bar_lon0 = 35.42, -107.15
    bar_lon1 = bar_lon0 + 25 / (111.32 * np.cos(np.radians(bar_lat)))
    fig.add_trace(go.Scattermap(lat=[bar_lat, bar_lat], lon=[bar_lon0, bar_lon1], mode="lines+markers+text",
                                text=["", "25 km"], textposition="middle right", marker=dict(size=5, color=p["ink2"]),
                                line=dict(color=p["ink2"], width=2), textfont=dict(size=12, color=p["ink2"]),
                                hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scattermap(lat=[35.20, 36.23], lon=[split_lon, split_lon], mode="lines",
                                line=dict(color=p["muted"], width=1), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scattermap(lat=[36.21], lon=[split_lon], mode="markers+text", text=[f"{abs(split_lon):.2f}° W"],
                                textposition="middle right", marker=dict(size=1, opacity=0),
                                textfont=dict(size=11.5, color=p["ink2"]), hoverinfo="skip", showlegend=False))
    _map_points_traces(fig, pts, dark, size=8)
    _town_traces(fig, dark, {"Cuba": "top right", "Jemez Springs": "middle right", "San Ysidro": "middle left",
                             "Cochiti": "top left", "Bernalillo": "top center", "Placitas": "bottom right",
                             "Rio Rancho": "bottom left"})
    _map_layout(fig, dark, center=dict(lat=35.70, lon=-106.93), zoom=8.1, basemap=basemap, height=660)

    near = pts[pts["distance_from_cuba_km"] <= CUBA_RADIUS_KM]
    by_type = pts.groupby("data_type").size()
    east = (pts["longitude"] > split_lon).mean()
    near_wl = near[near["data_type"] == "Water-level records"]
    outside = int((~pts["inside_county"]).sum())
    title = (f"{east:.0%} of the {len(pts)} mapped sites are east of {abs(split_lon):.2f}° W, along the Rio Grande "
             f"side; only {len(near)} are within {CUBA_RADIUS_KM} km of Cuba, and none of those is a monitoring well "
             "in the collected data")
    findings = [
        ("Measured", f"{len(pts)} mapped sites: " + ", ".join(f"{by_type.get(t, 0)} {t.lower()}" for t in DATA_TYPE_ORDER) + "."),
        ("Measured", f"Within {CUBA_RADIUS_KM} km of Cuba: {len(near)} sites, "
                     + ("none of them water-level monitoring sites" if len(near_wl) == 0 else f"{len(near_wl)} of them water-level monitoring sites")
                     + "; they are one-time aquifer tests or well logs and the Rio Puerco stream gage."),
        ("Insufficient data", "The northwest of the county, around Cuba, has no repeated groundwater-level record in "
                              "the collected data."),
    ]
    return Chart(
        key="county_coverage_map",
        title=title,
        subtitle=(f"Every mapped site in the project's datasets ({_years([pts['first_year'].min(), pts['last_year'].max()])} "
                  "records), colored by what it "
                  "measures; outline = Sandoval County"),
        caption=("A dot is a site with any record in the collected files, not necessarily active monitoring: many are "
                 "one-time tests from decades ago (hover for record years). Water-level records = USGS monitoring "
                 "wells and NMBGMR wells; well construction and aquifer tests = OSE aquifer tests and well logs; "
                 "surface-water stations = USGS stream, canal, and reservoir sites, including Rio Puerco at Cuba. "
                 f"The thin vertical line at {abs(split_lon):.2f}° W is the east/west split used in the title. "
                 f"{outside} sites lie just outside the simplified county line but are in the downloaded county files. One OSE "
                 "well log isn't mapped because its coordinates disagree with its legal description. Town locations "
                 "are approximate; in the app, zoom in to separate the dense Rio Grande cluster."),
        scope=SCOPE_COUNTY_ALL,
        rqs=(5, 1, 3),
        findings=findings,
        fig=fig,
        data=pts.round(4),
        source=ALL_SOURCES,
        height=660,
    )


def _nearest_repeated_wl(pts: pd.DataFrame) -> pd.Series:
    wl = pts[(pts["data_type"] == "Water-level records") & (pts["n_records"] >= 2)]
    return wl.sort_values("distance_from_cuba_km").iloc[0]


# --- pictograph maps -------------------------------------------------------
# Transmissivity classes for the well pictograms: one size per class (a graduated-symbol
# map: the key gives each class's range, so sizes are read as classes, not measured).
# Diameters are km on the ground at the starting zoom; pictograms are far larger than a
# well, so their size shows the class, not an area.
T_CLASSES = [(0, 100, "under 100", 3.0), (100, 1000, "100 to under 1,000", 4.2), (1000, np.inf, "1,000 or more", 5.8)]
T_MISSING_KM = 3.0
OTHER_ICON_KM = 3.4
MAX_NUDGE_KM = 1.0
GROUP_KM = 1.0     # sites of one kind closer than this share a pictogram (with a count)
LABEL_KM = 3.3     # height of the count / formation labels on the map
RING_BANDS = (0, 10, CUBA_RADIUS_KM, 50, np.inf)  # distance rings drawn on the Cuba map


def _t_class(t: float) -> tuple[str, float]:
    if pd.isna(t):
        return "not recorded", T_MISSING_KM
    for lo, hi, label, km in T_CLASSES:
        if lo <= t < hi:
            return label, km
    return T_CLASSES[-1][2], T_CLASSES[-1][3]


def _relax(x: np.ndarray, y: np.ndarray, r: np.ndarray, iters: int = 200, max_shift: float = MAX_NUDGE_KM,
           bands=RING_BANDS) -> tuple[np.ndarray, np.ndarray]:
    """Nudge overlapping pictograms apart (positions and radii in km from Cuba), within
    limits that keep the map honest: no pictogram moves more than ``max_shift`` km from its
    true location, and none crosses a distance ring (so counts inside each ring stay right).
    Leftover overlaps are allowed; smaller pictograms are drawn on top."""
    x0, y0 = np.asarray(x, float), np.asarray(y, float)
    x, y = x0.copy(), y0.copy()
    d0 = np.hypot(x0, y0)
    edges = np.asarray(bands, float)
    band = np.searchsorted(edges, d0, side="right") - 1
    lo, hi = edges[band] + 0.3, edges[band + 1] - 0.3
    for _ in range(iters):
        dx, dy = x[None, :] - x[:, None], y[None, :] - y[:, None]
        dist = np.hypot(dx, dy) + np.eye(len(x))
        overlap = np.clip((r[:, None] + r[None, :]) - dist, 0, None)
        np.fill_diagonal(overlap, 0)
        if not overlap.any():
            break
        push = overlap / dist / 2
        x -= (dx * push).sum(axis=1) * 0.5
        y -= (dy * push).sum(axis=1) * 0.5
        # limits: stay within max_shift of the true location, and inside the true distance band
        sx, sy = x - x0, y - y0
        sh = np.hypot(sx, sy)
        k = np.where(sh > max_shift, max_shift / np.maximum(sh, 1e-9), 1.0)
        x, y = x0 + sx * k, y0 + sy * k
        dn = np.hypot(x, y)
        target = np.clip(dn, np.minimum(lo, d0), np.maximum(hi, d0))
        scale = np.where(dn > 0, target / np.maximum(dn, 1e-9), 1.0)
        x, y = x * scale, y * scale
    return x, y


def _km_xy(lat, lon):
    """Local east/north km from Cuba (fine for a map this size)."""
    lat0, lon0 = d.CUBA["latitude"], d.CUBA["longitude"]
    return ((np.asarray(lon) - lon0) * 111.320 * np.cos(np.radians(lat0)), (np.asarray(lat) - lat0) * 110.574)


def _xy_latlon(x, y):
    lat0, lon0 = d.CUBA["latitude"], d.CUBA["longitude"]
    return lat0 + np.asarray(y) / 110.574, lon0 + np.asarray(x) / (111.320 * np.cos(np.radians(lat0)))


def _geojson_line(lat, lon) -> dict:
    return {"type": "Feature", "properties": {},
            "geometry": {"type": "LineString", "coordinates": [[float(a), float(b)] for a, b in zip(lon, lat)]}}


def _pictograph_key(fig: go.Figure, dark: bool, x0: float, rows: list, top: float = 0.98, dy: float = 0.062):
    """A key drawn in paper coordinates: rows of (kind, payload). kind = 'head' (text),
    'icon' (uri, size_frac, label), or 'gap'."""
    p = palette(dark)
    y = top
    for kind, *payload in rows:
        if kind == "head":
            fig.add_annotation(x=x0, y=y, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                               text=f"<b>{payload[0]}</b>", showarrow=False, font=dict(size=12.5, color=p["ink"]))
            y -= dy * 0.85
        elif kind == "icon":
            uri, frac, label = payload
            fig.add_layout_image(source=uri, x=x0 + 0.022, y=y, xref="paper", yref="paper", sizex=frac, sizey=frac,
                                 xanchor="center", yanchor="middle", sizing="contain", layer="above")
            fig.add_annotation(x=x0 + 0.05, y=y, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                               text=label, showarrow=False, font=dict(size=12, color=p["ink2"]))
            y -= dy
        elif kind == "note":
            fig.add_annotation(x=x0, y=y, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                               text=payload[0], showarrow=False, font=dict(size=11.5, color=p["ink2"]))
            y -= dy * 0.62
        elif kind == "gap":
            y -= dy * 0.45
    return y


FORMATION_TAG = {"Ojo Alamo Sandstone": "OA", "San Jose Formation": "SJ"}


def _cuba_area_pictograms(fig: go.Figure, pts: pd.DataFrame, dark: bool, zoom: float, plot_h: int) -> tuple[list, pd.DataFrame]:
    """Pictograph layer for cuba_area_map. One pictogram per location: aquifer-test wells
    (orange, as on every chart) sized by transmissivity class and tagged OA / SJ when the
    test names one of the two Cuba-area formations; wells at the same spot share one
    pictogram with a count; well logs, water-level records, and stream gages get their own
    symbol. Returns the map image layers and the table behind them (one row per site)."""
    p = palette(dark)
    tests = d.load_aquifer_tests()
    per_well = tests.groupby("well_key").agg(formation=("formation_short", "first"),
                                             t=("transmissivity_drawdown_ft2_per_day", "median"))
    pts = pts.copy()
    is_test = pts["dataset"] == "OSE aquifer tests"
    pts["formation"] = pts["site_id"].map(per_well["formation"]).where(is_test)
    pts["transmissivity_ft2_per_day"] = pts["site_id"].map(per_well["t"]).where(is_test)
    pts["glyph"] = np.select([is_test, pts["dataset"] == "OSE well logs", pts["data_type"] == "Water-level records"],
                             ["test_well", "well_log", "water_level"], "stream")
    # sites of the same kind within GROUP_KM of each other share one pictogram (greedy, nearest to Cuba first)
    sx, sy = _km_xy(pts["latitude"], pts["longitude"])
    pts["_x"], pts["_y"] = sx, sy
    loc = pd.Series(-1, index=pts.index)
    for i in pts.sort_values("distance_from_cuba_km").index:
        if loc[i] >= 0:
            continue
        near = (loc < 0) & (pts["glyph"] == pts.at[i, "glyph"]) & \
               (np.hypot(pts["_x"] - pts.at[i, "_x"], pts["_y"] - pts.at[i, "_y"]) <= GROUP_KM)
        loc[near] = i
    pts["loc"] = loc.astype(str)

    t_txt = pts["transmissivity_ft2_per_day"].map(lambda v: f"{_sig(v)} ft²/day" if pd.notna(v) else "not recorded")
    line = np.where(is_test, pts["name"] + " (" + pts["formation"].fillna("formation not recorded") + "): " + t_txt,
                    pts["name"] + ": " + pts["detail"])
    pts["hover_line"] = line
    groups = []
    for loc, g in pts.groupby("loc", sort=False):
        glyph = g["glyph"].iloc[0]
        t_vals = g["transmissivity_ft2_per_day"].dropna()
        t_med = t_vals.median() if glyph == "test_well" and len(t_vals) else np.nan
        if glyph == "test_well":
            t_label, km = _t_class(t_med)
            color, hollow = p["orange"], pd.isna(t_med)
        else:
            t_label, km, hollow = "", OTHER_ICON_KM, False
            color = p["orange"] if glyph == "well_log" else p["blue"] if glyph == "water_level" else p["aqua"]
        forms = sorted({FORMATION_TAG[f] for f in g["formation"].dropna() if f in FORMATION_TAG})
        groups.append(dict(loc=loc, glyph=glyph, color=color, hollow=hollow, icon_km=km, t_class=t_label,
                           t_group_median=t_med, n=len(g), tag="/".join(forms),
                           latitude=g["latitude"].mean(), longitude=g["longitude"].mean(),
                           distance_from_cuba_km=g["distance_from_cuba_km"].mean(),
                           dataset=g["dataset"].iloc[0], hover="<br>".join(g["hover_line"].head(8))
                           + (f"<br>... and {len(g) - 8} more" if len(g) > 8 else "")))
    gp = pd.DataFrame(groups)
    x, y = _km_xy(gp["latitude"], gp["longitude"])
    ix, iy = _relax(x, y, gp["icon_km"].to_numpy() / 2)
    gp["icon_lat"], gp["icon_lon"] = _xy_latlon(ix, iy)
    gp["shift_km"] = np.hypot(ix - x, iy - y)

    # transparent hover targets on top of the pictograms
    fig.add_trace(go.Scattermap(
        lat=gp["icon_lat"], lon=gp["icon_lon"], mode="markers", showlegend=False,
        marker=dict(size=(gp["icon_km"] * _px_per_km(zoom)).round(), opacity=0),
        customdata=np.column_stack([gp["dataset"], gp["n"], gp["hover"], gp["distance_from_cuba_km"]]),
        hovertemplate=("<b>%{customdata[0]}</b> · %{customdata[1]} site(s) here<br>%{customdata[2]}"
                       "<br>%{customdata[3]:.1f} km from Cuba<extra></extra>"),
    ))

    layers = []
    for rk in RING_BANDS[1:-1]:
        la, lo = _circle(d.CUBA["latitude"], d.CUBA["longitude"], rk)
        layers.append(dict(sourcetype="geojson", source=_geojson_line(la, lo), type="line", color=p["muted"],
                           line=dict(width=1), below="traces"))
    for _, r in gp.sort_values("icon_km", ascending=False).iterrows():  # big first, so small ones stay visible
        layers.append(dict(sourcetype="image", below="traces",
                           source=icons.badge_png(r["glyph"], r["color"], ring=p["surface"], hollow=bool(r["hollow"])),
                           coordinates=icons.km_box(r["icon_lat"], r["icon_lon"], r["icon_km"])))
    # counts (xn) and formation tags (OA / SJ) beside the pictograms: right of the pictogram east of
    # Cuba, left of it to the west, so they point away from the town label
    for _, r in gp[(gp["n"] > 1) | (gp["tag"] != "")].iterrows():
        text = " ".join(t for t in [f"x{r['n']}" if r["n"] > 1 else "", r["tag"]] if t)
        uri, aspect = icons.label_png(text, p["ink"], p["surface"])
        w = LABEL_KM * aspect
        east = r["icon_lon"] >= d.CUBA["longitude"]
        x_left = (r["icon_km"] / 2 + 0.2) if east else -(r["icon_km"] / 2 + 0.2 + w)
        layers.append(dict(sourcetype="image", below="traces", source=uri,
                           coordinates=icons.km_rect(r["icon_lat"], r["icon_lon"], w, LABEL_KM, x_left)))

    # key, with pictograms at the size they have on the map at the starting zoom
    frac = lambda km: km * _px_per_km(zoom) / plot_h  # noqa: E731
    ring = p["surface"]
    key = [("head", "Records (one pictogram per location)"),
           ("icon", icons.badge_svg("test_well", p["orange"], ring), frac(OTHER_ICON_KM), "Aquifer-test well"),
           ("icon", icons.badge_svg("well_log", p["orange"], ring), frac(OTHER_ICON_KM), "Well log (drilling record)"),
           ("icon", icons.badge_svg("water_level", p["blue"], ring), frac(OTHER_ICON_KM), "Water-level record"),
           ("icon", icons.badge_svg("stream", p["aqua"], ring), frac(OTHER_ICON_KM), "Surface-water station"),
           ("gap",), ("head", "Aquifer-test well size = transmissivity"), ("note", "(ft²/day, median per location)")]
    key += [("icon", icons.badge_svg("test_well", p["orange"], ring), frac(km), label) for _, _, label, km in T_CLASSES]
    key += [("icon", icons.badge_svg("test_well", p["orange"], hollow=True), frac(T_MISSING_KM), "not recorded"),
            ("gap",), ("head", "Labels"),
            ("note", "OA / SJ = test names the Ojo Alamo"), ("note", "Sandstone / San Jose Formation"),
            ("note", f"xn = n wells within {GROUP_KM:.0f} km of each other")]
    _pictograph_key(fig, dark, 0.735, key, top=0.97, dy=0.058)
    out = pts.drop(columns=["hover_line", "_x", "_y"]).merge(
        gp[["loc", "n", "t_class", "t_group_median", "icon_km", "shift_km"]].rename(
            columns={"n": "sites_at_location", "t_group_median": "location_median_transmissivity"}), on="loc")
    return layers, out


def _px_per_km(zoom: float, lat: float = 36.02) -> float:
    """Screen pixels per km on the app's maps (MapLibre, 512-px tiles) at a given zoom."""
    return 512 * 2 ** zoom / (40075.017 * np.cos(np.radians(lat)))


def cuba_area_map(dark: bool = False, basemap: str | None = None, radius_km: float = 60,
                  pictograph: bool = True) -> Chart:
    p = palette(dark)
    allpts = d.load_monitoring_points().dropna(subset=["latitude"])
    pts = allpts[allpts["distance_from_cuba_km"] <= radius_km]
    fig = go.Figure()
    zoom, height = (8.38, 660) if pictograph else (7.95, 620)
    if pictograph:
        layers, table = _cuba_area_pictograms(fig, pts, dark, zoom, plot_h=height - 40)
        _town_traces(fig, dark, {"Cuba": "top left", "San Ysidro": "middle left", "Jemez Springs": "bottom right"})
        for rk in (10, CUBA_RADIUS_KM, 50):
            lab_la, lab_lo = _circle(d.CUBA["latitude"], d.CUBA["longitude"], rk, n=9)
            fig.add_trace(go.Scattermap(lat=[lab_la[1]], lon=[lab_lo[1]], mode="markers+text", text=[f"{rk} km"],
                                        marker=dict(size=1, opacity=0), textposition="top right",
                                        textfont=dict(size=12, color=p["ink2"]), hoverinfo="skip", showlegend=False))
        _map_layout(fig, dark, center=dict(lat=d.CUBA["latitude"] - 0.06, lon=d.CUBA["longitude"] + 0.0),
                    zoom=zoom, basemap=basemap, height=height)
        fig.update_layout(map_layers=list(fig.layout.map.layers) + layers, map_domain=dict(x=[0, 0.72], y=[0, 1]),
                          showlegend=False)
    else:
        _town_traces(fig, dark, {"Cuba": "top left", "San Ysidro": "middle left", "Jemez Springs": "bottom right"})
        for rk in (10, CUBA_RADIUS_KM, 50):
            la, lo = _circle(d.CUBA["latitude"], d.CUBA["longitude"], rk)
            fig.add_trace(go.Scattermap(lat=la, lon=lo, mode="lines", line=dict(color=p["muted"], width=1),
                                        hoverinfo="skip", showlegend=False))
            lab_la, lab_lo = _circle(d.CUBA["latitude"], d.CUBA["longitude"], rk, n=9)  # 45° steps
            # (markers+text with an invisible marker: plain "text" mode fails in static export)
            fig.add_trace(go.Scattermap(lat=[lab_la[3]], lon=[lab_lo[3]], mode="markers+text", text=[f"{rk} km"],
                                        marker=dict(size=1, opacity=0), textposition="bottom right",
                                        textfont=dict(size=12, color=p["ink2"]), hoverinfo="skip", showlegend=False))
        _map_points_traces(fig, pts, dark, size=11)
        _map_layout(fig, dark, center=dict(lat=d.CUBA["latitude"] - 0.05, lon=d.CUBA["longitude"] + 0.03),
                    zoom=zoom, basemap=basemap, height=height)

    inner = pts[pts["distance_from_cuba_km"] <= CUBA_RADIUS_KM]
    tests = inner[inner["dataset"] == "OSE aquifer tests"]
    t_raw = d.load_aquifer_tests()
    t_inner = t_raw[(t_raw["distance_from_cuba_km"] <= CUBA_RADIUS_KM) & t_raw["depth_to_water_ft"].notna()]
    first = t_inner.sort_values("distance_from_cuba_km").iloc[0]
    nr = _nearest_repeated_wl(allpts)
    logs = inner[inner["dataset"] == "OSE well logs"]
    gages = inner[inner["data_type"] == "Surface-water stations"]
    title = (f"Within {CUBA_RADIUS_KM} km of Cuba: {len(tests)} wells with one-time aquifer tests ({_years(tests['first_year'])}), "
             f"{len(logs)} well log{'s' if len(logs) != 1 else ''}, and {len(gages)} stream gage{'s' if len(gages) != 1 else ''}; "
             "in the collected data, no well there is measured repeatedly")
    findings = [
        ("Measured", f"{t_inner['well_key'].nunique()} of the tested wells within {CUBA_RADIUS_KM} km had a one-time depth "
                     f"to water recorded during their test ({_years(t_inner['year'])}), e.g. {first['depth_to_water_ft']:.0f} ft at "
                     f"{first['distance_from_cuba_km']:.1f} km in {int(first['year'])}. Two of the well names may be "
                     "the same well (same location and depth)."),
        ("Measured", f"The nearest well with repeated water-level measurements is {nr['distance_from_cuba_km']:.0f} km "
                     f"away ({nr['name']}, {nr['n_records']} readings in {_years([nr['first_year'], nr['last_year']])})."),
        ("Insufficient data", "Without repeated water levels near Cuba, the data can't confirm or rule out severe "
                              "decline in Cuba's aquifer (research question 3)."),
    ]
    caption = ("Most sites near Cuba are aquifer tests done once, decades ago; they give well depth, aquifer "
               "properties, and the water level on test day, not a trend. The Rio Puerco gage measures the river, "
               f"not groundwater. The {CUBA_RADIUS_KM} km 'Cuba area' radius is an analysis choice, not an official "
               "boundary. Town locations are approximate.")
    if pictograph:
        is_t = table["dataset"] == "OSE aquifer tests"
        n_t = int(table.loc[is_t, "transmissivity_ft2_per_day"].notna().sum())
        shared = table.loc[table["sites_at_location"] > 1, "loc"].nunique()
        subtitle = (f"One pictogram per location within {radius_km:.0f} km of Cuba; aquifer-test wells sized by "
                    f"transmissivity class; rings at 10, {CUBA_RADIUS_KM}, and 50 km")
        caption += (" Pictogram size is a class of transmissivity (three classes, see the key), not a proportional "
                    f"scale; {n_t} of {int(is_t.sum())} tested wells on the map have a value (median of each well's "
                    "tests; where wells share a location, the median of those wells). Transmissivity describes the "
                    "aquifer at that well on test day, not today's supply. Pictograms are drawn far larger than a well, "
                    f"so they overlap; sites of one kind within {GROUP_KM:.0f} km of each other share one pictogram with a "
                    f"count ({shared} places), and "
                    f"overlapping pictograms are nudged at most {MAX_NUDGE_KM:.0f} km and never across a distance ring. "
                    "Pictograms scale with zoom in the app.")
        tt = table[is_t & (table["distance_from_cuba_km"] <= CUBA_RADIUS_KM)].dropna(subset=["transmissivity_ft2_per_day"])
        lo_w, hi_w = tt.loc[tt["transmissivity_ft2_per_day"].idxmin()], tt.loc[tt["transmissivity_ft2_per_day"].idxmax()]
        oa = tt[tt["formation"] == "Ojo Alamo Sandstone"]["transmissivity_ft2_per_day"]
        findings.insert(1, ("Measured", f"Transmissivity was recorded at {len(tt)} of the {len(tests)} tested wells within "
                                        f"{CUBA_RADIUS_KM} km: from {_sig(lo_w['transmissivity_ft2_per_day'])} ft²/day "
                                        f"({lo_w['name']}, {lo_w['distance_from_cuba_km']:.0f} km) to "
                                        f"{_sig(hi_w['transmissivity_ft2_per_day'])} ft²/day ({hi_w['name']}, "
                                        f"{hi_w['distance_from_cuba_km']:.0f} km); the {len(oa)} Ojo Alamo wells with a value "
                                        f"measured {_sig(oa.min())}-{_sig(oa.max())} ft²/day. One-time tests, "
                                        f"{_years(tests['first_year'])}."))
        data = table.drop(columns=["loc"]).sort_values("distance_from_cuba_km").round(4)
    else:
        subtitle = f"Sites within {radius_km:.0f} km of Cuba, colored by what they measure; rings at 10, {CUBA_RADIUS_KM}, and 50 km"
        data = pts.sort_values("distance_from_cuba_km").round(4)
    return Chart(
        key="cuba_area_map",
        title=title,
        subtitle=subtitle,
        caption=caption,
        scope=f"Cuba and surroundings (within {radius_km:.0f} km)",
        rqs=(3, 5),
        findings=findings,
        fig=fig,
        data=data,
        source=ALL_SOURCES,
        height=height - 20,
    )


DATASET_GLYPH = {  # which pictogram stands for each dataset's records
    "USGS monitoring wells (monthly)": "water_level",
    "NMBGMR well measurements": "water_level",
    "OSE aquifer tests": "test_well",
    "OSE well logs": "well_log",
    "USGS surface-water statistics": "stream",
    "USGS Rio Puerco at Cuba (visits)": "stream",
}


def _nearest_pictograms(fig: go.Figure, near: pd.DataFrame, dark: bool):
    """Pictograph version of cuba_nearest_records: a thin stem to each distance with
    the dataset's pictogram at its end, and a key of the pictograms above the chart."""
    p = palette(dark)
    for i, (_, r_) in enumerate(near.iterrows()):
        col = data_type_color(r_["data_type"], dark)
        fig.add_shape(type="line", x0=0, x1=r_["distance_from_cuba_km"], y0=i, y1=i, line=dict(color=col, width=3))
        fig.add_layout_image(source=icons.badge_svg(DATASET_GLYPH.get(r_["dataset"], "stream"), col, ring=p["surface"]),
                             x=r_["distance_from_cuba_km"], y=i, xref="x", yref="y", sizex=30, sizey=0.78,
                             xanchor="center", yanchor="middle", sizing="contain", layer="above")
    # transparent hover targets on the pictograms
    fig.add_trace(go.Scatter(
        x=near["distance_from_cuba_km"], y=list(range(len(near))), mode="markers", showlegend=False,
        marker=dict(size=22, opacity=0),
        customdata=near[["dataset", "name", "first_year", "last_year", "n_records"]].to_numpy(),
        hovertemplate=("<b>%{customdata[0]}</b><br>Nearest site: %{customdata[1]}<br>%{x:.1f} km from Cuba · "
                       "records %{customdata[2]}-%{customdata[3]} (%{customdata[4]} records)<extra></extra>"),
    ))
    ring = p["surface"]
    _hkey(fig, dark, [(icons.badge_svg("water_level", p["blue"], ring), "Water-level records"),
                      (icons.badge_svg("test_well", p["orange"], ring), "Aquifer tests"),
                      (icons.badge_svg("well_log", p["orange"], ring), "Well logs"),
                      (icons.badge_svg("stream", p["aqua"], ring), "Surface water")],
          y=1.17, x0=0.01, size=0.075, spacing=0.25)
    fig.update_yaxes(tickvals=list(range(len(near))), ticktext=near["dataset"].tolist(), showgrid=False,
                     range=[-0.6, len(near) - 0.4])
    fig.update_layout(showlegend=False)


def _nearest_bars(fig: go.Figure, near: pd.DataFrame, dark: bool):
    """Plain version of cuba_nearest_records: one bar per dataset."""
    for dtype in DATA_TYPE_ORDER:
        s = near[near["data_type"] == dtype]
        if s.empty:
            continue
        fig.add_trace(go.Bar(
            x=s["distance_from_cuba_km"], y=s["dataset"], orientation="h", name=dtype, width=0.5,
            marker=dict(color=data_type_color(dtype, dark), cornerradius=4, line=dict(width=0)),
            customdata=s[["name", "first_year", "last_year", "n_records"]].to_numpy(),
            hovertemplate=("<b>%{y}</b><br>Nearest site: %{customdata[0]}<br>%{x:.1f} km from Cuba · "
                           "records %{customdata[1]}-%{customdata[2]} (%{customdata[3]} records)<extra></extra>"),
        ))


def cuba_nearest_records(dark: bool = False, pictograph: bool = True) -> Chart:
    p = palette(dark)
    pts = d.load_monitoring_points().dropna(subset=["latitude"])
    idx = pts.groupby("dataset")["distance_from_cuba_km"].idxmin()
    near = pts.loc[idx].sort_values("distance_from_cuba_km", ascending=False)
    fig = go.Figure()
    fig.add_vrect(x0=0, x1=CUBA_RADIUS_KM, fillcolor=p["grid"], opacity=0.5, line_width=0, layer="below")
    fig.add_annotation(x=CUBA_RADIUS_KM / 2, y=1, yref="paper", yanchor="bottom", text=f"Cuba area (≤{CUBA_RADIUS_KM} km)",
                       showarrow=False, font=dict(size=12, color=p["ink2"]))
    if pictograph:
        _nearest_pictograms(fig, near, dark)
    else:
        _nearest_bars(fig, near, dark)
    for i, (_, r_) in enumerate(near.iterrows()):
        km = r_["distance_from_cuba_km"]
        fig.add_annotation(x=km, y=i if pictograph else r_["dataset"], xanchor="left", xshift=22 if pictograph else 6,
                           text=f"{km:.1f} km · {_years([r_['first_year'], r_['last_year']])}" if km < 5 else
                                f"{km:.0f} km · {_years([r_['first_year'], r_['last_year']])}",
                           showarrow=False, font=dict(size=12.5, color=p["ink2"]))
    fig.update_xaxes(title_text="Distance from Cuba to the nearest site in each dataset (km)",
                     range=[-3 if pictograph else 0, near["distance_from_cuba_km"].max() * (1.26 if pictograph else 1.32)])
    if not pictograph:
        fig.update_yaxes(showgrid=False, categoryorder="array", categoryarray=near["dataset"].tolist())
    _base_layout(fig, dark, 440 if pictograph else 420, bargap=0.4, margin=dict(l=260, t=90), legend=dict(y=1.12))

    nr = _nearest_repeated_wl(pts)
    tests = near.loc[near["dataset"] == "OSE aquifer tests"].iloc[0]
    usgs = near.loc[near["dataset"] == "USGS monitoring wells (monthly)"].iloc[0]
    inner = pts[pts["distance_from_cuba_km"] <= CUBA_RADIUS_KM]
    i_tests = inner[inner["dataset"] == "OSE aquifer tests"]
    i_logs = inner[inner["dataset"] == "OSE well logs"]
    i_sw = inner[inner["data_type"] == "Surface-water stations"]
    title = (f"The nearest well with repeated water-level measurements is {nr['distance_from_cuba_km']:.0f} km from Cuba; "
             f"within {CUBA_RADIUS_KM} km there are only one-time tests at {len(i_tests)} wells "
             f"({_years(i_tests['first_year'])}), {len(i_logs)} well log{'s' if len(i_logs) != 1 else ''}, and "
             f"{len(i_sw)} stream gage{'s' if len(i_sw) != 1 else ''}")
    findings = [
        ("Measured", f"Nearest repeated water-level record: {nr['name']} ({nr['dataset']}), {nr['distance_from_cuba_km']:.0f} km, "
                     f"{nr['n_records']} readings in {_years([nr['first_year'], nr['last_year']])}; nearest USGS monitoring well: "
                     f"{usgs['distance_from_cuba_km']:.0f} km."),
        ("Measured", f"Nearest aquifer test: {tests['distance_from_cuba_km']:.1f} km ({int(tests['first_year'])}), a one-time record."),
        ("Insufficient data", "Answering research question 3 needs Cuba's municipal well records: well IDs, formation, "
                              "pumping, and water-level history."),
    ]
    return Chart(
        key="cuba_nearest_records",
        title=title,
        subtitle="For each dataset, the distance from Cuba's village center to its closest site, and that site's record years",
        caption=("Distances are straight-line from the approximate village center. A short "
                 + ("stem" if pictograph else "bar") + " only means a site is "
                 "close, not that it answers the question: the closest records are one-time aquifer tests and river "
                 "visits, neither of which tracks groundwater over time."
                 + (" Pictograms: ▽ water-table symbol = water-level records; well with a cone of depression = aquifer "
                    "test; well with a log strip = well log; waves = surface water." if pictograph else "")),
        scope="Cuba and the nearest site in each dataset",
        rqs=(3, 5),
        findings=findings,
        fig=fig,
        data=near[["dataset", "data_type", "name", "distance_from_cuba_km", "first_year", "last_year", "n_records"]].round(2),
        source=ALL_SOURCES.split("; county")[0],
        height=440 if pictograph else 420,
    )


# ---------------------------------------------------------------------------
# RQ3/RQ4: Cuba case study
# ---------------------------------------------------------------------------
M2D_TO_FT2D = 10.7639  # 1 m²/day in ft²/day
# San Jose Formation (Cuba Mesa Member) transmissivity published in Blandford et al. (2025),
# NMGS Guidebook 75, Table 1 (dataset 6, data/data6_cuba_mesa_member_of_san_jose_formation.pdf)
PUBLISHED_SJ_T = [
    ("Well SJ-2259, Lindrith area (Blandford et al. 2025, Table 1)", 9.4, 9.4),
    ("Stone et al. (1983), two tests, as compiled in Blandford et al. (2025), Table 1", 4.0, 11.0),
]


def ojo_alamo_vs_san_jose(dark: bool = False) -> Chart:
    p = palette(dark)
    at = d.load_aquifer_tests()
    sub = at[at["formation_short"].isin(FOCUS_FORMATIONS)].copy()
    metrics = [("depth_to_water_ft", "Depth to water (ft)", True, [10, 30, 100, 300, 1000]),
               ("well_depth_ft", "Well depth (ft)", False, None),
               ("transmissivity_drawdown_ft2_per_day", "Transmissivity (ft²/day)", True, [30, 50, 100, 200]),
               ("specific_capacity_gpm_per_ft", "Specific capacity (gpm/ft)", True, [0.2, 0.5, 1, 2, 5])]
    fig = make_subplots(rows=1, cols=4, shared_yaxes=True, horizontal_spacing=0.05,
                        subplot_titles=[m[1] for m in metrics])
    forms = list(FOCUS_FORMATIONS)
    yi = {f: i for i, f in enumerate(forms)}
    for c, (col, lab, logx, ticks) in enumerate(metrics, start=1):
        for f in forms:
            s = sub[(sub["formation_short"] == f) & sub[col].notna()]
            s = s.drop_duplicates(subset=["well_key", "date", col])  # a value entered twice for one test shows once
            jitter = np.linspace(-0.12, 0.12, len(s)) if len(s) > 1 else np.zeros(len(s))
            fig.add_trace(go.Scatter(
                x=s[col], y=yi[f] + jitter, mode="markers", name=f"{f} (aquifer tests)", legendgroup=f,
                showlegend=c == 1, marker=dict(size=MARKER_SIZE + 2, color=p[FOCUS_FORMATIONS[f]], line=_ring(dark)),
                customdata=np.column_stack([s["site_name"].fillna("(unnamed)"), s["year"], s["distance_from_cuba_km"]]),
                hovertemplate=("<b>%{customdata[0]}</b> (" + f + ")<br>tested %{customdata[1]}, "
                               "%{customdata[2]:.0f} km from Cuba<br>" + lab + ": <b>%{x:,.3~r}</b><extra></extra>"),
            ), row=1, col=c)
            fig.add_annotation(x=1, xref=f"x{'' if c == 1 else c} domain", y=yi[f] + 0.36, yref="y",
                               text=f"n={len(s)}", showarrow=False, xanchor="right",
                               font=dict(size=12, color=p["muted"]))
        if col == "transmissivity_drawdown_ft2_per_day":  # published San Jose values (dataset 6)
            for k, (name, lo, hi) in enumerate(PUBLISHED_SJ_T):
                y = yi["San Jose Formation"] + 0.22 + 0.1 * k
                xs = [lo * M2D_TO_FT2D, hi * M2D_TO_FT2D] if hi > lo else [lo * M2D_TO_FT2D]
                fig.add_trace(go.Scatter(
                    x=xs, y=[y] * len(xs), mode="lines+markers",
                    name="Published San Jose values (dataset 6, Table 1)", legendgroup="pub", showlegend=k == 0,
                    line=dict(color=p["san_jose"], width=2),
                    marker=dict(symbol="diamond-open", size=10, color=p["san_jose"], line=dict(width=2)),
                    hovertemplate=f"{name}<br>" + "%{x:,.0f} ft²/day<extra></extra>",
                ), row=1, col=c)
        if logx:
            fig.update_xaxes(type="log", row=1, col=c, tickvals=ticks, ticktext=[f"{t:g}" for t in ticks])
        else:
            fig.update_xaxes(rangemode="tozero", row=1, col=c)
    fig.update_yaxes(tickvals=[0, 1], ticktext=forms, range=[1.6, -0.55], showgrid=False)
    _left_align_titles(fig, p["ink2"], size=13.5)
    _base_layout(fig, dark, 340, margin=dict(l=170, t=100), legend=dict(y=1.3))

    keyed = sub[["formation_short", "well_key", "date"]].drop_duplicates()
    events = keyed.groupby("formation_short").size()
    wells = sub.groupby("formation_short")["well_key"].nunique()
    oa = sub[sub["formation_short"] == "Ojo Alamo Sandstone"].dropna(subset=["depth_to_water_ft"])
    near_oa = oa[oa["distance_from_cuba_km"] <= 5]
    far_oa = oa[oa["distance_from_cuba_km"] > 5]
    sj = sub[sub["formation_short"] == "San Jose Formation"]
    sj1 = sj.dropna(subset=["depth_to_water_ft"]).iloc[0]
    sj_t = sj["transmissivity_drawdown_ft2_per_day"].dropna()
    pub_lo = min(lo for _, lo, _ in PUBLISHED_SJ_T) * M2D_TO_FT2D
    pub_hi = max(hi for _, _, hi in PUBLISHED_SJ_T) * M2D_TO_FT2D
    # two Ojo Alamo well names share a location and depth and may be one well
    loc = sub.drop_duplicates("well_key").assign(lat=lambda t: t["latitude"].round(4), lon=lambda t: t["longitude"].round(4))
    dup_wells = int(loc.duplicated(subset=["formation_short", "lat", "lon"]).sum())
    n_wells = int(wells.sum())
    wells_txt = f"{n_wells - dup_wells}-{n_wells}" if dup_wells else f"{n_wells}"
    title = (f"Only {events.sum()} test events at {wells_txt} wells name these formations ({events['Ojo Alamo Sandstone']} "
             f"Ojo Alamo, {events['San Jose Formation']} San Jose; {_years(sub['year'])}): too few to describe either "
             "formation, let alone compare them")
    findings = [
        ("Measured", f"Ojo Alamo depth to water: {near_oa['depth_to_water_ft'].min():.0f}-{near_oa['depth_to_water_ft'].max():.0f} ft "
                     f"at the well(s) within 5 km of Cuba, and {far_oa['depth_to_water_ft'].min():.0f}-{far_oa['depth_to_water_ft'].max():.0f} ft "
                     f"at wells {far_oa['distance_from_cuba_km'].min():.0f}-{far_oa['distance_from_cuba_km'].max():.0f} km away."),
        ("Measured", f"San Jose: one test at one well ({sj1['site_name']}, {sj1['distance_from_cuba_km']:.0f} km from Cuba, "
                     f"{int(sj1['year'])}): {sj1['depth_to_water_ft']:.0f} ft to water, {sj1['well_depth_ft']:.0f} ft deep, "
                     f"{sj_t.iloc[0]:.0f} ft²/day. That is close to the one published Cuba Mesa Member value near "
                     f"Lindrith ({PUBLISHED_SJ_T[0][1] * M2D_TO_FT2D:.0f} ft²/day at well SJ-2259, estimated from specific "
                     f"capacity) and inside the San Jose range from Stone et al. (1983), {pub_lo:.0f}-{pub_hi:.0f} ft²/day."),
        ("Insufficient data", "Comparing the formations needs more (and recent) tests, plus the Ojo Alamo thickness and "
                              "extent maps in USGS HA-720-B (dataset 5), which is a scanned map plate not yet digitized."),
    ]
    data = sub[["site_name", "formation_short", "date", "latitude", "longitude", "distance_from_cuba_km",
                "well_depth_ft", "depth_to_water_ft", "transmissivity_drawdown_ft2_per_day",
                "transmissivity_recovery_ft2_per_day", "specific_capacity_gpm_per_ft", "storativity"]]
    return Chart(
        key="ojo_alamo_vs_san_jose",
        title=title,
        subtitle=("Every aquifer test recorded in the Ojo Alamo Sandstone or San Jose Formation (one dot per reported "
                  "value), with published San Jose transmissivity for comparison"),
        caption=("A test event is one well on one date; some events are reported on two rows (e.g. separate drawdown "
                 "results), so n counts values. Two Ojo Alamo well names, 'Cuba Independent Rural School Well No 1' "
                 "and '21.1W.28.143', share a location and depth and may be the same well. Open violet diamonds are "
                 "published San Jose Formation transmissivity compiled in Blandford et al. (2025, Table 1): well SJ-2259, "
                 "screened in the Cuba Mesa Member near Lindrith (estimated from specific capacity, assuming 70% well "
                 "efficiency), and a range from two tests in Stone et al. (1983), location not given; both converted "
                 "from m²/day. A value entered twice for the same test is drawn once. Depth to water and the two right panels use log "
                 "scales. Blank panels mean the value wasn't recorded. The tests date from "
                 f"{_years(sub['year'])} and don't show which formation Cuba's municipal wells use today."),
        scope=f"{SCOPE_COUNTY_ALL}: tests {_km_range(sub['latitude'], sub['longitude'])} from Cuba; published values from the San Juan Basin",
        rqs=(4, 2),
        findings=findings,
        fig=fig,
        data=data.round({"latitude": 5, "longitude": 5, "distance_from_cuba_km": 1}),
        source=(f"NM OSE aquifer tests ({FILES['tests']}); published values: Blandford et al. (2025), NMGS Guidebook 75, "
                "Table 1 (data/data6_cuba_mesa_member_of_san_jose_formation.pdf)"),
        height=340,
    )


# USGS HA-720-B (dataset 5) is a scanned map plate, so it can't be charted as data.
# This shows a crop of its Figure 5 around Cuba, with Cuba's own label on the plate.
# The crop (analysis/assets/ha720b_fig5_cuba_area.jpg) was cut from
# data/data5_ojo_alamo_sandstone_pub.pdf at 200 dpi (pdftoppm -r 200 -x 7000 -y 1300
# -W 1500 -H 1150), then scaled to 1200 x 920 px. USGS publications are public domain.
PLATE_IMAGE = d.ROOT / "analysis" / "assets" / "ha720b_fig5_cuba_area.jpg"
PLATE_POINTS = {  # pixel positions on the crop, read off the image
    "cuba_label": (694, 488),   # just below-right of the map's "Cuba" label, so the label stays visible
    "outcrop": (530, 536),
    "contour_3000": (612, 274),
    "contour_1000": (465, 480),
    "lat_36": (940, 490),
}


def ojo_alamo_depth_map(dark: bool = False) -> Chart:
    import base64

    p = palette(dark)
    w, h = 1200, 920
    src = "data:image/jpeg;base64," + base64.b64encode(PLATE_IMAGE.read_bytes()).decode("ascii")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, w], y=[0, h], mode="markers", marker=dict(opacity=0), hoverinfo="skip",
                             showlegend=False))
    fig.add_layout_image(dict(source=src, xref="x", yref="y", x=0, y=0, sizex=w, sizey=h, sizing="stretch",
                              layer="below", xanchor="left", yanchor="top"))
    box = dict(bgcolor="rgba(255,255,255,0.92)", bordercolor="#52514e", borderwidth=1, borderpad=4,
               font=dict(size=13, color="#0b0b0b"), arrowcolor="#0b0b0b", arrowwidth=1.6, arrowhead=2,
               axref="x", ayref="y")
    notes = [
        ("cuba_label", (900, 660), "<b>Cuba</b> (labeled on the USGS map)"),
        ("outcrop", (300, 690), "Ojo Alamo Sandstone at the surface<br>(brown = outcrop)"),
        ("contour_3000", (250, 120), "Red lines: depth to the top of the<br>sandstone, every 500 ft (3,000 ft here)"),
    ]
    for key, (tx, ty), text in notes:
        x, y = PLATE_POINTS[key]
        fig.add_annotation(x=x, y=y, ax=tx, ay=ty, text=text, showarrow=True, align="left", **box)
    fig.update_xaxes(visible=False, range=[0, w])
    fig.update_yaxes(visible=False, range=[h, 0], scaleanchor="x", scaleratio=1)
    _base_layout(fig, dark, 700, margin=dict(l=10, r=10, t=10, b=10))

    data = pd.DataFrame([
        {"item": "Publication", "value": "Thorn, Levings, Craigg, Dam, and Kernodle (1990), Hydrogeology of the Ojo Alamo "
                                          "Sandstone in the San Juan Structural Basin, USGS Hydrologic Investigations Atlas HA-720-B"},
        {"item": "Figure", "value": "Figure 5, Approximate depth to the top of the Ojo Alamo Sandstone (crop around Cuba)"},
        {"item": "Map scale", "value": "1:1,000,000"},
        {"item": "Contour interval", "value": "500 ft; datum is land surface"},
        {"item": "File", "value": "data/data5_ojo_alamo_sandstone_pub.pdf (crop: analysis/assets/ha720b_fig5_cuba_area.jpg)"},
    ])
    findings = [
        ("Measured", "On the USGS map, Cuba sits at the southeastern end of the Ojo Alamo outcrop band, where the top of "
                     "the sandstone is shallow; it deepens northward along the basin's eastern edge, past the 1,000-ft "
                     "and 3,000-ft lines (read from the published map)."),
        ("Hypothesis", "Because the Ojo Alamo is shallow at Cuba, shallow wells there can reach it, as the 148-ft Cuba "
                       "school well did in 1957; whether Cuba's municipal wells use it today isn't established."),
        ("Insufficient data", "This is a 1990 regional interpretation at 1:1,000,000 scale, read by eye; it doesn't show "
                              "current water levels, how much water the formation holds, or which formation Cuba's wells use."),
    ]
    return Chart(
        key="ojo_alamo_depth_map",
        title=("On the 1990 USGS map, Cuba sits at the southeastern end of the Ojo Alamo outcrop, where the sandstone "
               "is shallow; its top deepens northward past 1,000 and 3,000 ft"),
        subtitle="Crop of USGS Hydrologic Atlas HA-720-B, Figure 5 (approximate depth to the top of the Ojo Alamo Sandstone), with labels added",
        caption=("The map itself is unchanged; only the white labels and arrows are added. Brown is where the Ojo Alamo "
                 "Sandstone crops out at the surface; each red line joins points where its top is the same depth below "
                 "land surface, every 500 ft. 'Cuba' is the map's own town label. Dataset 5 is a scanned plate, so "
                 "values are read by eye and nothing here is digitized."),
        scope="Cuba area and the eastern San Juan Basin (regional map, 1990)",
        rqs=(4, 2, 3),
        findings=findings,
        fig=fig,
        data=data,
        source=("USGS Hydrologic Investigations Atlas HA-720-B (Thorn et al. 1990), Figure 5 "
                "(data/data5_ojo_alamo_sandstone_pub.pdf); public domain"),
        height=700,
    )


def _hkey(fig: go.Figure, dark: bool, items: list, y: float = 1.13, x0: float = 0.0, size: float = 0.085,
          spacing: float = 0.33):
    """A one-row key above a chart: [(icon uri, label), ...] in paper coordinates."""
    p = palette(dark)
    for k, (uri, label) in enumerate(items):
        x = x0 + k * spacing
        # the box is centered on x; "contain" keeps the icon square and centered in it
        fig.add_layout_image(source=uri, x=x, y=y, xref="paper", yref="paper", sizex=size, sizey=size,
                             xanchor="center", yanchor="middle", sizing="contain", layer="above")
        fig.add_annotation(x=x + 0.022, y=y, xref="paper", yref="paper", xanchor="left", yanchor="middle",
                           text=label, showarrow=False, font=dict(size=14, color=p["ink"]))


def _rio_puerco_pictograms(fig: go.Figure, rp: pd.DataFrame, dark: bool):
    """Pictograph version of rio_puerco_visits: a drop per visit (filled = flow measured,
    outline = no measurable flow); the right panel stacks one drop per visit by month."""
    p = palette(dark)
    full, empty = icons.glyph_svg("drop", p["aqua"]), icons.glyph_svg("drop", p["ink2"], hollow=True)
    top = max(rp["discharge_cfs"].max() * 1.25, 5)
    h = top * 0.115                           # drop height in ft³/s units (left panel)
    for _, r_ in rp.iterrows():
        yv = r_["discharge_cfs"] if r_["flowing"] else 0.0
        # the drop's round body (62% down the glyph) sits on the measured value
        fig.add_layout_image(source=full if r_["flowing"] else empty, x=r_["date"], y=yv + 0.62 * h, xref="x",
                             yref="y", sizex=900 * 86400000, sizey=h, xanchor="center", yanchor="top",
                             sizing="contain", layer="above")
        below = r_["textpos"] == "bottom center"
        fig.add_annotation(x=r_["date"], y=yv, xref="x", yref="y", text=r_["mon"], showarrow=False,
                           yshift=-24 if below else 24, font=dict(size=12, color=p["ink2"]))
    # right panel: one drop per visit, stacked by month
    rp = rp.sort_values("date")
    k = rp.groupby("month").cumcount()
    for (_, r_), level in zip(rp.iterrows(), k):
        fig.add_layout_image(source=full if r_["flowing"] else empty, x=r_["month"], y=level + 1, xref="x2", yref="y2",
                             sizex=0.95, sizey=0.82, xanchor="center", yanchor="middle", sizing="contain", layer="above")
    fig.update_yaxes(title_text="Visits", range=[0.3, max(k.max() + 1, 3) + 0.7], tickvals=list(range(1, int(k.max()) + 2)),
                     showgrid=False, row=1, col=2)
    return rp.assign(stack=k + 1)


def rio_puerco_visits(dark: bool = False, pictograph: bool = True) -> Chart:
    p = palette(dark)
    rp = d.load_rio_puerco()
    rp["month"] = rp["date"].dt.month
    rp["mon"] = rp["date"].dt.strftime("%b")
    # alternate labels above/below when two no-flow visits are close in time, so labels don't touch
    pos = []
    for i, r_ in rp.iterrows():
        close = i > 0 and (r_["date"] - rp.loc[i - 1, "date"]).days < 150 and not rp.loc[i - 1, "flowing"]
        pos.append("bottom center" if (close and not r_["flowing"] and pos[-1] == "top center") else "top center")
    rp["textpos"] = pos
    flow, dry = rp[rp["flowing"]], rp[~rp["flowing"]]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=not pictograph, column_widths=[0.7, 0.3],
                        horizontal_spacing=0.09 if pictograph else 0.04,
                        subplot_titles=["By visit date", "By month of year (1 drop = 1 visit)"
                                        if pictograph else "Same visits by month of year"])
    styles = {
        True: dict(name=f"Flow measured ({len(flow)} visits)",
                   marker=dict(size=MARKER_SIZE + 3, color=p["aqua"], line=_ring(dark))),
        False: dict(name=f"No measurable flow ({len(dry)} visits)",
                    marker=dict(size=MARKER_SIZE + 2, color=p["surface"], line=dict(width=2.5, color=p["ink2"]))),
    }
    if pictograph:
        _rio_puerco_pictograms(fig, rp, dark)
        _hkey(fig, dark, [(icons.glyph_svg("drop", p["aqua"]), f"Flow measured ({len(flow)} visits)"),
                          (icons.glyph_svg("drop", p["ink2"], hollow=True), f"No measurable flow ({len(dry)} visits)")],
              y=1.2, x0=0.012, size=0.09, spacing=0.3)
    for flowing, s in [(True, flow), (False, dry)]:
        hov = ("%{customdata[0]}: <b>%{y:.1f} ft³/s</b><br>gage height %{customdata[1]} ft · %{customdata[2]}<extra></extra>"
               if flowing else "%{customdata[0]}: <b>no measurable flow</b> at the gage<extra></extra>")
        cd = np.column_stack([s["date"].dt.strftime("%d %b %Y"),
                              s["gage_height_ft"].map(lambda v: f"{v:.2f}" if pd.notna(v) else "n/a"),
                              s["measurement_type"].replace({"Other": "Observed (no measurable flow)"})])
        if pictograph:  # transparent hover targets on the pictograms
            hide = dict(opacity=0, size=18)
            fig.add_trace(go.Scatter(x=s["date"], y=s["discharge_cfs"], mode="markers", showlegend=False, customdata=cd,
                                     hovertemplate=hov, marker=hide), row=1, col=1)
            allk = rp.sort_values("date").groupby("month").cumcount() + 1
            fig.add_trace(go.Scatter(x=s["month"], y=allk.reindex(s.index), mode="markers", showlegend=False,
                                     customdata=cd, hovertemplate=hov, marker=hide), row=1, col=2)
            continue
        fig.add_trace(go.Scatter(x=s["date"], y=s["discharge_cfs"], mode="markers+text", text=s["mon"],
                                 textposition=s["textpos"].tolist(), textfont=dict(size=12, color=p["ink2"]),
                                 legendgroup=str(flowing), customdata=cd, hovertemplate=hov, **styles[flowing]),
                      row=1, col=1)
        # visits in the same month are spread sideways (x is a month category, so flow values stay exact)
        k = s.groupby("month").cumcount()
        n_in_month = s.groupby("month")["month"].transform("size")
        xm = s["month"] + (k - (n_in_month - 1) / 2) * 0.28
        fig.add_trace(go.Scatter(x=xm, y=s["discharge_cfs"], mode="markers", showlegend=False,
                                 legendgroup=str(flowing), customdata=cd, hovertemplate=hov,
                                 marker=styles[flowing]["marker"]), row=1, col=2)
    top = max(rp["discharge_cfs"].max() * 1.25, 5)
    fig.update_yaxes(title_text="Streamflow (ft³/s)", range=[-4, top], row=1, col=1)
    for c in ((1,) if pictograph else (1, 2)):
        fig.add_hline(y=0, line=dict(color=p["axis"], width=1), row=1, col=c)
    fig.update_xaxes(range=[f"{rp['date'].dt.year.min()}-01-01", f"{rp['date'].dt.year.max()}-12-31"], dtick="M12",
                     tickformat="%Y", row=1, col=1)
    fig.update_xaxes(range=[0.5, 12.5], tickvals=list(range(1, 13)), ticktext=[m[0] for m in MONTHS], row=1, col=2)
    _left_align_titles(fig, p["ink2"], size=13.5)
    _base_layout(fig, dark, 440 if pictograph else 420, margin=dict(t=110 if pictograph else 90),
                 legend=dict(y=1.14), showlegend=not pictograph)

    fm = sorted(flow["month"].unique())
    dm = sorted(dry["month"].unique())
    after = [m for m in dm if m > fm[-1]]
    before = [m for m in dm if m < fm[0]]
    title = (f"Rio Puerco at Cuba had measurable flow on all {len(flow)} visits in {MONTHS[fm[0] - 1]}-{MONTHS[fm[-1] - 1]} "
             f"and on none of the {len(dry)} visits from {MONTHS[min(after) - 1]} to {MONTHS[max(before) - 1]}")
    findings = [
        ("Measured", f"{len(dry)} of {len(rp)} visits ({_years(rp['date'].dt.year)}) found no measurable flow; flowing visits "
                     f"measured {flow['discharge_cfs'].min():.2f}-{flow['discharge_cfs'].max():.1f} ft³/s, all in "
                     f"{' or '.join(MONTHS[m - 1] for m in fm)}."),
        ("Hypothesis", "Flow at Cuba may depend mostly on spring snowmelt from the mountains upstream; ten visits are "
                       "consistent with that but can't prove it."),
        ("Insufficient data", "Spot visits can't show how many days a year the river has no flow, or any long-term trend."),
    ]
    return Chart(
        key="rio_puerco_visits",
        title=title,
        subtitle=(f"Each {'drop' if pictograph else 'dot'} is one USGS field visit to station 08332525 "
                  f"({_years(rp['date'].dt.year)}); left by date (labeled with the month), right by month of year; "
                  "not a continuous record"),
        caption=("No line is drawn between visits because the river was not measured in between. 'No measurable flow' "
                 "is what the visit recorded at that moment (the channel may still hold pools), not that the river "
                 "was dry all season. This station measures the river at Cuba, not Cuba's groundwater or water supply."),
        scope=f"{SCOPE_CUBA}, surface water only (gage {d.distance_km(rp['latitude'].iloc[0], rp['longitude'].iloc[0]):.1f} km from the village center)",
        rqs=(3, 5, 6),
        findings=findings,
        fig=fig,
        data=rp.drop(columns=["mon", "textpos"]),
        source=f"USGS station 08332525, Rio Puerco at Cuba, NM ({FILES['rio_puerco']})",
        height=440 if pictograph else 420,
    )


def cuba_key_numbers() -> dict:
    """Headline numbers for the Cuba page, computed from the data."""
    pts = d.load_monitoring_points().dropna(subset=["latitude"])
    nr = _nearest_repeated_wl(pts)
    inner = pts[pts["distance_from_cuba_km"] <= CUBA_RADIUS_KM]
    tests = inner[inner["dataset"] == "OSE aquifer tests"]
    rp = d.load_rio_puerco()
    return {
        "nearest_water_level_km": float(nr["distance_from_cuba_km"]),
        "nearest_water_level_last_year": int(nr["last_year"]),
        "nearest_water_level_name": nr["name"],
        "nearest_water_level_n": int(nr["n_records"]),
        "aquifer_test_wells_in_area": int(len(tests)),
        "aquifer_test_years": _years(tests["first_year"]),
        "rio_puerco_visits": int(len(rp)),
        "rio_puerco_flowing": int(rp["flowing"].sum()),
        "rio_puerco_years": _years(rp["date"].dt.year),
        "radius_km": CUBA_RADIUS_KM,
    }


# ---------------------------------------------------------------------------
# Out of scope since the research questions were narrowed (water quality)
# ---------------------------------------------------------------------------
def rio_grande_quality(dark: bool = False, site: str = "RIO GRANDE BELOW COCHITI DAM, NM") -> Chart:
    """Out of scope: answers the dropped question on water quality. Not in the app, docs, or report."""
    p = palette(dark)
    params = [("00095", "Specific conductance (µS/cm)"), ("00400", "pH (monthly median)")]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        subplot_titles=[lab for _, lab in params])
    frames = []
    for i, (code, lab) in enumerate(params, start=1):
        s = d.load_usgs_stats(code, "month")
        s = s[s["site_name"] == site]
        frames.append(s.assign(parameter=lab))
        g = _break_gaps(s, "date", pd.Timedelta(days=1), pd.Timedelta(days=45))
        fig.add_trace(go.Scatter(
            x=g["date"], y=g["value"], mode="lines+markers", name=lab, showlegend=False,
            line=dict(color=p["aqua"], width=1.6), marker=dict(size=3.5, color=p["aqua"]),
            hovertemplate="%{x|%b %Y}: <b>%{y:,.1f}</b><extra>" + lab + "</extra>",
        ), row=i, col=1)
    _left_align_titles(fig, p["ink2"], size=13.5)
    fig.add_annotation(x=1, y=1, xref="x domain", yref="y domain", xanchor="right", yanchor="bottom", showarrow=False,
                       text="for scale: EPA taste guideline ≈ 700-900 µS/cm, far above this axis",
                       font=dict(size=11.5, color=p["muted"]))
    fig.update_yaxes(tickformat=".1f", row=2, col=1)
    _base_layout(fig, dark, 480, hovermode="x unified", margin=dict(t=50))
    q = pd.concat(frames, ignore_index=True)
    others = pd.concat([d.load_usgs_stats(c, "month") for c in ("00095", "00400", "00300", "63680")])
    others = others[others["site_name"] != site]

    sc = q[q["parameter"].str.startswith("Specific")]
    ph = q[q["parameter"].str.startswith("pH")]
    ann = sc.assign(year=sc["date"].dt.year).groupby("year")["value"].agg(["mean", "count"])
    ann = ann[ann["count"] >= 9]
    sen = st_.sen_slope(ann.index, ann["mean"])
    mk = st_.mann_kendall(ann["mean"])
    sul = others[others["site_name"].str.startswith("SULPHUR")]
    sul_sc, sul_ph = sul[sul["parameter"] == "Specific conductance"], sul[sul["parameter"] == "pH"]
    title = (f"The Rio Grande below Cochiti Dam stays fresh: in 90% of months, specific conductance was "
             f"{sc['value'].quantile(.05):.0f}-{sc['value'].quantile(.95):.0f} µS/cm ({_years(sc['date'].dt.year)}) "
             f"and pH {ph['value'].quantile(.05):.1f}-{ph['value'].quantile(.95):.1f} ({_years(ph['date'].dt.year)})")
    findings = [
        ("Measured", f"Monthly specific conductance (a salinity indicator): median {sc['value'].median():.0f} µS/cm; "
                     f"annual-mean trend {sen['slope']:+.1f} µS/cm per year (Mann-Kendall p = {mk['p']:.2f}, no clear trend)."),
        ("Measured", f"Sulphur Creek in the Jemez Mountains, sampled only in {sul_sc['date'].min():%b %Y}-"
                     f"{sul_sc['date'].max():%b %Y}: {sul_sc['value'].min():,.0f}-{sul_sc['value'].max():,.0f} µS/cm "
                     f"and pH {sul_ph['value'].min():.1f}-{sul_ph['value'].max():.1f} (very acidic)."),
        ("Hypothesis", "Sulphur Creek's acidity and salinity likely come from the volcanic and geothermal ground it "
                       "drains, not from human use; the data don't show the source."),
        ("Insufficient data", "No groundwater-quality or salinity data were collected, and nothing on water quality near "
                              "Cuba (research question 5 needs the NMBGMR brackish-water data)."),
    ]
    table = pd.concat([q, d.load_usgs_stats("00300", "month").query("site_name == @site"),
                       d.load_usgs_stats("63680", "month").query("site_name == @site"), others])
    return Chart(
        key="rio_grande_quality",
        title=title,
        subtitle=(f"Monthly values at USGS 08317400, Rio Grande below Cochiti Dam, {_years(q['date'].dt.year)} (the only "
                  "long water-quality record in the data)"),
        caption=("These are river measurements, not groundwater. Specific conductance rises with dissolved salts; for "
                 "scale, the US EPA's secondary (taste) guideline of 500 mg/L total dissolved solids corresponds to "
                 "roughly 700-900 µS/cm. Lines break at months without data. Dissolved oxygen, turbidity, and the few "
                 "months from other sites (Sulphur Creek, Jemez River near Jemez) are in the data table."),
        scope=f"{SCOPE_COUNTY}: Rio Grande at Cochiti, about {d.distance_km(sc['latitude'].iloc[0], sc['longitude'].iloc[0]):.0f} km from Cuba",
        rqs=(),  # answered a question the team dropped (see OUT_OF_SCOPE_CHARTS)
        findings=findings,
        fig=fig,
        data=table[["site_id", "site_name", "date", "parameter", "unit", "value", "sample_count"]],
        source=("USGS Water Data statistics, parameters 00095 and 00400 (also 00300, 63680 in the table), monthly "
                f"({FILES['usgs']}, prepared in analysis/data.py)"),
        height=480,
    )


# ---------------------------------------------------------------------------
# Out of scope since the research questions were narrowed (canals, groundwater-river links)
# ---------------------------------------------------------------------------
def canal_seasonal(dark: bool = False, since: int = 2000) -> Chart:
    """Out of scope: answers the dropped question on acequias and canals. Not in the app, docs, or report."""
    p = palette(dark)
    q = d.load_usgs_stats("00060", "month")
    q = q[(q["site_type"] == "Canal") & (q["date"].dt.year >= since)].copy()
    q["month"] = q["date"].dt.month
    q["canal"] = q["site_name"].map(d.tidy_site_name).str.replace(" at Cochiti, NM", "", regex=False)
    stats = q.groupby(["canal", "month"])["value"].describe(percentiles=[0.25, 0.5, 0.75]).reset_index()
    canals = sorted(stats["canal"].unique())
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.05, subplot_titles=canals)
    col = p["aqua"]
    for c, canal in enumerate(canals, start=1):
        s = stats[stats["canal"] == canal].set_index("month").reindex(range(1, 13)).reset_index()
        fig.add_trace(go.Scatter(x=s["month"], y=s["75%"], mode="lines", line=dict(width=0), hoverinfo="skip",
                                 showlegend=False), row=1, col=c)
        fig.add_trace(go.Scatter(x=s["month"], y=s["25%"], mode="lines", line=dict(width=0), fill="tonexty",
                                 fillcolor=_rgba(col, 0.16), hoverinfo="skip", showlegend=False), row=1, col=c)
        fig.add_trace(go.Scatter(
            x=s["month"], y=s["50%"], mode="lines+markers", name=canal, showlegend=False,
            line=dict(color=col, width=LINE_WIDTH), marker=dict(size=MARKER_SIZE - 1, color=col, line=_ring(dark)),
            customdata=np.column_stack([s["25%"], s["75%"], s["count"], MONTHS]),
            hovertemplate=(canal + "<br>%{customdata[3]}: median <b>%{y:.0f} ft³/s</b><br>middle half of years: "
                           "%{customdata[0]:.0f}-%{customdata[1]:.0f} ft³/s (%{customdata[2]:.0f} years)<extra></extra>"),
        ), row=1, col=c)
        ticktext = [f"{m}<br><span style='font-size:10.5px;color:{p['muted']}'>{int(n) if pd.notna(n) else 0}</span>"
                    for m, n in zip([x[0] for x in MONTHS], s["count"])]
        fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=ticktext, range=[0.5, 12.5], row=1, col=c)
    fig.update_yaxes(title_text="Monthly mean flow (ft³/s)", rangemode="tozero", col=1)
    _left_align_titles(fig, p["ink2"], size=13.5)
    _base_layout(fig, dark, 400, margin=dict(t=50, b=70))

    first_year, last_year = int(q["date"].dt.year.min()), int(q["date"].dt.year.max())
    on = stats[stats["50%"] > 0]
    off_months = sorted(set(range(1, 13)) - set(on["month"]))
    peak = stats.loc[stats["50%"].idxmax()]
    winter_n = stats[stats["month"].isin(off_months)]["count"]
    title = (f"The two main irrigation canals at Cochiti carry water from {MONTHS[int(on['month'].min()) - 1]} to "
             f"{MONTHS[int(on['month'].max()) - 1]} and have zero median flow in "
             f"{_month_list(off_months)}; median flow peaks near {peak['50%']:.0f} ft³/s")
    findings = [
        ("Measured", f"{first_year}-{last_year}: median monthly flow is zero in {_month_list(off_months)} "
                     f"in both canals; the {peak['canal']} peaks at about {peak['50%']:.0f} ft³/s in {MONTHS[int(peak['month']) - 1]}."),
        ("Insufficient data", "These are two USGS-gaged irrigation canals, not the acequia inventory: acequia locations, "
                              "service areas, and sources (research question 6) are still to be collected."),
    ]
    return Chart(
        key="canal_seasonal",
        title=title,
        subtitle=(f"Median monthly mean flow by calendar month, {first_year}-{last_year}; shaded band = middle half of "
                  "years; small numbers under each month = years with data"),
        caption=(f"Both canals take water from the Rio Grande at Cochiti for irrigation. Winter months have fewer years "
                 f"of data ({int(winter_n.min())}-{int(winter_n.max())} vs up to {int(stats['count'].max())}), possibly "
                 "because the canals are off and not always measured, so 'zero in winter' rests on fewer years. Canal "
                 "diversions show when surface-water irrigation is running; they are context for acequias, not acequia records."),
        scope=f"{SCOPE_COUNTY}: Cochiti, about {d.distance_km(q['latitude'].iloc[0], q['longitude'].iloc[0]):.0f} km from Cuba",
        rqs=(),  # answered a question the team dropped (see OUT_OF_SCOPE_CHARTS)
        findings=findings,
        fig=fig,
        data=stats.rename(columns={"50%": "median_cfs", "25%": "p25_cfs", "75%": "p75_cfs", "count": "years"}).round(1),
        source=f"USGS Water Data statistics, parameter 00060, monthly, sites 08313500 and 08314000 ({FILES['usgs']})",
        height=400,
    )


def bernalillo_river_vs_well(dark: bool = False) -> Chart:
    """Out of scope: answers the dropped question on groundwater-river links. Not in the app, docs, or report."""
    p = palette(dark)
    gw = d.load_groundwater_levels()
    names = gw.drop_duplicates("site_id").set_index("site_id")[["site_group", "well"]]
    ann = st_.annual_means(gw).join(names, on="site_id")
    bern = ann[ann["site_group"] == "Bernalillo site"]
    site_lat, site_lon = gw.loc[gw["site_group"] == "Bernalillo site", ["latitude", "longitude"]].iloc[0]
    q = d.load_usgs_stats("00060", "calendar_year")
    q = q[q["site_name"] == "RIO GRANDE BELOW COCHITI DAM, NM"].assign(year=lambda t: t["date"].dt.year)
    q = q[(q["year"] >= bern["year"].min()) & (q["year"] <= bern["year"].max())]
    styles = _well_style(dark)

    fig = make_subplots(
        rows=3, cols=2, column_widths=[0.62, 0.38], horizontal_spacing=0.1, vertical_spacing=0.13,
        specs=[[{}, None], [{}, {}], [{}, {}]],
        subplot_titles=["Rio Grande below Cochiti Dam: annual mean flow (ft³/s)",
                        "Main well: depth to water (ft; up = higher)", "Main well: yearly change (ft, + = rose)",
                        "Well A: depth to water (ft; up = higher)", "Well A: yearly change (ft, + = rose)"],
    )
    fig.add_trace(go.Bar(x=q["year"], y=q["value"], name="River flow", showlegend=False, width=0.6,
                         marker=dict(color=p["aqua"], cornerradius=3),
                         hovertemplate="%{x}: <b>%{y:,.0f} ft³/s</b><extra></extra>"), row=1, col=1)
    # axis names in this grid: row1 left x/y; row2 left x2/y2, right x3/y3; row3 left x4/y4, right x5/y5
    scatter_axes = {2: "3", 3: "5"}
    stats_rows, deltas = [], []
    flow = q.set_index("year")["value"]
    for row, well in [(2, "Well"), (3, "Well A")]:
        s = bern[bern["well"] == well].sort_values("year")
        sg = _break_gaps(s, "year", 0.5, 1)
        fig.add_trace(go.Scatter(
            x=sg["year"], y=sg["value"], mode="lines+markers", name=f"Bernalillo {well}", showlegend=False,
            line=dict(color=styles[well]["color"], width=LINE_WIDTH),
            marker=dict(size=MARKER_SIZE - 2, color=styles[well]["color"], line=_ring(dark)),
            hovertemplate=f"Bernalillo {well}" + " %{x}: <b>%{y:.1f} ft</b><extra></extra>",
        ), row=row, col=1)
        fig.update_yaxes(autorange="reversed", row=row, col=1, dtick=5 if well == "Well" else 1)
        s = s.set_index("year")
        consecutive = [y for y in s.index if y - 1 in s.index and y in flow.index and y - 1 in flow.index]
        dl = pd.DataFrame({"year": consecutive,
                           "change_flow_cfs": [flow[y] - flow[y - 1] for y in consecutive],
                           # water-level change = minus the depth change, so + means the water table rose
                           "change_level_ft": [-(s.loc[y, "value"] - s.loc[y - 1, "value"]) for y in consecutive]})
        dl["well"] = well
        deltas.append(dl)
        rho = st_.spearman(dl["change_flow_cfs"], dl["change_level_ft"])
        pval = st_.permutation_p(dl["change_flow_cfs"], dl["change_level_ft"])
        stats_rows.append({"well": well, "n": len(dl), "rho": rho, "p": pval, "mean_depth": s["value"].mean()})
        fig.add_trace(go.Scatter(
            x=dl["change_flow_cfs"], y=dl["change_level_ft"], mode="markers", showlegend=False,
            marker=dict(size=MARKER_SIZE, color=styles[well]["color"], line=_ring(dark)),
            customdata=dl[["year"]].to_numpy(),
            hovertemplate=("%{customdata[0]} vs year before:<br>river %{x:+,.0f} ft³/s, water level "
                           "<b>%{y:+.2f} ft</b><extra></extra>"),
        ), row=row, col=2)
        fig.add_hline(y=0, line=dict(color=p["axis"], width=1), row=row, col=2)
        fig.add_vline(x=0, line=dict(color=p["axis"], width=1), row=row, col=2)
        ax = scatter_axes[row]
        # headroom above the dots, so the statistics label never sits on a data point
        lo, hi = dl["change_level_ft"].min(), dl["change_level_ft"].max()
        fig.update_yaxes(range=[lo - 0.08 * (hi - lo), hi + 0.42 * (hi - lo)], row=row, col=2)
        fig.add_annotation(x=0.02, y=0.98, xref=f"x{ax} domain", yref=f"y{ax} domain",
                           text=f"ρ = {rho:+.2f}, n = {len(dl)}, p = {pval:.2f}", showarrow=False,
                           xanchor="left", yanchor="top", font=dict(size=12, color=p["ink2"]))
        fig.update_xaxes(title_text="Change in river flow from the year before (ft³/s)" if row == 3 else None,
                         title_font=dict(size=13), row=row, col=2)
    xr = [bern["year"].min() - 0.6, bern["year"].max() + 0.6]
    for row in (1, 2, 3):
        fig.update_xaxes(range=xr, row=row, col=1, dtick=5)
    fig.update_yaxes(rangemode="tozero", row=1, col=1)
    _left_align_titles(fig, p["ink2"], size=13)
    fig.add_annotation(x=0.69, y=0.97, xref="paper", yref="paper", xanchor="left", yanchor="top", showarrow=False,
                       align="left", font=dict(size=12, color=p["ink2"]),
                       text=("<b>How to read the right column</b><br>Each dot is one year compared with the year<br>"
                             "before: right = more river flow, up = water<br>level rose. Dots running from lower left to<br>"
                             "upper right mean the well tracks the river."))
    _base_layout(fig, dark, 640, margin=dict(t=50, b=60, l=70, r=30))
    st = pd.DataFrame(stats_rows).set_index("well")
    a, w = st.loc["Well A"], st.loc["Well"]
    nb = "\u00a0"  # non-breaking spaces keep "ρ = +0.54" on one line
    title = (f"At Bernalillo, Well A's water level tended to rise in years when river flow increased (ρ{nb}={nb}{a['rho']:+.2f}, "
             f"n{nb}={nb}{int(a['n'])}); the main well showed no clear link (ρ{nb}={nb}{w['rho']:+.2f})")
    findings = [
        ("Measured", f"Year-to-year change in Well A water level vs change in river flow: Spearman ρ = {a['rho']:+.2f} "
                     f"(n = {int(a['n'])} year pairs, permutation p = {a['p']:.3f}); main well ρ = {w['rho']:+.2f} "
                     f"(p = {w['p']:.2f}). With two wells tested, a Bonferroni-adjusted p for Well A is "
                     f"{min(1, 2 * a['p']):.3f}, so the link is suggestive, not firm."),
        ("Hypothesis", f"Well A (water about {a['mean_depth']:.0f} ft down) may respond to river-fed recharge near the "
                       f"Rio Grande, while the main well (about {w['mean_depth']:.0f} ft down) follows a slower long-term "
                       "decline; well construction details would be needed to confirm."),
        ("Insufficient data", "This is the only place in the data with a long well record near a long river record; "
                              "there is nothing comparable near Cuba."),
    ]
    dl_all = pd.concat(deltas)
    data = (bern[["site_id", "well", "year", "value", "months"]].rename(columns={"value": "depth_to_water_ft"})
            .merge(q[["year", "value"]].rename(columns={"value": "rio_grande_flow_cfs"}), on="year", how="left")
            .merge(dl_all, on=["well", "year"], how="left"))
    gage_km = d.distance_km(q["latitude"].iloc[0], q["longitude"].iloc[0], site_lat, site_lon)
    return Chart(
        key="bernalillo_river_vs_well",
        title=title,
        subtitle=(f"Left: annual mean river flow and depth to water at the two Bernalillo-site wells, "
                  f"{_years(bern['year'])}. Right: each dot is one year's change from the year before"),
        caption=(f"Separate panels share the year axis instead of one chart with two scales; their vertical scales differ "
                 f"(the main well spans about {bern[bern['well'] == 'Well']['value'].agg(lambda v: v.max() - v.min()):.0f} ft, "
                 f"Well A about {bern[bern['well'] == 'Well A']['value'].agg(lambda v: v.max() - v.min()):.0f} ft). The scatters use changes "
                 "from one year to the next, so the long-term drift in both records can't create a false match; "
                 "water-level change is positive when the water table rose. The two scatters also use different "
                 "vertical scales. Lines break where a year has fewer than "
                 f"{st_.MIN_MONTHS_PER_YEAR} months of well data. The flow gage is about {gage_km:.0f} km upstream of the wells (the closer "
                 "Rio Grande near Bernalillo gage stopped in 1969)."),
        scope=f"{SCOPE_COUNTY}: Bernalillo, about {d.distance_km(site_lat, site_lon):.0f} km from Cuba",
        rqs=(),  # answered a question the team dropped (see OUT_OF_SCOPE_CHARTS)
        findings=findings,
        fig=fig,
        data=data.round(3),
        source=(f"USGS Water Data statistics: parameter 72019 ({FILES['gw']}) and parameter 00060 calendar-year means, "
                f"site 08317400 ({FILES['usgs']})"),
        height=640,
    )


# ---------------------------------------------------------------------------
# RQ5/RQ6: Coverage, evidence, indicators
# ---------------------------------------------------------------------------
COUNTY_HEADER = "<b>Whole county</b> (including Cuba)"
CUBA_HEADER = f"<b>Cuba area</b> (≤{CUBA_RADIUS_KM} km)"


def _coverage_counts() -> pd.DataFrame:
    """Number of sites with at least one record, per row and year."""
    rows = []
    near = lambda df: d.distance_km(df["latitude"], df["longitude"]) <= CUBA_RADIUS_KM  # noqa: E731
    gw = d.load_groundwater_levels()
    nm = d.load_nmbgmr_levels().dropna(subset=["depth_to_water_ft"])
    at = d.load_aquifer_tests().assign(site_id=lambda t: t["well_key"])
    wl = d.load_well_logs()
    flow = pd.concat([d.load_usgs_stats("00060", "month"), d.load_rio_puerco()])
    levels = pd.concat([gw[["site_id", "latitude", "longitude", "date"]], nm[["site_id", "latitude", "longitude", "date"]]])
    tests = pd.concat([at[["site_id", "latitude", "longitude", "date"]],
                       wl.dropna(subset=["latitude"])[["site_id", "latitude", "longitude", "date"]]])

    def add(df, label, group):
        c = df.dropna(subset=["date"]).assign(year=lambda t: t["date"].dt.year).groupby("year")["site_id"].nunique()
        rows.extend({"row": label, "group": group, "year": int(y), "sites": int(n)} for y, n in c.items())
        if c.empty:
            rows.append({"row": label, "group": group, "year": np.nan, "sites": 0})

    add(gw.assign(site_id=gw["site_group"]), "Water levels: USGS monitoring sites", "county")
    add(nm, "Water levels: NMBGMR wells", "county")
    add(at, "Aquifer tests (OSE)", "county")
    add(wl, "Well logs (OSE)", "county")
    add(flow, "Streamflow (USGS)", "county")
    add(levels[near(levels)], "Water-level monitoring", "cuba")
    add(tests[near(tests)], "Aquifer tests and well logs", "cuba")
    add(flow[near(flow)], "Streamflow", "cuba")
    return pd.DataFrame(rows)


def coverage_timeline(dark: bool = False, start: int = 1925, end: int = 2026) -> Chart:
    p = palette(dark)
    cov = _coverage_counts()
    cov["label"] = np.where(cov["group"] == "cuba", "Cuba area: " + cov["row"], cov["row"])
    labels = ([COUNTY_HEADER] + cov.loc[cov["group"] == "county", "label"].drop_duplicates().tolist()
              + [CUBA_HEADER] + cov.loc[cov["group"] == "cuba", "label"].drop_duplicates().tolist())
    years = list(range(start, end + 1))
    z = np.full((len(labels), len(years)), np.nan)
    counts = np.full_like(z, np.nan)
    for i, lab in enumerate(labels):
        for _, x in cov[(cov["label"] == lab) & cov["year"].between(start, end)].iterrows():
            j = int(x["year"]) - start
            n = x["sites"]
            counts[i, j] = n
            z[i, j] = 1 if n == 1 else 2 if n <= 4 else 3 if n <= 9 else 4
    ramp = RAMP_DARK if dark else RAMP_LIGHT
    cs = []
    for k, c in enumerate(ramp):
        cs += [[k / 4, c], [(k + 1) / 4, c]]
    ticktext = [lab.replace("Cuba area: ", "") if not lab.startswith("<b>") else lab for lab in labels]
    fig = go.Figure(go.Heatmap(
        x=years, y=labels, z=z, zmin=0.5, zmax=4.5, colorscale=cs, xgap=1, ygap=6, customdata=counts, showscale=False,
        hovertemplate="%{y}<br>%{x}: <b>%{customdata:.0f}</b> site(s) with records<extra></extra>",
    ))
    for lab, c in zip(["1 site", "2-4 sites", "5-9 sites", "10+ sites"], ramp):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=lab,
                                 marker=dict(symbol="square", size=12, color=c)))
    fig.add_hline(y=labels.index(CUBA_HEADER) - 0.5, line=dict(color=p["axis"], width=1.5))
    for i, lab in enumerate(labels):
        if not lab.startswith("<b>") and np.all(np.isnan(z[i])):
            fig.add_annotation(x=(start + end) / 2, y=lab, text="no records in the collected data", showarrow=False,
                               font=dict(size=12, color=p["muted"]))
    fig.update_yaxes(categoryorder="array", categoryarray=labels, tickvals=labels, ticktext=ticktext,
                     autorange="reversed", showgrid=False)
    fig.update_xaxes(range=[start - 0.5, end + 0.5], dtick=10, showgrid=False)
    _base_layout(fig, dark, 520, margin=dict(l=270, t=60), legend=dict(y=1.04))

    usgs = cov[cov["row"] == "Water levels: USGS monitoring sites"]
    n_sites = int(usgs["sites"].max())
    all_year = int(usgs.loc[usgs["sites"] == n_sites, "year"].min())
    nmb = cov[cov["row"] == "Water levels: NMBGMR wells"]["year"].astype(int).sort_values()
    nmb_blocks = []
    for y in nmb:
        if nmb_blocks and y - nmb_blocks[-1][1] <= 1:
            nmb_blocks[-1][1] = y
        else:
            nmb_blocks.append([y, y])
    tests_cuba = cov[(cov["label"] == "Cuba area: Aquifer tests and well logs") & cov["year"].notna()]
    flow_cuba = cov[(cov["label"] == "Cuba area: Streamflow") & cov["year"].notna()]
    title = (f"Groundwater levels are monitored every year only since {all_year}, at {n_sites} sites in the east of the "
             "county; the collected data have no water-level monitoring in the Cuba area")
    findings = [
        ("Measured", f"USGS monitoring sites cover {_years(usgs['year'])} (all {n_sites} from {all_year}); NMBGMR wells were measured in "
                     + " and ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in nmb_blocks) + ", with nothing in between."),
        ("Measured", f"Cuba-area well records come from {len(tests_cuba)} separate years "
                     f"({_years(tests_cuba['year'])}); the only recent Cuba-area data are Rio Puerco visits "
                     f"({_years(flow_cuba['year'])})."),
        ("Insufficient data", "No repeated groundwater-level records exist for the Cuba area in the collected data."),
    ]
    return Chart(
        key="coverage_timeline",
        title=title,
        subtitle=(f"Number of sites with at least one record, by year ({int(cov['year'].min())}-{end}); top: whole county, "
                  "bottom: the Cuba area only"),
        caption=(f"Darker = more sites recorded that year. The USGS row counts monitoring sites (locations; the "
                 f"{d.load_groundwater_levels()['site_id'].nunique()} wells sit at {n_sites} sites). Aquifer tests count wells tested that year (each test also "
                 "records a one-time water level, which isn't monitoring). Streamflow includes the Rio Puerco at Cuba "
                 "visits. Gaps are years with no record in these files; "
                 "other agencies may have data."),
        scope=SCOPE_PROJECT,
        rqs=(5, 6),
        findings=findings,
        fig=fig,
        data=cov.drop(columns="label"),
        source=ALL_SOURCES.split("; county")[0],
        height=520,
    )


# Support levels from Dylan's dataset briefs (docs/files/support_doc1-7) plus the
# analysis team's rating of the OSE aquifer-test file (no brief yet) and of the
# non-groundwater parts of dataset 1. Levels: 3 strong, 2 moderate, 1 limited, 0 none.
EVIDENCE = {
    "1 · USGS stats (wells)": {1: ("Strong", 3), 2: ("Partial", 1), 3: ("None", 0), 5: ("Strong", 3), 6: ("Strong", 3)},
    "1 · USGS stats (rivers)†": {5: ("Moderate", 2)},
    "2 · NMBGMR wells": {1: ("Moderate", 2), 2: ("Best fit", 2), 3: ("None", 0), 5: ("Strong", 3), 6: ("Moderate", 2)},
    "3 · Aquifer sensitivity": {1: ("None", 0), 2: ("None", 0), 3: ("None", 0), 5: ("Limited", 1), 6: ("Conditional", 1)},
    "4 · Rio Puerco at Cuba": {1: ("None", 0), 2: ("None", 0), 3: ("None", 0), 4: ("None", 0), 5: ("Moderate", 2), 6: ("Moderate", 2)},
    "5 · Ojo Alamo map‡": {2: ("Partial", 1), 3: ("None", 0), 4: ("Strong‡", 3)},
    "6 · San Jose study": {1: ("Limited", 1), 2: ("Strong", 3), 3: ("Limited", 1), 4: ("Strong", 3), 5: ("Moderate", 2), 6: ("Context", 1)},
    "7 · OSE well logs": {1: ("None", 0), 2: ("Best fit", 2), 3: ("None", 0), 4: ("Potential", 1), 5: ("Useful", 2), 6: ("Context", 1)},
    "OSE aquifer tests†": {1: ("None", 0), 2: ("Strong", 3), 3: ("Limited", 1), 4: ("Limited", 1), 5: ("Moderate", 2)},
}
EVIDENCE_WORDS = {3: "Strong", 2: "Moderate, Best fit, Useful", 1: "Limited, Partial, Potential, Conditional, Context",
                  0: "None"}
# What each weakly supported question still needs (from data-collection.md, "Not collected").
NEEDS_DATA = {3: "Cuba's municipal well records"}
# The six research questions (docs/index.md). The briefs used the proposal's nine; their ratings
# are carried over with the team's renumbering (Q1-Q4 unchanged, Q8 -> Q5, Q9 -> Q6).
RQ_SHORT = {
    1: "1 Groundwater-level trends", 2: "2 Wells and aquifer units", 3: "3 Groundwater near Cuba",
    4: "4 Ojo Alamo vs San Jose", 5: "5 Monitoring coverage and gaps", 6: "6 Groundwater-stress indicators",
}


LEVEL_NAMES = ["None", "Limited", "Moderate", "Strong"]


def _evidence_balls(fig: go.Figure, cols: list, rqs: list, z: np.ndarray, text: list, dark: bool):
    """Pictograph version of evidence_matrix: a Harvey ball per rating (empty = none,
    one third = limited, two thirds = moderate, full = strong), with the brief's word under it."""
    p = palette(dark)
    for i in range(len(rqs)):
        if i % 2 == 0:  # faint row bands help the eye across nine columns
            fig.add_shape(type="rect", x0=-0.5, x1=len(cols) - 0.5, y0=i - 0.5, y1=i + 0.5, line_width=0,
                          fillcolor=_rgba(p["grid"], 0.55 if not dark else 0.6), layer="below")
    hx, hy, hc = [], [], []
    for i, q in enumerate(rqs):
        for j, c in enumerate(cols):
            if not text[i][j]:
                continue
            fig.add_layout_image(source=icons.harvey_svg(z[i, j] / 3, p["ink2"], p["surface"]), x=j, y=i - 0.12,
                                 xref="x", yref="y", sizex=0.56, sizey=0.56, xanchor="center", yanchor="middle",
                                 sizing="contain", layer="above")
            fig.add_annotation(x=j, y=i + 0.3, text=text[i][j], showarrow=False, font=dict(size=10.5, color=p["ink2"]))
            hx.append(j); hy.append(i); hc.append([c, RQ_SHORT[q], text[i][j], LEVEL_NAMES[int(z[i, j])]])
    fig.add_trace(go.Scatter(x=hx, y=hy, mode="markers", marker=dict(size=26, opacity=0), showlegend=False,
                             customdata=hc, hovertemplate="<b>%{customdata[1]}</b><br>%{customdata[0]}: %{customdata[2]} "
                                                          "(%{customdata[3]})<extra></extra>"))
    fig.update_xaxes(side="top", tickangle=-30, showgrid=False, showline=False, ticks="", tickvals=list(range(len(cols))),
                     ticktext=cols, range=[-0.5, len(cols) - 0.5])
    fig.update_yaxes(showgrid=False, showline=False, ticks="", tickvals=list(range(len(rqs))),
                     ticktext=[RQ_SHORT[q] for q in rqs], range=[len(rqs) - 0.5, -0.5])
    _hkey(fig, dark, [(icons.harvey_svg(k / 3, p["ink2"], p["surface"]), lab) for k, lab in enumerate(LEVEL_NAMES)],
          y=-0.07, x0=0.01, size=0.05, spacing=0.17)


def evidence_matrix(dark: bool = False, pictograph: bool = True) -> Chart:
    p = palette(dark)
    cols = list(EVIDENCE)
    rqs = list(RQ_SHORT)
    z = np.full((len(rqs), len(cols)), np.nan)
    text = [["" for _ in cols] for _ in rqs]
    for j, c in enumerate(cols):
        for i, q in enumerate(rqs):
            if q in EVIDENCE[c]:
                text[i][j], z[i, j] = EVIDENCE[c][q]
    ramp = [p["grid"], *(RAMP_DARK if dark else RAMP_LIGHT)[:3]]
    if pictograph:
        fig = go.Figure()
        _evidence_balls(fig, cols, rqs, z, text, dark)
        _base_layout(fig, dark, 600, showlegend=False, margin=dict(l=230, t=130, b=60, r=130))
    else:
        fig = _evidence_heatmap(cols, rqs, z, text, ramp, dark)
    weak = [q for q in rqs if not any(EVIDENCE[c].get(q, ("", -1))[1] >= 2 for c in cols)]
    return _evidence_chart(fig, cols, rqs, weak, pictograph)


def _evidence_heatmap(cols, rqs, z, text, ramp, dark) -> go.Figure:
    p = palette(dark)
    cs = []
    for k, c in enumerate(ramp):
        cs += [[k / 4, c], [(k + 1) / 4, c]]
    fig = go.Figure(go.Heatmap(
        x=cols, y=[RQ_SHORT[q] for q in rqs], z=z, zmin=-0.5, zmax=3.5, colorscale=cs, xgap=3, ygap=3,
        showscale=False, customdata=text, hovertemplate="<b>%{y}</b><br>%{x}: %{customdata}<extra></extra>",
    ))
    for i, q in enumerate(rqs):
        for j, c in enumerate(cols):
            if text[i][j]:
                light_text = z[i, j] >= 3 if not dark else z[i, j] <= 1  # pick the readable ink for each cell
                fig.add_annotation(x=c, y=RQ_SHORT[q], text=text[i][j], showarrow=False,
                                   font=dict(size=11.5, color=("#ffffff" if not dark else "#f0efec") if light_text
                                             else "#0b0b0b"))
    for lab, c in zip(["None", "Limited", "Moderate", "Strong"], ramp):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=lab,
                                 marker=dict(symbol="square", size=13, color=c)))
    fig.update_xaxes(side="top", tickangle=-30, showgrid=False, showline=False, ticks="")
    fig.update_yaxes(autorange="reversed", showgrid=False, showline=False, ticks="")
    _base_layout(fig, dark, 480, legend=dict(y=-0.04, yanchor="top"), margin=dict(l=230, t=130, b=40, r=60))
    return fig


def _evidence_chart(fig, cols, rqs, weak, pictograph) -> Chart:
    missing = {q: NEEDS_DATA[q] for q in weak if q in NEEDS_DATA}
    which = (f"research question {weak[0]}, about {RQ_SHORT[weak[0]][2:].lower().replace('cuba', 'Cuba')}"
             if len(weak) == 1 else
             f"research questions {', '.join(str(q) for q in weak[:-1])} and {weak[-1]}")
    title = (f"Per the dataset briefs, no dataset gives more than limited support for {which}; coverage, "
             "trend, and well questions are the best supported")
    findings = [
        ("Insufficient data", f"No dataset is rated moderate or strong for question{'s' if len(weak) > 1 else ''} "
                              + "; ".join(f"{q} ({RQ_SHORT[q][2:]})" for q in weak) + "."),
        ("Insufficient data", "; ".join(f"Question {q} needs {need}" for q, need in missing.items())
                              + ", which weren't collected."),
    ]
    rows = [{"dataset": c, "research_question": RQ_SHORT[q], "support": EVIDENCE[c][q][0], "level": EVIDENCE[c][q][1]}
            for c in cols for q in rqs if q in EVIDENCE[c]]
    return Chart(
        key="evidence_matrix",
        title=title,
        subtitle="How well each dataset can answer each research question; blank = not applicable or not assessed",
        caption=("Ratings come from Dylan's one-page dataset briefs; each cell shows a short form of the brief's wording "
                 "(e.g. 'Best fit' for 'Strongest fit (partial)'), grouped into "
                 + ("four Harvey balls (empty, one third, two thirds, full): " if pictograph else "four colors: ")
                 + "; ".join(f"{['None', 'Limited', 'Moderate', 'Strong'][k]} = {v}"
                                            for k, v in sorted(EVIDENCE_WORDS.items())) +
                 ". The briefs rated the proposal's nine questions; their ratings are shown under the team's six "
                 "(questions 1-4 unchanged, 8 → 5, 9 → 6; the three dropped questions are left out). "
                 "† = no brief; rated by the analysis (the river part of USGS dataset 1 and the OSE aquifer tests). "
                 "‡ = an image-only map plate: it is shown as an "
                 "attributed map on the Cuba page but not digitized, so its numbers aren't charted, and its 'Strong' for "
                 "question 4 holds only once it is digitized. This is a judgment summary of what each dataset could "
                 "support, not a measurement."),
        scope=SCOPE_PROJECT,
        rqs=(5, 6),
        findings=findings,
        fig=fig,
        data=pd.DataFrame(rows),
        source=("Dataset briefs 1-7 (docs/files/support_doc1-7) by D. Gonzales; † no brief, rated by the analysis; "
                "‡ image-only map plate, not digitized"),
        height=600 if pictograph else 480,
    )


def _waffle_counts(pcts: pd.Series, n: int = 100) -> pd.Series:
    """Whole cells per class that add up to n (largest-remainder rounding)."""
    raw = pcts / pcts.sum() * n
    cells = np.floor(raw).astype(int)
    for k in (raw - cells).sort_values(ascending=False).index[: n - int(cells.sum())]:
        cells[k] += 1
    return cells


def _sensitivity_waffles(fig: go.Figure, g: pd.DataFrame, order: list, names: dict, dark: bool):
    """Pictograph version of aquifer_sensitivity_classes: two 10 x 10 unit charts,
    one square = 1% of the polygons (left) or of the listed area (right)."""
    p = palette(dark)
    ramp = RAMP_DARK if dark else RAMP_LIGHT
    shade = {"High": ramp[3], "Moderate": ramp[1], "Less": ramp[0]}
    offset = 12.5
    scale = []
    for k, cls in enumerate(order):  # discrete colorscale: class index -> its shade
        scale += [[k / len(order), shade[cls]], [(k + 1) / len(order), shade[cls]]]
    panels = [("share_polygons_pct", "Share of mapped areas (polygons)"), ("share_area_pct", "Share of listed area (map units)")]
    for k, (col, label) in enumerate(panels):
        cells = _waffle_counts(g[col])
        seq = [i for i, cls in enumerate(order) for _ in range(int(cells[cls]))]   # row by row from the top left
        z = np.array(seq, dtype=float).reshape(10, 10)
        info = np.array([[f"{names[order[int(v)]]}: <b>{g.loc[order[int(v)], col]:.1f}%</b> "
                          f"({int(g.loc[order[int(v)], 'polygons'])} polygons)" for v in row] for row in z])
        x0 = k * offset
        fig.add_trace(go.Heatmap(
            z=z, x=x0 + np.arange(10) + 0.5, y=np.arange(10) + 0.5, zmin=-0.5, zmax=len(order) - 0.5,
            colorscale=scale, showscale=False, xgap=3, ygap=3, customdata=info,
            hovertemplate=f"{label}<br>" + "%{customdata}<extra></extra>"))
        fig.add_annotation(x=x0, y=-0.35, text=f"<b>{label}</b>", showarrow=False, xanchor="left", yanchor="bottom",
                           font=dict(size=13.5, color=p["ink2"]))
        fig.add_annotation(x=x0, y=10.25, showarrow=False, xanchor="left", yanchor="top",
                           text="   ".join(f"{names[c]} <b>{g.loc[c, col]:.0f}%</b>" for c in order),
                           font=dict(size=13, color=p["ink2"]))
    for cls in order:  # legend swatches
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"{names[cls]} sensitivity",
                                 marker=dict(symbol="square", size=14, color=shade[cls])))
    # square cells: the y axis is tied to x, and x widens its range (not its domain), so the plot area
    # keeps the full width and the footer of the slide image lines up with the other charts
    fig.update_xaxes(visible=False, range=[-0.3, offset + 10.3], constrain="range", showgrid=False)
    fig.update_yaxes(visible=False, range=[11.4, -1.6], scaleanchor="x", scaleratio=1, constrain="range", showgrid=False)


def _sensitivity_bars(fig: go.Figure, g: pd.DataFrame, order: list, names: dict, dark: bool):
    """Plain version of aquifer_sensitivity_classes: two bar panels."""
    p = palette(dark)
    for c, col in enumerate(["share_polygons_pct", "share_area_pct"], start=1):
        fig.add_trace(go.Bar(
            x=g[col], y=[names[k] for k in order], orientation="h", width=0.5, showlegend=False,
            marker=dict(color=p["ink2"], cornerradius=4), text=[f"{v:.0f}%" for v in g[col]], textposition="outside",
            textfont=dict(color=p["ink2"]), customdata=g[["polygons"]].to_numpy(),
            hovertemplate="%{y}: <b>%{x:.1f}%</b> (%{customdata[0]} polygons)<extra></extra>",
        ), row=1, col=c)
        fig.update_xaxes(range=[0, 75], ticksuffix="%", row=1, col=c)


def aquifer_sensitivity_classes(dark: bool = False, pictograph: bool = True) -> Chart:
    p = palette(dark)
    raw = pd.read_csv(d.CLEAN / "aquifer_sensitivity.csv")
    names = {"High": "High", "Moderate": "Moderate", "Less": "Less"}
    g = raw.groupby("sensitivity").agg(polygons=("polygon_id", "size"), area=("area_sq_deg", "sum"))
    g["share_polygons_pct"] = 100 * g["polygons"] / g["polygons"].sum()
    g["share_area_pct"] = 100 * g["area"] / g["area"].sum()
    order = [k for k in ["High", "Moderate", "Less"] if k in g.index]
    g = g.loc[order]
    if pictograph:
        fig = go.Figure()
        _sensitivity_waffles(fig, g, order, names, dark)
        _base_layout(fig, dark, 400, margin=dict(l=30, t=50, r=30, b=10),
                     legend=dict(orientation="h", y=1.08, yanchor="bottom", x=0))
    else:
        fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.08,
                            subplot_titles=["Share of mapped areas (polygons)", "Share of listed area (map units)"])
        _sensitivity_bars(fig, g, order, names, dark)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        _left_align_titles(fig, p["ink2"], size=13.5)
        _base_layout(fig, dark, 280, margin=dict(l=110, t=50))
    hi = g.loc["High"] if "High" in g.index else None
    title = (f"High sensitivity covers {hi['share_polygons_pct']:.0f}% of the {len(raw)} mapped areas but "
             f"{hi['share_area_pct']:.0f}% of the listed area; without locations, none of it can be placed on the map "
             "or linked to Cuba") if hi is not None else f"The aquifer-sensitivity file lists {len(raw)} mapped areas"
    findings = [
        ("Measured", f"{len(raw)} polygons: " + ", ".join(f"{names[k]} {int(g.loc[k, 'polygons'])}" for k in order)
                     + "; share of listed area: " + ", ".join(f"{names[k]} {g.loc[k, 'share_area_pct']:.0f}%" for k in order) + "."),
        ("Insufficient data", "The CSV has no coordinates, and what 'sensitivity' measures isn't documented in it; the "
                              "map layer and its metadata weren't collected (a coverage gap, research question 5)."),
    ]
    return Chart(
        key="aquifer_sensitivity_classes",
        title=title,
        subtitle=("Aquifer-sensitivity classes in the downloaded table (dataset 3): share of polygons and share of listed area"
                  + ("; one square = 1%" if pictograph else "")),
        caption=("Area shares use the table's area_sq_deg column, in square degrees (the source doesn't state units; "
                 "square degrees shrink slightly northward), so the shares are approximate. Polygon counts and area "
                 "shares differ because a few large polygons dominate. This describes the downloaded inventory, not Cuba."
                 + (" Squares are rounded to whole percents so each grid adds up to 100." if pictograph else "")),
        scope=("Probably statewide, not Sandoval County or Cuba (the file has no locations; if its area units are "
               "square degrees, the listed areas add up to about the size of New Mexico)"),
        rqs=(5, 6),
        findings=findings,
        fig=fig,
        data=g.rename(index=names).rename_axis("sensitivity").reset_index().round(2),
        source=f"New Mexico Water Data, aquifer sensitivity ({FILES['sens']})",
        height=400 if pictograph else 280,
    )


def indicator_table() -> pd.DataFrame:
    """Research question 6: indicators for a groundwater-stress dashboard, each with
    where it applies and how much to trust it. Values computed from the data."""
    gw = d.load_groundwater_levels()
    rec = st_.well_trends(gw, 2016, 2025).dropna(subset=["level_slope_ft_per_yr"])
    ann = st_.annual_means(gw).sort_values("year")
    # measured water-level change per well = minus (last annual depth - first annual depth)
    measured = ann.groupby("site_id")["value"].agg(lambda v: -(v.iloc[-1] - v.iloc[0]))
    k = cuba_key_numbers()
    return pd.DataFrame([
        {"Indicator": "Water-level trend, 2016-2025", "Applies to": f"{gw['site_group'].nunique()} USGS sites, Rio Rancho to Cochiti",
         "Value": f"{(rec['trend'] == 'Declining').sum()} of {len(rec)} wells falling, {(rec['trend'] == 'Rising').sum()} rising",
         "Confidence": "Moderate (9-10 years per well)", "Caveat": "Not representative of the whole county; none near Cuba"},
        {"Indicator": "Water-level change, full record", "Applies to": f"Same {gw['site_id'].nunique()} wells",
         "Value": f"{measured.min():+.0f} to {measured.max():+.0f} ft, first to last full year",
         "Confidence": "High at these wells", "Caveat": "Change depends on start year (Sandia fell, then recovered)"},
        {"Indicator": "Distance to nearest repeated water-level record", "Applies to": "Cuba",
         "Value": f"{k['nearest_water_level_km']:.0f} km ({k['nearest_water_level_n']} readings, {k['nearest_water_level_last_year']})",
         "Confidence": "High (it is a count, not an estimate)", "Caveat": "Shows a data gap, not a water condition"},
        {"Indicator": "Rio Puerco visits with measurable flow", "Applies to": "Cuba (river)",
         "Value": f"{k['rio_puerco_flowing']} of {k['rio_puerco_visits']} visits ({k['rio_puerco_years']})",
         "Confidence": "Low", "Caveat": f"{k['rio_puerco_visits']} spot visits; the season of each visit drives the result"},
        {"Indicator": "Aquifer properties near Cuba", "Applies to": f"Cuba area (≤{CUBA_RADIUS_KM} km)",
         "Value": f"{k['aquifer_test_wells_in_area']} tested wells, {k['aquifer_test_years']}",
         "Confidence": "Low", "Caveat": "One-time historical tests; formation often not recorded"},
    ])


# ---------------------------------------------------------------------------
# Registry: every chart, in display order
# ---------------------------------------------------------------------------
ALL_CHARTS = [
    county_coverage_map,
    groundwater_hydrographs,
    groundwater_trends,
    placitas_remeasured,
    well_depth_vs_water,
    depth_by_area,
    formation_properties,
    cuba_area_map,
    cuba_nearest_records,
    ojo_alamo_depth_map,
    ojo_alamo_vs_san_jose,
    rio_puerco_visits,
    coverage_timeline,
    evidence_matrix,
    aquifer_sensitivity_classes,
]

# Charts for research questions the team dropped when the questions were narrowed from nine to
# six (water quality, acequias and canals, groundwater-river links). They still run, but they are
# not in the app, the docs, the report, or the figure exports. Kept in case those questions return.
OUT_OF_SCOPE_CHARTS = [rio_grande_quality, canal_seasonal, bernalillo_river_vs_well]

# Charts with a pictograph version (``pictograph=True``, the default). The app and the
# slide/docs images use it; the LaTeX report uses ``pictograph=False``.
PICTOGRAPH_CHARTS = {fn.__name__ for fn in (placitas_remeasured, cuba_area_map, cuba_nearest_records,
                                            rio_puerco_visits, evidence_matrix, aquifer_sensitivity_classes)}
