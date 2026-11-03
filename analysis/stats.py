"""Trend statistics for groundwater levels.

Method (standard in groundwater studies; see Helsel et al. 2020, *Statistical
Methods in Water Resources*, USGS Techniques and Methods 4-A3, ch. 12):

1. Average the monthly values into **annual means**, using only calendar years
   with at least 9 of 12 months, so a year with only winter or only summer
   readings doesn't skew the average (water levels have a seasonal cycle).
2. **Sen's slope**: the median of the slopes between every pair of years.
   It is a robust "typical change per year" that one odd year can't drag around.
3. **Mann-Kendall test**: is there a consistent upward or downward trend, or
   could the ups and downs be chance? We call a trend "declining" or "rising"
   only when p < 0.05, and "no clear trend" otherwise.

Caution: annual groundwater levels are serially correlated (a low year tends
to follow a low year). The Mann-Kendall p-value assumes independent years, so
it can make a trend look more certain than it is. The charts therefore show
the size of the change and its confidence interval, not just the label.

Only numpy, pandas, and the standard library are used (no scipy), so no new packages are needed.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

MIN_MONTHS_PER_YEAR = 9
ALPHA = 0.05


def annual_means(monthly: pd.DataFrame, value: str = "depth_to_water_ft",
                 min_months: int = MIN_MONTHS_PER_YEAR) -> pd.DataFrame:
    """Annual mean per site from monthly rows; drops years with too few months."""
    df = monthly.copy()
    df["year"] = df["date"].dt.year
    out = (
        df.groupby(["site_id", "year"])
        .agg(value=(value, "mean"), months=(value, "count"))
        .reset_index()
    )
    return out[out["months"] >= min_months].reset_index(drop=True)


def _norm_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def mann_kendall(y) -> dict:
    """Mann-Kendall trend test with the tie correction. Returns S, z, p."""
    y = np.asarray(y, dtype=float)
    y = y[~np.isnan(y)]
    n = len(y)
    if n < 4:
        return {"n": n, "S": np.nan, "z": np.nan, "p": np.nan, "var_s": np.nan}
    diffs = np.sign(y[None, :] - y[:, None])
    s = np.triu(diffs, k=1).sum()
    _, counts = np.unique(y, return_counts=True)
    ties = counts[counts > 1]
    var_s = (n * (n - 1) * (2 * n + 5) - np.sum(ties * (ties - 1) * (2 * ties + 5))) / 18.0
    if s > 0:
        z = (s - 1) / math.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / math.sqrt(var_s)
    else:
        z = 0.0
    p = 2 * (1 - _norm_cdf(abs(z)))
    return {"n": n, "S": float(s), "z": float(z), "p": float(p), "var_s": float(var_s)}


def sen_slope(t, y, alpha: float = ALPHA) -> dict:
    """Sen's slope (median pairwise slope) with its confidence interval
    (Gilbert 1987, eq. 16.6). Units: y-units per t-unit."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = ~(np.isnan(t) | np.isnan(y))
    t, y = t[ok], y[ok]
    n = len(t)
    if n < 4:
        return {"slope": np.nan, "lower": np.nan, "upper": np.nan}
    i, j = np.triu_indices(n, k=1)
    dt = t[j] - t[i]
    keep = dt != 0
    slopes = np.sort((y[j] - y[i])[keep] / dt[keep])
    m = len(slopes)
    var_s = mann_kendall(y)["var_s"]
    z = 1.959963984540054 if alpha == 0.05 else _z_for(alpha)
    c = z * math.sqrt(var_s)
    lo = int(np.floor((m - c) / 2))  # 1-based rank M1 -> 0-based index M1-1
    hi = int(np.ceil((m + c) / 2))   # 1-based rank M2+1 -> 0-based index M2
    lo = min(max(lo - 1, 0), m - 1)
    hi = min(max(hi, 0), m - 1)
    return {"slope": float(np.median(slopes)), "lower": float(slopes[lo]), "upper": float(slopes[hi])}


def _z_for(alpha: float) -> float:
    # Small bisection so we don't need scipy for a different alpha.
    target = 1 - alpha / 2
    lo, hi = 0.0, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if _norm_cdf(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def classify(slope_level: float, p: float, alpha: float = ALPHA) -> str:
    """Label a WATER-LEVEL slope (positive = water table rising)."""
    if np.isnan(slope_level) or np.isnan(p):
        return "Not enough data"
    if p >= alpha:
        return "No clear trend"
    return "Rising" if slope_level > 0 else "Declining"


def well_trends(monthly: pd.DataFrame, start: int | None = None, end: int | None = None,
                min_years: int = 7) -> pd.DataFrame:
    """Trend per well over [start, end] (calendar years, inclusive).

    Works on depth to water but reports the WATER-LEVEL change
    (``level_slope_ft_per_yr`` = minus the depth slope), so positive means
    the water table is rising and negative means it is falling.
    """
    ann = annual_means(monthly)
    if start is not None:
        ann = ann[ann["year"] >= start]
    if end is not None:
        ann = ann[ann["year"] <= end]
    rows = []
    for site_id, g in ann.groupby("site_id"):
        g = g.sort_values("year")
        if len(g) < min_years:
            rows.append({"site_id": site_id, "n_years": len(g), "first_year": g["year"].min(),
                         "last_year": g["year"].max(), "level_slope_ft_per_yr": np.nan,
                         "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan,
                         "trend": "Not enough data", "total_change_ft": np.nan})
            continue
        sen = sen_slope(g["year"], g["value"])
        mk = mann_kendall(g["value"])
        level = -sen["slope"]
        rows.append({
            "site_id": site_id,
            "n_years": len(g),
            "first_year": int(g["year"].min()),
            "last_year": int(g["year"].max()),
            "level_slope_ft_per_yr": level,
            # flip the interval too: the depth CI [lower, upper] becomes [-upper, -lower]
            "ci_low": -sen["upper"],
            "ci_high": -sen["lower"],
            "p_value": mk["p"],
            "trend": classify(level, mk["p"]),
            "total_change_ft": level * (g["year"].max() - g["year"].min()),
        })
    return pd.DataFrame(rows)


def spearman(x, y) -> float:
    """Spearman rank correlation (Pearson correlation of the ranks)."""
    xr = pd.Series(x).rank().to_numpy()
    yr = pd.Series(y).rank().to_numpy()
    return float(np.corrcoef(xr, yr)[0, 1])


def permutation_p(x, y, n: int = 10000, seed: int = 220) -> float:
    """Two-sided permutation p-value for a Spearman correlation: how often a
    random shuffle of y gives a correlation at least as strong as the real one.
    Works for small samples without assuming a distribution."""
    rng = np.random.default_rng(seed)
    xr = pd.Series(x).rank().to_numpy()
    yr = pd.Series(y).rank().to_numpy()
    obs = abs(np.corrcoef(xr, yr)[0, 1])
    hits = sum(abs(np.corrcoef(xr, rng.permutation(yr))[0, 1]) >= obs for _ in range(n))
    return (hits + 1) / (n + 1)
