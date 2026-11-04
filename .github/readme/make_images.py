"""Make the chart images shown in the repository's README.md.

Each chart is drawn twice: on GitHub's light background with dark text
(``<key>_light.png``) and on its dark background with light text
(``<key>_dark.png``), each as a card with rounded corners and a thin border.
README.md shows the one that matches the reader's light or dark setting with a
``<picture>`` element. That setting comes from the reader's device, so a reader
whose GitHub theme differs from their device still gets a readable card, just
in the other theme. The charts come from ``analysis/charts.py``, so the numbers
match the app, the report, and the documentation site.

Run from the repository root after the charts change:

    pip install kaleido
    python .github/readme/make_images.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import io  # noqa: E402

import numpy as np  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from analysis import charts  # noqa: E402
from analysis.charts import _plot_left_px, _wrap  # noqa: E402
from analysis.theme import palette, template_name  # noqa: E402

README_CHARTS = ["groundwater_hydrographs", "cuba_area_map", "county_coverage_map"]
OUT_DIR = Path(__file__).resolve().parent
CLEAR = "rgba(0,0,0,0)"
# GitHub's page background and border colors in its light and dark themes
CARD = {False: ("#ffffff", "#d0d7de"), True: ("#0d1117", "#30363d")}
# A map style with no tiles and a see-through background (the charts' static maps
# otherwise use Plotly's "white-bg" style, which stays white in the dark version).
CLEAR_MAP_STYLE = {"version": 8, "sources": {}, "layers": [
    {"id": "background", "type": "background", "paint": {"background-color": CLEAR}}]}


def themed_static(c: charts.Chart, dark: bool, width: int = 1000) -> go.Figure:
    """The same layout as ``Chart.static()`` (title, subtitle, and footer baked in),
    in the light or dark theme, with a transparent background."""
    p = palette(dark)
    fig = go.Figure(c.fig)
    m = fig.layout.margin
    base_t = m.t if m.t is not None else 50
    base_b = m.b if m.b is not None else 60
    base_l = m.l if m.l is not None else 70
    title = _wrap(c.title, int(width / 11.2))
    subtitle = _wrap(c.subtitle, int(width / 8.3))
    title_h = 27 * (title.count("<br>") + 1) + 20 * (subtitle.count("<br>") + 1) + 30
    foot = _wrap(f"Scope: {c.scope}.  Source: {c.source}", int(width / 6.4))
    foot_h = 17 * (foot.count("<br>") + 1) + 22
    fig.update_layout(
        template=template_name(dark),
        width=width,
        height=c.height + title_h + foot_h,
        margin=dict(t=base_t + title_h, b=base_b + foot_h, l=base_l),
        font=dict(size=15),
        paper_bgcolor=CLEAR,
        plot_bgcolor=CLEAR,
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:14.5px;color:{p['ink2']}'>{subtitle}</span>",
            x=0, xref="container", xanchor="left", y=1, yref="container", yanchor="top",
            pad=dict(l=22, t=18), font=dict(size=19.5, color=p["ink"]),
        ),
    )
    if any(t.type == "scattermap" for t in fig.data):
        fig.update_layout(map_style=CLEAR_MAP_STYLE)
    plot_left = _plot_left_px(fig, base_l)
    fig.add_annotation(
        text=f"<span style='color:{p['muted']}'>{foot}</span>",
        xref="paper", yref="paper", x=0, y=0, xshift=-(plot_left - 22), yshift=-(base_b + 6),
        xanchor="left", yanchor="top", showarrow=False, align="left", font=dict(size=12),
    )
    return fig


def remove_map_attribution_box(png: bytes) -> bytes:
    """Plotly's maps draw an empty attribution box (a small half-white rectangle) in
    the corner of the map. It's invisible on white but shows on a dark page, so make
    any small, solid rectangle of exactly that color transparent."""
    img = np.array(Image.open(io.BytesIO(png)).convert("RGBA"))
    mask = np.all(img == (255, 255, 255, 191), axis=2)
    seen = np.zeros_like(mask)
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        x1 = x
        while x1 + 1 < mask.shape[1] and mask[y, x1 + 1]:
            x1 += 1
        y1 = y
        while y1 + 1 < mask.shape[0] and mask[y1 + 1, x:x1 + 1].all():
            y1 += 1
        seen[y:y1 + 1, x:x1 + 1] = True
        if 6 <= x1 - x + 1 <= 60 and 4 <= y1 - y + 1 <= 30:
            img[y:y1 + 1, x:x1 + 1, 3] = 0
    out = io.BytesIO()
    Image.fromarray(img).save(out, format="PNG", optimize=True)
    return out.getvalue()


def card(png: bytes, dark: bool, radius: int = 24, border: int = 2) -> bytes:
    """Put the transparent chart on GitHub's background color for its theme, with
    rounded corners and a thin border, so it reads as a figure on any page."""
    bg, line = CARD[dark]
    chart = Image.open(io.BytesIO(png)).convert("RGBA")
    w, h = chart.size
    out = Image.new("RGBA", (w, h), bg)
    out.alpha_composite(chart)
    ImageDraw.Draw(out).rounded_rectangle((0, 0, w - 1, h - 1), radius, outline=line, width=border)
    big = Image.new("L", (w * 4, h * 4), 0)  # drawn large and shrunk, for smooth corners
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), radius * 4, fill=255)
    out.putalpha(big.resize((w, h), Image.LANCZOS))
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


if __name__ == "__main__":
    for key in README_CHARTS:
        for dark in (False, True):
            chart = getattr(charts, key)(dark=dark)
            path = OUT_DIR / f"{key}_{'dark' if dark else 'light'}.png"
            fig = themed_static(chart, dark)
            png = fig.to_image(format="png", scale=2)
            if any(t.type == "scattermap" for t in fig.data):
                png = remove_map_attribution_box(png)
            path.write_bytes(card(png, dark))
            print(f"  wrote {path.relative_to(ROOT)}")
