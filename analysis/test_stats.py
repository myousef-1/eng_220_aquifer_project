"""Quick checks of the statistics against known answers. Run from the repository root:

    python -m analysis.test_stats

Reference values come from textbook definitions and were cross-checked with the
pymannkendall package (which isn't a project dependency)."""

import numpy as np

from . import stats


def test_mann_kendall_known_values():
    # Strictly increasing series of 10: S = n(n-1)/2 = 45, Var(S) = n(n-1)(2n+5)/18 = 125
    r = stats.mann_kendall(np.arange(10))
    assert r["S"] == 45 and abs(r["var_s"] - 125) < 1e-9
    assert abs(r["z"] - (45 - 1) / np.sqrt(125)) < 1e-9 and r["p"] < 0.001
    # No trend: a symmetric up-down series has S = 0 and p = 1
    r = stats.mann_kendall([1, 3, 2, 3, 1])
    assert r["S"] == 0 and r["p"] == 1.0


def test_mann_kendall_ties():
    # Ties reduce the variance: values [1, 1, 2, 3] -> one tie group of 2
    r = stats.mann_kendall([1, 1, 2, 3])
    expected_var = (4 * 3 * 13 - 2 * 1 * 9) / 18.0
    assert abs(r["var_s"] - expected_var) < 1e-9


def test_sen_slope():
    t = np.arange(2000, 2011)
    y = 2.0 * (t - 2000) + 5.0
    r = stats.sen_slope(t, y)
    assert abs(r["slope"] - 2.0) < 1e-12 and r["lower"] <= 2.0 <= r["upper"]
    # Robust to one wild value
    y2 = y.copy()
    y2[5] = 500
    assert abs(stats.sen_slope(t, y2)["slope"] - 2.0) < 1e-12


def test_spearman_and_permutation():
    x = np.arange(20)
    assert abs(stats.spearman(x, x ** 3) - 1.0) < 1e-12  # monotonic -> rho = 1
    assert stats.permutation_p(x, x, n=2000) < 0.01
    y = np.random.default_rng(1).permutation(x)  # a fixed shuffle with no real relationship
    assert stats.permutation_p(x, y, n=2000) > 0.05


def test_water_level_sign():
    # depth increasing by 1 ft/yr = water table FALLING 1 ft/yr
    import pandas as pd
    dates = pd.date_range("2000-01-01", "2009-12-01", freq="MS")
    df = pd.DataFrame({"site_id": "w", "date": dates, "depth_to_water_ft": 100 + (dates.year - 2000)})
    tr = stats.well_trends(df)
    assert abs(tr["level_slope_ft_per_yr"].iloc[0] + 1.0) < 1e-9 and tr["trend"].iloc[0] == "Declining"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("All statistics checks passed.")
