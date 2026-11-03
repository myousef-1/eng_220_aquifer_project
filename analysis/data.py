"""Load the project's datasets into tidy pandas tables.

Every loader returns a table that starts with the project's shared columns
(``site_id, site_name, latitude, longitude, date, source``), the same
convention James uses for the files in ``data/clean/``.

Two kinds of loaders
    * Cleaned files (``data/clean/``), made by James's ``cleaning/clean_csvs.m``:
      ``load_groundwater_levels`` and ``load_aquifer_tests``.
    * Raw files that are not cleaned yet. For these, the loader does only the
      minimum preparation needed to chart them (convert UTM coordinates to
      latitude/longitude, parse dates, rename columns). The raw files are never
      changed. When James adds a cleaned version of one of these, swap the loader
      body for a ``pd.read_csv`` of the cleaned file; the chart code won't need
      to change because the column names already follow the conventions.

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
# Raw files, minimal preparation (not yet cleaned by James)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _nmbgmr_levels() -> pd.DataFrame:
    raw = pd.read_csv(DATA / "data2_groundwater_sandoval_county.csv", na_values=["NULL"])
    # UTMDatum is NAD83 for every row; Sandoval County is entirely in UTM zone 13.
    lat, lon = utm_to_latlon(raw["Easting"], raw["Northing"], zone=13)
    df = pd.DataFrame(
        {
            "site_id": raw["PointID"].astype(str),
            "site_name": raw["PointID"].astype(str),
            "latitude": lat,
            "longitude": lon,
            "date": pd.to_datetime(raw["DateMeasured"]).dt.normalize(),
            "source": "NMBGMR",
            "well_depth_ft": raw["WellDepth"],
            "hole_depth_ft": raw["HoleDepth"],
            "depth_to_water_ft": raw["DepthToWaterBGS"],
            "level_status": raw["LevelStatus"],
            "altitude_ft": raw["Altitude"],
        }
    )
    df["area"] = np.select(
        [df["site_id"].str.startswith("PC-"), df["site_id"].str.startswith("PB-")],
        ["Placitas", "Peña Blanca"],
        default="Other",
    )
    return df.sort_values(["site_id", "date"]).reset_index(drop=True)


def load_nmbgmr_levels() -> pd.DataFrame:
    """NM Bureau of Geology depth-to-water measurements: 456 rows, 87 wells, 1997-2019.

    Raw file ``data2_groundwater_sandoval_county.csv``; prepared in code:
    UTM zone 13 (NAD83) converted to latitude/longitude, 'NULL' read as blank,
    dates parsed. Rows with a blank depth (wells recorded dry, ``level_status`` 'D')
    are kept so counts match the raw file; charts drop them.
    """
    return _nmbgmr_levels().copy()


@lru_cache(maxsize=None)
def _rio_puerco() -> pd.DataFrame:
    meta = pd.read_csv(DATA / "data4_monitoring-location-metadata.csv")
    flow = pd.read_csv(DATA / "data4_channel-measurements.csv")
    stage = pd.read_csv(DATA / "data4_field-measurements.csv")
    stage = stage.rename(columns={"value": "gage_height_ft"})[["field_visit_id", "gage_height_ft"]]
    # Times are UTC; convert to local time before taking the calendar date.
    when = pd.to_datetime(flow["time"], utc=True).dt.tz_convert("America/Denver")
    df = pd.DataFrame(
        {
            "site_id": flow["monitoring_location_id"],
            "site_name": tidy_site_name(meta.loc[0, "monitoring_location_name"]),
            "latitude": flow["y"],
            "longitude": flow["x"],
            "date": when.dt.tz_localize(None).dt.normalize(),
            "source": "USGS",
            "flow_cfs": flow["channel_flow"].astype(float),
            "measurement_method": flow["measurement_type"].replace({"Other": "Observed (no measurable flow)"}),
            "field_visit_id": flow["field_visit_id"],
        }
    ).merge(stage, on="field_visit_id", how="left").drop(columns="field_visit_id")
    df["flowing"] = df["flow_cfs"] > 0
    return df.sort_values("date").reset_index(drop=True)


def load_rio_puerco() -> pd.DataFrame:
    """USGS 08332525 Rio Puerco at Cuba: 10 discrete streamflow visits, 2019-2026.

    Raw ``data4_*`` files; prepared in code: joined the 4 gage-height readings
    to their visits, converted UTC times to local dates, flagged visits with
    flow > 0. These are spot visits, not a continuous record.
    """
    return _rio_puerco().copy()


@lru_cache(maxsize=None)
def _well_logs() -> pd.DataFrame:
    raw = pd.read_csv(DATA / "data7_Wells With Well Log Information.csv", dtype=str)
    raw = raw[raw["County"].notna()].copy()  # last line of the file is a footnote
    plss_flag = raw.iloc[:, 13].fillna("").str.strip() == "*"
    x = raw["X"].astype(float)
    y = raw["Y"].astype(float)
    lat, lon = utm_to_latlon(x, y, zone=13)
    df = pd.DataFrame(
        {
            "site_id": raw["POD Number"].str.split().str.join(" "),
            "site_name": raw["POD Number"].str.split().str.join(" "),
            "latitude": lat,
            "longitude": lon,
            "date": pd.to_datetime(raw["Start Date"]),
            "source": "NM OSE",
            "borehole_depth_ft": pd.to_numeric(raw["Borehole Depth"], errors="coerce"),
            "first_water_ft": pd.to_numeric(raw["Depth Water First Encountered"], errors="coerce"),
            "location_from_plss": plss_flag.values,
            "plss": (raw["Sec"] + " " + raw["Tws"] + " " + raw["Range"]).values,
            "driller": raw["Driller"].str.strip().values,
        }
    )
    # SJ 04455 POD1: its PLSS location (sec 01, T21N R04W) is next to the other
    # wells, but its UTM northing (4,077,235 m) puts it ~80 km north, outside
    # Sandoval County. Probably a typo in the northing; we don't map it.
    df["location_note"] = ""
    outside = df["latitude"] > 36.25
    df.loc[outside, "location_note"] = "UTM northing disagrees with PLSS location; not mapped"
    df.loc[outside, ["latitude", "longitude"]] = np.nan
    return df.reset_index(drop=True)


def load_well_logs() -> pd.DataFrame:
    """NM OSE well logs coded to Sandoval County (6 wells, drilled 1978-2022).

    Raw ``data7_Wells With Well Log Information.csv``; prepared in code: UTM zone 13
    converted to lat/lon, extra spaces removed from POD numbers, the footnote row
    dropped, and one well with an inconsistent northing left unmapped.
    ``first_water_ft`` is the depth where water was first found on drilling day,
    not a current water level.
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
            "site_id": wl["site_id"], "name": wl["site_name"], "latitude": wl["latitude"],
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
                "site_id": [rp["site_id"].iloc[0]], "name": [rp["site_name"].iloc[0]],
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
