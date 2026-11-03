"""Small flat pictograms for the pictograph versions of the charts.

Why pictograms?
    Some charts read faster when a mark looks like the thing it stands for: a
    well, a stream gage, a river visit. The pictograph versions are used in the
    Streamlit app and the slide/docs images; the LaTeX report keeps the plain
    versions (see ``charts.PICTOGRAPH_CHARTS``).

Rules, so the pictograms add meaning without bending the data
    * One pictogram = one real thing (a well, a site, a visit), or one fixed unit
      (one visit, 1% of an area). Never a decoration.
    * Sizes come from data only through stated classes or areas, always with a
      key on the chart. A pictogram's *area* is what grows, not its height.
    * Flat shapes, one color each, from the project palette in ``theme.py``, so a
      color means the same thing as on every other chart. No faces, 3D, or clip art.
    * The glyphs are standard hydrology symbols where one exists (the inverted
      triangle for a water table; a well casing; a cone of depression for a
      pumping test; wavy lines for surface water).

Every glyph is drawn on a 100 x 100 grid (y points down) from a few primitives,
so the same drawing becomes an SVG (sharp at any size, used on ordinary charts)
or a PNG (used on the interactive maps, whose image layers need a bitmap).
"""

from __future__ import annotations

import base64
import io
import math
from functools import lru_cache

# ---------------------------------------------------------------------------
# Glyph geometry (100 x 100 grid). Primitives:
#   ("rect", x0, y0, x1, y1, radius)     filled rounded rectangle
#   ("poly", [(x, y), ...])              filled polygon
#   ("line", [(x, y), ...], width)       stroked polyline (round ends)
#   ("circle", cx, cy, r)                filled circle
#   ("ring", cx, cy, r, width)           stroked circle
#   ("wedge", cx, cy, r, fraction)       filled pie slice clockwise from 12 o'clock
# ---------------------------------------------------------------------------


def _wave(y: float, x0: float = 24, x1: float = 76, amp: float = 4.5, waves: float = 1.5, n: int = 24):
    return [(x0 + (x1 - x0) * i / n, y + amp * math.sin(2 * math.pi * waves * i / n)) for i in range(n + 1)]


def _cone(x0: float, x1: float, y0: float = 49, depth: float = 17, width: float = 12, n: int = 16):
    """Half of a cone of depression: the water table dipping toward a pumped well at x = 50."""
    return [(x, y0 + depth * math.exp(-((x - 50) / width) ** 2))
            for x in (x0 + (x1 - x0) * i / n for i in range(n + 1))]


def _drop_outline(cx: float = 50, cy: float = 62, r: float = 30, tip_y: float = 6, n: int = 40):
    """Teardrop: a circle plus the two tangent lines to a tip straight above it."""
    dist = cy - tip_y
    a = math.asin(r / dist)                 # half-angle at the tip
    t = math.pi / 2 - a                     # tangent points, measured from the upward vertical at the center
    pts = [(cx, tip_y)]
    for i in range(n + 1):                  # sweep around the bottom from the right tangent to the left one
        ang = -math.pi / 2 + t + (2 * math.pi - 2 * t) * i / n
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


GLYPHS = {
    # aquifer-test well: wellhead, casing, and the cone of depression a pumping test makes
    "test_well": [
        ("rect", 36, 21, 64, 29, 2),
        ("rect", 45, 29, 55, 81, 2),
        ("line", _cone(18, 43), 5.5),
        ("line", _cone(57, 82), 5.5),
    ],
    # well log (drilling record): casing with a log strip beside it
    "well_log": [
        ("rect", 31, 22, 55, 30, 2),
        ("rect", 38, 30, 48, 80, 2),
        ("line", [(57, 42), (70, 42)], 6),
        ("line", [(57, 54), (77, 54)], 6),
        ("line", [(57, 66), (66, 66)], 6),
    ],
    # water-level record: the hydrogeology water-table symbol
    "water_level": [
        ("poly", [(31, 31), (69, 31), (50, 56)]),
        ("line", [(33, 66), (67, 66)], 6),
        ("line", [(41, 76), (59, 76)], 6),
    ],
    # surface-water station: wavy lines
    "stream": [
        ("line", _wave(37), 6),
        ("line", _wave(51), 6),
        ("line", _wave(65), 6),
    ],
    # one river visit
    "drop": [("poly", _drop_outline())],
}


# ---------------------------------------------------------------------------
# Composition: a glyph alone, or a glyph on a round badge
# ---------------------------------------------------------------------------

