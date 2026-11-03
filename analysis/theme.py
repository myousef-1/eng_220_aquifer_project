"""Colors, fonts, and the shared Plotly look for every chart in the project.

Why a theme module?
    Every chart should look like it belongs to the same project, in the app,
    in the report, and on the slides. All colors and chart chrome live here,
    so changing a color means changing it in one place.

Light and dark
    The app can run in Streamlit's light or dark theme. Each color has a light
    and a dark step (the dark steps are slightly adjusted so they stay readable
    on a dark background). Chart functions take ``dark=True/False`` and ask
    ``palette(dark)`` for colors.

What each color means (the same everywhere in the app and report)
    * Data types (maps, coverage charts, and any chart that mixes sources):
      blue = water-level records, orange = well construction and aquifer tests,
      aqua = surface water (rivers, canals, the Rio Puerco gage).
    * Wells at one monitoring site (Well, Well A, Well B) and the two Placitas
      measurement periods: shades of the water-level blue (lighter = older period).
    * Geologic formations near Cuba: ochre = Ojo Alamo Sandstone,
      violet = San Jose Formation. Other formations are gray context.
    * Water-level trend direction: blue = rising, red = falling, gray = no clear trend.
    * Counts and ratings (coverage timeline, evidence matrix): one neutral gray
      ramp, darker = more (lighter = more in dark mode).

The palette was checked with a colorblind-safety validator (all three map /
scatter colors stay distinguishable for the common types of color blindness
in both modes). Keep the slot ORDER as is: the order is part of what makes it
safe. If you need more than three categories in a scatter or map, use the
legend + symbols, or split the chart into panels, instead of adding colors.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------
_LIGHT = {
    # categorical slots, always used in this order
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
    # diverging pair for "water table rising" vs "falling"
    "rise": "#2a78d6",
    "fall": "#e34948",
    # text and chrome
    "ink": "#0b0b0b",
    "ink2": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "surface": "#ffffff",
    "context": "#b8b6ae",  # de-emphasized points (the "everything else" gray)
    "boundary": "#52514e",
    # shades of the water-level blue, for wells at one site and for time periods
    "blue_light": "#86b6ef",
    "blue_dark": "#104281",
    # geologic formations near Cuba
    "ojo_alamo": "#c98500",
    "san_jose": "#6250d6",
}

_DARK = {
    "blue": "#3987e5",
    "orange": "#d95926",
    "aqua": "#199e70",
    "rise": "#3987e5",
    "fall": "#e66767",
    "ink": "#f0efec",
    "ink2": "#c3c2b7",
    "muted": "#898781",
    "grid": "#2c2c2a",
    "axis": "#383835",
    "surface": "#0e1117",  # Streamlit's dark background
    "context": "#5f5e59",
    "boundary": "#c3c2b7",
    "blue_light": "#184f95",  # on dark backgrounds the "older/lighter" step is the darker one
    "blue_dark": "#9ec5f4",
    "ojo_alamo": "#c98500",
    "san_jose": "#9085e9",
}

# Ordinal ramp for counts and ratings: a neutral warm gray, so blue keeps meaning
# "water level" (validated: one hue, monotone lightness, light end >= 2:1 on the surface).
RAMP_LIGHT = ["#b5b3ab", "#8a8882", "#5c5b56", "#2e2d2a"]
RAMP_DARK = ["#4a4945", "#75736d", "#a3a19a", "#d6d4cc"]

FONT_FAMILY = 'system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'


def palette(dark: bool = False) -> dict:
    """Return the color tokens for light (default) or dark mode."""
    return dict(_DARK if dark else _LIGHT)


# The three data types used on every map, in fixed slot order, so a data type
# is the same color everywhere in the app and report.
DATA_TYPE_ORDER = [
    "Water-level records",
    "Well construction and aquifer tests",
    "Surface-water stations",
]
_DATA_TYPE_SLOT = {
    "Water-level records": "blue",
    "Well construction and aquifer tests": "orange",
    "Surface-water stations": "aqua",
}


def data_type_color(data_type: str, dark: bool = False) -> str:
    return palette(dark)[_DATA_TYPE_SLOT[data_type]]


# ---------------------------------------------------------------------------
# Plotly templates
# ---------------------------------------------------------------------------
# Chart chrome (backgrounds, grid, fonts) lives in a *template*, not in each
# figure's layout. That matters for Streamlit: st.plotly_chart(theme="streamlit")
# swaps the template for Streamlit's own light/dark look but keeps every trace
# color we set explicitly.

def _template(dark: bool) -> go.layout.Template:
    p = palette(dark)
    axis = dict(
        showgrid=True,
        gridcolor=p["grid"],
        gridwidth=1,
        zeroline=False,
        showline=True,
        linecolor=p["axis"],
        linewidth=1,
        ticks="outside",
        tickcolor=p["axis"],
        ticklen=4,
        tickfont=dict(color=p["ink2"]),
        title=dict(font=dict(color=p["ink2"])),
        automargin=True,
    )
    return go.layout.Template(
        layout=dict(
            font=dict(family=FONT_FAMILY, size=14, color=p["ink"]),
            paper_bgcolor=p["surface"],
            plot_bgcolor=p["surface"],
            colorway=[p["blue"], p["orange"], p["aqua"]],
            xaxis=axis,
            yaxis=axis,
            legend=dict(
                font=dict(color=p["ink2"]),
                bgcolor="rgba(0,0,0,0)",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            hoverlabel=dict(font=dict(family=FONT_FAMILY, size=13)),
            margin=dict(l=70, r=30, t=50, b=60),
        )
    )


pio.templates["mesa_light"] = _template(False)
pio.templates["mesa_dark"] = _template(True)


def template_name(dark: bool = False) -> str:
    return "mesa_dark" if dark else "mesa_light"


# Marker and line sizes used across charts (kept thin and consistent).
LINE_WIDTH = 2
MARKER_SIZE = 9
MARKER_RING = 1.5  # ring in the surface color so overlapping dots stay readable
