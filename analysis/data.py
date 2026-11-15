"""Load the project's datasets into tidy pandas tables.

Every loader returns a table that starts with the project's shared columns
(``site_id, site_name, latitude, longitude, date, source``), the same
convention James uses for the files in ``data/clean/``.

Where the data come from
    * James's cleaned files in ``data/clean/``, made by his MATLAB script in
      ``cleaning/``: groundwater levels, aquifer tests, NMBGMR groundwater levels,
      Rio Puerco streamflow, well logs, and aquifer sensitivity. Loaders read them
      as they are and keep James's column names; they only add columns that are
      analysis results (such as ``year``, ``well_key``, or ``flowing``).
    * The other USGS series in dataset 1 (streamflow, reservoir storage, water
      quality), read from the raw file by ``load_usgs_stats``, which keeps one
      parameter and one interval type at a time. The raw files are never changed.

Every preparation step and decision is listed in ``docs/analysis.md`` under
"Data preparation inside the analysis code".

Loaders are cached (``lru_cache``) so the Streamlit app reads each file only
once. They return copies, so a chart can't accidentally change the cached table.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CLEAN = DATA / "clean"

# Approximate village center of Cuba, NM (decimal degrees).
CUBA = {"name": "Cuba", "latitude": 36.0195, "longitude": -106.9580}

# Approximate town locations, used only as map labels for orientation.
TOWNS = {
    "Cuba": (36.0195, -106.9580),
    "San Ysidro": (35.5600, -106.7700),
    "Jemez Springs": (35.7700, -106.6922),
    "Cochiti": (35.6100, -106.3470),
    "Bernalillo": (35.3000, -106.5511),
    "Rio Rancho": (35.2864, -106.6703),
    "Placitas": (35.3070, -106.4245),
}

USGS_STATS_FILE = DATA / "water_flow_data_sandoval_county_sources.csv"  # same copy James's script reads

SHARED = ["site_id", "site_name", "latitude", "longitude", "date", "source"]

USGS_PARAMETERS = {
    "00060": ("Streamflow", "ft³/s"),
    "00054": ("Reservoir storage", "acre-ft"),
    "00010": ("Water temperature", "°C"),
    "00095": ("Specific conductance", "µS/cm"),
    "00300": ("Dissolved oxygen", "mg/L"),
    "00400": ("pH", "pH units"),
    "63680": ("Turbidity", "FNU"),
    "80154": ("Suspended sediment concentration", "mg/L"),
    "80155": ("Suspended sediment discharge", "tons/day"),
    "72019": ("Depth to water", "ft below land surface"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def utm_to_latlon(easting, northing, zone: int = 13):
    """Convert UTM coordinates (meters, northern hemisphere) to latitude/longitude.

    Uses the standard inverse transverse Mercator series (Snyder 1987, USGS
    Professional Paper 1395) on the GRS80 ellipsoid used by NAD83. Checked
    against pyproj (EPSG:26913 to EPSG:4269): differences are under 1e-8
    degrees. All of Sandoval County lies in UTM zone 13.
    """
    a = 6378137.0
    f = 1 / 298.257222101
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    x = np.asarray(easting, dtype=float) - 500000.0
    y = np.asarray(northing, dtype=float)
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))
    e1 = (1 - np.sqrt(1 - e2)) / (1 + np.sqrt(1 - e2))
    phi1 = (
        mu
        + (3 * e1 / 2 - 27 * e1**3 / 32) * np.sin(2 * mu)
        + (21 * e1**2 / 16 - 55 * e1**4 / 32) * np.sin(4 * mu)
        + (151 * e1**3 / 96) * np.sin(6 * mu)
        + (1097 * e1**4 / 512) * np.sin(8 * mu)
    )
    c1 = ep2 * np.cos(phi1) ** 2
    t1 = np.tan(phi1) ** 2
    n1 = a / np.sqrt(1 - e2 * np.sin(phi1) ** 2)
    r1 = a * (1 - e2) / (1 - e2 * np.sin(phi1) ** 2) ** 1.5
    d = x / (n1 * k0)
    lat = phi1 - (n1 * np.tan(phi1) / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * ep2 - 3 * c1**2) * d**6 / 720
    )
    lon = (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * ep2 + 24 * t1**2) * d**5 / 120
    ) / np.cos(phi1)
    lon0 = np.radians((zone - 1) * 6 - 180 + 3)
    return np.degrees(lat), np.degrees(lon0 + lon)


def distance_km(lat, lon, lat0: float = CUBA["latitude"], lon0: float = CUBA["longitude"]):
    """Great-circle distance in km from (lat0, lon0); defaults to Cuba."""
    r = 6371.0
    p1, p2 = np.radians(lat0), np.radians(np.asarray(lat, dtype=float))
    dl = np.radians(np.asarray(lon, dtype=float) - lon0)
    h = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(h))


_WORD_FIXES = {
    "At": "at", "Near": "near", "Nr": "near", "N": "near", "Below": "below", "Bl": "below",
    "Abv": "above", "Above": "above", "In": "in", "Of": "of", "De": "de", "Los": "los",
    "Nm": "NM", "C": "Creek", "Cr": "Creek", "R": "River", "Res": "Reservoir", "Sps": "Springs",
    "Nat": "National", "Mon": "Monument", "Nfs-Baca": "NFS-Baca", "Bndry": "Boundary",
    "(At": "(at",
}


def tidy_site_name(name: str) -> str:
    """'RIO PUERCO AT CUBA, NM' -> 'Rio Puerco at Cuba, NM' (readable USGS names)."""
    text = str(name).strip()
    if text.endswith(" N M"):
        text = text[:-4] + ", NM"
    words = [_WORD_FIXES.get(w.title(), w.title()) for w in text.replace(",", " ,").split()]
    return " ".join(words).replace(" ,", ",")


def _well_label(site_name: str) -> tuple[str, str]:
    """Split a USGS well name like '12N.04E.29.433A SANDIA SITE' into
    ('Sandia site', 'Well A'). Wells with an A/B suffix share a location
    with the unsuffixed well but are measured at a different depth."""
    code, _, name = site_name.partition(" ")
    name = name.replace(" PIEZ 2", "").strip().title()
    name = name.replace("Site", "site").replace("Well", "well").replace("Middle School", "Middle School")
    suffix = code[-1] if code[-1].isalpha() else ""
    return name, (f"Well {suffix}" if suffix else "Well")


FORMATION_SHORT = {
    "ABO SANDSTONE": "Abo Sandstone",
    "SANTA FE GROUP": "Santa Fe Group",
    "MADERA LIMESTONE": "Madera Limestone",
    "OJO ALAMO SANDSTONE": "Ojo Alamo Sandstone",
    "ABIQUIU TUFF, LOWER PART OF SANTA FE GROUP": "Abiquiu Tuff (Santa Fe Group)",
    "ALLUVIUM, BOLSON DEPOSITS AND OTHER SURFACE DEPOSITS": "Alluvium and surface deposits",
    "POINT LOOKOUT SANDSTONE": "Point Lookout Sandstone",
    "MORRISON FORMATION": "Morrison Formation",
    # the cleaned file still has the misspelling NACIEMIENTO (see docs/data-cleaning.md)
    "AGUA ZARCA SANDSTONE MEMBER OF SIERRA NACIEMIENTO": "Agua Zarca Sandstone",
    "AGUA ZARCA SANDSTONE MEMBER OF SIERRA NACIMIENTO": "Agua Zarca Sandstone",
    "YESO FORMATION, MANZANO GROUP": "Yeso Formation",
    "MANCOS SHALE": "Mancos Shale",
    "MENEFEE FORMATION": "Menefee Formation",
    "GALLUP SANDSTONE": "Gallup Sandstone",
    "SAN JOSE FORMATION": "San Jose Formation",
    "TRES HERMANOS SANDSTONE MEMBER OF MANCOS SHALE": "Tres Hermanos Sandstone",
    "HOSTA TONGUE OF POINT LOOKOUT SANDSTONE OF MESAVERDE GROUP": "Hosta Tongue (Point Lookout)",
    "WESTWATER CANYON SANDSTONE MEMBER OF MORRISON FORMATION": "Westwater Canyon Sandstone",
    "CHUSKA SANDSTONE": "Chuska Sandstone",
    "ENTRADA": "Entrada Sandstone",
}


# ---------------------------------------------------------------------------
# Cleaned files (James)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _groundwater_levels() -> pd.DataFrame:
    df = pd.read_csv(CLEAN / "groundwater_levels_monthly.csv", dtype={"site_id": str}, parse_dates=["date"])
    labels = df["site_name"].map(_well_label)
    df["site_group"] = [lab[0] for lab in labels]
    df["well"] = [lab[1] for lab in labels]
    df["year"] = df["date"].dt.year
    return df


def load_groundwater_levels() -> pd.DataFrame:
    """USGS monthly mean depth to water, 9 wells at 4 sites, 1998-2026 (cleaned).

    Adds ``site_group`` (e.g. 'Sandia site'), ``well`` ('Well', 'Well A', 'Well B'),
    and ``year``. ``depth_to_water_ft`` is depth below land surface, so a larger
    number means a LOWER water table.
    """
    return _groundwater_levels().copy()


@lru_cache(maxsize=None)
def _aquifer_tests() -> pd.DataFrame:
    df = pd.read_csv(CLEAN / "aquifer_tests.csv", dtype={"site_id": str}, parse_dates=["date"])
    # site_id is incomplete in the raw OSE file (85 tests are just "RG--"), so
    # wells are told apart by name + location, as docs/data-cleaning.md advises.
    df["well_key"] = (
        df["site_name"].fillna("(unnamed)")
        + " @ "
        + df["latitude"].round(5).astype(str)
        + ","
        + df["longitude"].round(5).astype(str)
    )
    # The same test is sometimes entered twice under one name with slightly different
    # coordinates (e.g. BIA-(RF)-033-2(10) Smelser Well, 8.8 and 9.1 km from Cuba, same date,
    # depth, and water level). Rows with the same name and date within 1 km are one well.
    for (_name, _date), grp in df.dropna(subset=["site_name"]).groupby(["site_name", "date"]):
        keys = grp["well_key"].unique()
        if len(keys) > 1:
            first = grp.iloc[0]
            near = distance_km(grp["latitude"], grp["longitude"], first["latitude"], first["longitude"]) <= 1.0
            df.loc[grp.index[near], "well_key"] = first["well_key"]
    df["formation_short"] = df["formation"].map(FORMATION_SHORT).fillna(df["formation"].str.title())
    df["year"] = df["date"].dt.year
    df["distance_from_cuba_km"] = distance_km(df["latitude"], df["longitude"])
    return df


def load_aquifer_tests() -> pd.DataFrame:
    """NM OSE aquifer tests in Sandoval County, 179 tests, 1930-2008 (cleaned).

    Adds ``well_key`` (name + location; use it instead of ``site_id`` to tell
    wells apart), ``formation_short`` (readable formation name), ``year``, and
    ``distance_from_cuba_km``.
    """
    return _aquifer_tests().copy()


# ---------------------------------------------------------------------------
# More cleaned files (James)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _nmbgmr_levels() -> pd.DataFrame:
    df = pd.read_csv(CLEAN / "groundwater_levels_nmbgmr.csv", dtype={"site_id": str},
                     parse_dates=["date", "completion_date"])
    return df.sort_values(["site_id", "date"]).reset_index(drop=True)


def load_nmbgmr_levels() -> pd.DataFrame:
    """NM Bureau of Geology depth-to-water measurements: 451 readings, 87 wells, 1997-2019 (cleaned).

    The raw file (``data2_groundwater_sandoval_county.csv``) has 456 rows; the cleaning
    drops the 5 with no depth (wells recorded dry). This source has no well names, so
    ``site_name`` is blank and charts label wells by ``site_id``. ``level_status`` 'R'
    means the well had recently been pumped.
    """
    return _nmbgmr_levels().copy()


@lru_cache(maxsize=None)
def _rio_puerco() -> pd.DataFrame:
    df = pd.read_csv(CLEAN / "streamflow_measurements.csv", dtype={"site_id": str}, parse_dates=["date"])
    df["flowing"] = df["discharge_cfs"] > 0
    return df.sort_values("date").reset_index(drop=True)


def load_rio_puerco() -> pd.DataFrame:
    """USGS 08332525 Rio Puerco at Cuba: 10 discrete streamflow visits, 2019-2026 (cleaned).

    Adds ``flowing`` (``discharge_cfs`` above 0). A ``measurement_type`` of 'Other'
    means the visit found no measurable flow. These are spot visits, not a
    continuous record.
    """
    return _rio_puerco().copy()


@lru_cache(maxsize=None)
def _well_logs() -> pd.DataFrame:
    return pd.read_csv(CLEAN / "well_logs.csv", dtype={"site_id": str},
                       parse_dates=["date", "start_date", "log_file_date"])


def load_well_logs() -> pd.DataFrame:
    """NM OSE well logs coded to Sandoval County: 6 wells, finished 1979-2022 (cleaned).

    ``date`` is when drilling finished (``start_date`` is when it began).
    ``depth_to_first_water_ft`` is where water was first found while drilling, not a
    current water level. ``site_name`` is blank, so charts label wells by POD number
    (``site_id``). SJ 04455 POD1 has no latitude/longitude: its UTM coordinates fall
    outside Sandoval County, probably a typo in the northing.
    """
    return _well_logs().copy()


@lru_cache(maxsize=None)
def _usgs_stats() -> pd.DataFrame:
    return pd.read_csv(USGS_STATS_FILE, dtype={"parameter_code": str, "monitoring_location_id": str})


def load_usgs_stats(parameter_code: str, interval_type: str = "month") -> pd.DataFrame:
    """One USGS parameter from dataset 1 (raw), in the shared schema.

    ``interval_type`` is 'month', 'calendar_year', or 'water_year'. Use one
    interval type at a time: they summarize the same measurements. Keeps the
    central statistic only (Mean, or Median for pH, or SelectedValue for
    reservoir storage), so there is one value per site and period.
    """
    raw = _usgs_stats()
    raw = raw[(raw["parameter_code"] == parameter_code) & (raw["interval_type"] == interval_type)]
    raw = raw[raw["parent_statistic_name"].isin(["Mean", "Median", "SelectedValue"])]
    value = raw["arithmetic_mean"].fillna(raw["median"])
    name, unit = USGS_PARAMETERS.get(parameter_code, (parameter_code, ""))
    df = pd.DataFrame(
        {
            "site_id": raw["monitoring_location_id"],
            "site_name": raw["monitoring_location_name"],
            "latitude": raw["y"],
            "longitude": raw["x"],
            "date": pd.to_datetime(raw["start_date"]),
            "source": "USGS",
            "site_type": raw["site_type"],
            "parameter": name,
            "unit": unit,
            "value": value,
            "sample_count": raw["arithmetic_mean_sample_count"],
        }
    )
    return df.dropna(subset=["value"]).sort_values(["site_id", "date"]).reset_index(drop=True)


def load_usgs_sites() -> pd.DataFrame:
    """One row per USGS site in dataset 1, with type, parameters, and record years."""
    raw = _usgs_stats()
    m = raw[raw["interval_type"] == "month"].copy()
    m["year"] = m["start_date"].str[:4].astype(int)
    m["param_name"] = m["parameter_code"].map(lambda c: USGS_PARAMETERS.get(c, (c, ""))[0])
    sites = m.groupby("monitoring_location_id").agg(
        site_name=("monitoring_location_name", "first"),
        site_type=("site_type", "first"),
        latitude=("y", "first"),
        longitude=("x", "first"),
        first_year=("year", "min"),
        last_year=("year", "max"),
        n_months=("start_date", "nunique"),
        parameters=("param_name", lambda s: ", ".join(sorted(set(s)))),
    )
    return sites.reset_index().rename(columns={"monitoring_location_id": "site_id"})


def load_county_boundary() -> dict:
    """Simplified Sandoval County outline (GeoJSON) for map context.

    From the US Census Bureau 2010 cartographic boundary file as redistributed
    in plotly/datasets (geojson-counties-fips.json, FIPS 35043).
    """
    with open(DATA / "sandoval_county_boundary.geojson", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Combined tables
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _monitoring_points() -> pd.DataFrame:
    rows = []

    gw = load_groundwater_levels()
    g = gw.groupby("site_id").agg(
        name=("site_name", "first"), latitude=("latitude", "first"), longitude=("longitude", "first"),
        first_year=("year", "min"), last_year=("year", "max"), n_records=("date", "size"),
    ).reset_index()
    g["dataset"] = "USGS monitoring wells (monthly)"
    g["data_type"] = "Water-level records"
    g["detail"] = g["n_records"].astype(str) + " monthly means"
    rows.append(g)

    nm = load_nmbgmr_levels().dropna(subset=["depth_to_water_ft"])
    nm["year"] = nm["date"].dt.year
    n = nm.groupby("site_id").agg(
        name=("site_name", "first"), latitude=("latitude", "first"), longitude=("longitude", "first"),
        first_year=("year", "min"), last_year=("year", "max"), n_records=("date", "size"),
    ).reset_index()
    n["name"] = n["name"].fillna(n["site_id"])
    n["dataset"] = "NMBGMR well measurements"
    n["data_type"] = "Water-level records"
    n["detail"] = n["n_records"].astype(str) + " depth-to-water readings"
    rows.append(n)

    at = load_aquifer_tests()
    a = at.groupby("well_key").agg(
        name=("site_name", "first"), latitude=("latitude", "first"), longitude=("longitude", "first"),
        first_year=("year", "min"), last_year=("year", "max"), n_records=("date", "size"),
        formation=("formation_short", "first"),
    ).reset_index().rename(columns={"well_key": "site_id"})
    a["name"] = a["name"].fillna("(unnamed well)")
    a["dataset"] = "OSE aquifer tests"
    a["data_type"] = "Well construction and aquifer tests"
    a["detail"] = a["n_records"].astype(str) + " test(s); formation: " + a["formation"].fillna("not recorded")
    rows.append(a.drop(columns="formation"))

    wl = load_well_logs().dropna(subset=["latitude"])
    w = pd.DataFrame(
        {
            "site_id": wl["site_id"], "name": wl["site_name"].fillna(wl["site_id"]), "latitude": wl["latitude"],
            "longitude": wl["longitude"], "first_year": wl["date"].dt.year, "last_year": wl["date"].dt.year,
            "n_records": 1, "dataset": "OSE well logs", "data_type": "Well construction and aquifer tests",
            "detail": "drilled " + wl["date"].dt.year.astype(str) + ", " + wl["borehole_depth_ft"].astype(int).astype(str) + " ft deep",
        }
    )
    rows.append(w)

    us = load_usgs_sites()
    us = us[us["site_type"] != "Well"]
    s = pd.DataFrame(
        {
            "site_id": us["site_id"], "name": us["site_name"].map(tidy_site_name),
            "latitude": us["latitude"], "longitude": us["longitude"], "first_year": us["first_year"],
            "last_year": us["last_year"], "n_records": us["n_months"],
            "dataset": "USGS surface-water statistics", "data_type": "Surface-water stations",
            "detail": us["site_type"] + ": " + us["parameters"],
        }
    )
    rows.append(s)

    rp = load_rio_puerco()
    rows.append(
        pd.DataFrame(
            {
                "site_id": [rp["site_id"].iloc[0]], "name": [tidy_site_name(rp["site_name"].iloc[0])],
                "latitude": [rp["latitude"].iloc[0]], "longitude": [rp["longitude"].iloc[0]],
                "first_year": [rp["date"].dt.year.min()], "last_year": [rp["date"].dt.year.max()],
                "n_records": [len(rp)], "dataset": ["USGS Rio Puerco at Cuba (visits)"],
                "data_type": ["Surface-water stations"],
                "detail": [f"{len(rp)} streamflow visits ({int(rp['flowing'].sum())} with flow)"],
            }
        )
    )

    out = pd.concat(rows, ignore_index=True)
    out["distance_from_cuba_km"] = distance_km(out["latitude"], out["longitude"])
    cols = ["dataset", "data_type", "site_id", "name", "latitude", "longitude",
            "first_year", "last_year", "n_records", "detail", "distance_from_cuba_km"]
    return out[cols]


def load_monitoring_points() -> pd.DataFrame:
    """Every mapped site from every dataset, one row per site, with its data type.

    Data types (used for map colors): 'Water-level records' (USGS monitoring wells,
    NMBGMR wells), 'Well construction and aquifer tests' (OSE aquifer tests,
    OSE well logs), and 'Surface-water stations' (USGS stream, canal, and
    reservoir sites, and Rio Puerco at Cuba).
    """
    return _monitoring_points().copy()


def in_county(lat, lon) -> np.ndarray:
    """True where a point falls inside the (simplified) Sandoval County outline.
    Standard ray-casting point-in-polygon test on the boundary GeoJSON."""
    geom = load_county_boundary()["features"][0]["geometry"]
    rings = geom["coordinates"] if geom["type"] == "Polygon" else [r for poly in geom["coordinates"] for r in poly]
    ring = np.asarray(rings[0], dtype=float)
    x, y = np.asarray(lon, dtype=float), np.asarray(lat, dtype=float)
    inside = np.zeros(x.shape, dtype=bool)
    xs, ys = ring[:, 0], ring[:, 1]
    j = len(ring) - 1
    for i in range(len(ring)):
        crosses = ((ys[i] > y) != (ys[j] > y)) & (x < (xs[j] - xs[i]) * (y - ys[i]) / (ys[j] - ys[i] + 1e-12) + xs[i])
        inside ^= crosses
        j = i
    return inside