def _badge(glyph: str, fill: str, ring: str | None, hollow: bool, glyph_color: str | None):
    """Shapes for a round badge with the glyph inside. Hollow = outline only
    (used for 'value not recorded')."""
    if hollow:
        shapes = [("ring", 50, 50, 44, 7, fill)]
        gcol = glyph_color or fill
    else:
        shapes = [("circle", 50, 50, 47, fill)]
        if ring:
            shapes.append(("ring", 50, 50, 47, 5, ring))
        gcol = glyph_color or "#ffffff"
    for prim in GLYPHS[glyph]:
        shapes.append((*prim, gcol))
    return shapes


def _plain(glyph: str, color: str, hollow: bool = False, stroke: float = 6):
    """A glyph by itself (no badge). Hollow turns filled polygons into outlines."""
    out = []
    for prim in GLYPHS[glyph]:
        if hollow and prim[0] == "poly":
            out.append(("line", list(prim[1]) + [prim[1][0]], stroke, color))
        else:
            out.append((*prim, color))
    return out


def _harvey(fraction: float, color: str, empty: str):
    """Harvey ball: an outlined circle filled clockwise by `fraction` (0-1)."""
    shapes = [("circle", 50, 50, 44, empty)]
    if fraction >= 0.999:
        shapes.append(("circle", 50, 50, 44, color))
    elif fraction > 0:
        shapes.append(("wedge", 50, 50, 44, fraction, color))
    shapes.append(("ring", 50, 50, 44, 6, color))
    return shapes


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def _svg(shapes) -> str:
    parts = []
    for s in shapes:
        kind, color = s[0], s[-1]
        if kind == "rect":
            x0, y0, x1, y1, r = s[1:6]
            parts.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{color}"/>')
        elif kind == "poly":
            pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in s[1])
            parts.append(f'<polygon points="{pts}" fill="{color}"/>')
        elif kind == "line":
            pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in s[1])
            parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{s[2]}" '
                         'stroke-linecap="round" stroke-linejoin="round"/>')
        elif kind == "circle":
            parts.append(f'<circle cx="{s[1]}" cy="{s[2]}" r="{s[3]}" fill="{color}"/>')
        elif kind == "ring":
            parts.append(f'<circle cx="{s[1]}" cy="{s[2]}" r="{s[3]}" fill="none" stroke="{color}" stroke-width="{s[4]}"/>')
        elif kind == "wedge":
            cx, cy, r, f = s[1:5]
            ang = 2 * math.pi * f
            x1, y1 = cx + r * math.sin(ang), cy - r * math.cos(ang)
            large = 1 if f > 0.5 else 0
            parts.append(f'<path d="M{cx},{cy} L{cx},{cy - r} A{r},{r} 0 {large} 1 {x1:.2f},{y1:.2f} Z" fill="{color}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
            + "".join(parts) + "</svg>")


def _png(shapes, px: int) -> bytes:
    """Rasterize with Pillow (installed with Streamlit), supersampled for smooth edges."""
    from PIL import Image, ImageDraw  # imported here so the rest of the module needs no Pillow

    k = px * 4 / 100.0
    im = Image.new("RGBA", (px * 4, px * 4), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for s in shapes:
        kind, color = s[0], s[-1]
        if kind == "rect":
            x0, y0, x1, y1, r = s[1:6]
            dr.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k, fill=color)
        elif kind == "poly":
            dr.polygon([(x * k, y * k) for x, y in s[1]], fill=color)
        elif kind == "line":
            w = max(int(round(s[2] * k)), 1)
            pts = [(x * k, y * k) for x, y in s[1]]
            dr.line(pts, fill=color, width=w, joint="curve")
            for x, y in (pts[0], pts[-1]):  # round caps
                dr.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=color)
        elif kind == "circle":
            cx, cy, r = s[1:4]
            dr.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=color)
        elif kind == "ring":
            cx, cy, r, w = s[1:5]
            dr.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], outline=color, width=int(round(w * k)))
        elif kind == "wedge":
            cx, cy, r, f = s[1:5]
            dr.pieslice([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], -90, -90 + 360 * f, fill=color)
    im = im.resize((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _uri_svg(shapes) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(_svg(shapes).encode()).decode()


def _uri_png(shapes, px: int) -> str:
    return "data:image/png;base64," + base64.b64encode(_png(shapes, px)).decode()


# ---------------------------------------------------------------------------
# Public helpers (cached: the same pictogram is reused many times per chart)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def badge_svg(glyph: str, fill: str, ring: str | None = None, hollow: bool = False,
              glyph_color: str | None = None) -> str:
    """Round badge with a glyph, as an SVG data URI (for charts with x/y axes)."""
    return _uri_svg(_badge(glyph, fill, ring, hollow, glyph_color))


@lru_cache(maxsize=None)
def badge_png(glyph: str, fill: str, ring: str | None = None, hollow: bool = False,
              glyph_color: str | None = None, px: int = 96) -> str:
    """Round badge with a glyph, as a PNG data URI (for map image layers)."""
    return _uri_png(_badge(glyph, fill, ring, hollow, glyph_color), px)


@lru_cache(maxsize=None)
def glyph_svg(glyph: str, color: str, hollow: bool = False) -> str:
    """A glyph alone, as an SVG data URI (e.g. a filled or outlined drop)."""
    return _uri_svg(_plain(glyph, color, hollow))


@lru_cache(maxsize=None)
def harvey_svg(fraction: float, color: str, empty: str) -> str:
    """Harvey ball for a rating, as an SVG data URI."""
    return _uri_svg(_harvey(fraction, color, empty))


@lru_cache(maxsize=None)
def label_png(text: str, ink: str, halo: str, px_h: int = 44) -> tuple[str, float]:
    """A short text label as a PNG data URI, with a halo in the background color so it
    stays readable over a basemap or another pictogram. Returns (uri, width / height).
    Used for counts and tags on the maps: as an image it scales with the map and is never
    hidden by the map's label-collision rules, unlike map text."""
    from PIL import Image, ImageDraw, ImageFont

    k = 3
    size = int(px_h * k * 0.72)
    try:
        font = ImageFont.load_default(size=size)       # Pillow >= 10.1: a scalable built-in font
    except TypeError:                                   # older Pillow: small bitmap font
        font = ImageFont.load_default()
    stroke = max(int(size * 0.16), 1)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=font, stroke_width=stroke)
    w, h = x1 - x0 + 2 * stroke, px_h * k
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((stroke - x0, (h - (y1 - y0)) / 2 - y0), text, font=font, fill=ink,
                            stroke_width=stroke, stroke_fill=halo)
    im = im.resize((max(w // k, 1), px_h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.width / im.height


def km_rect(lat: float, lon: float, w_km: float, h_km: float, x_left_km: float) -> list:
    """Corners of a w x h km rectangle whose left edge is x_left_km east of (lat, lon) and
    which is vertically centered on it (for map labels beside a pictogram)."""
    deg_lat = h_km / 110.574 / 2
    kx = 111.320 * math.cos(math.radians(lat))
    l, r = lon + x_left_km / kx, lon + (x_left_km + w_km) / kx
    return [[l, lat + deg_lat], [r, lat + deg_lat], [r, lat - deg_lat], [l, lat - deg_lat]]


def km_box(lat: float, lon: float, km: float, dx_km: float = 0.0, dy_km: float = 0.0) -> list:
    """Corner coordinates [[lon, lat] x 4: top-left, top-right, bottom-right,
    bottom-left] of a km x km square centered on (lat, lon), optionally shifted
    east/north by dx_km/dy_km. Used to place a pictogram on a map."""
    lat_c = lat + dy_km / 110.574
    deg_lat = km / 110.574 / 2
    deg_lon = km / (111.320 * math.cos(math.radians(lat_c))) / 2
    lon_c = lon + dx_km / (111.320 * math.cos(math.radians(lat_c)))
    return [[lon_c - deg_lon, lat_c + deg_lat], [lon_c + deg_lon, lat_c + deg_lat],
            [lon_c + deg_lon, lat_c - deg_lat], [lon_c - deg_lon, lat_c - deg_lat]]


def spread_offsets(n: int, step_km: float) -> list[tuple[float, float]]:
    """Offsets (east, north, km) that spread n pictograms sharing one location
    around it, so each stays visible: one in the middle, the rest on a ring."""
    if n <= 1:
        return [(0.0, 0.0)]
    if n <= 4:
        r = step_km * 0.62
        return [(r * math.cos(2 * math.pi * i / n + math.pi / 4), r * math.sin(2 * math.pi * i / n + math.pi / 4))
                for i in range(n)]
    r = step_km * 1.05
    return [(0.0, 0.0)] + [(r * math.cos(2 * math.pi * i / (n - 1) + math.pi / 2),
                            r * math.sin(2 * math.pi * i / (n - 1) + math.pi / 2)) for i in range(n - 1)]
