# Cleaned data

Cleaned CSV files, each made by the matching script in `cleaning/`. Don't edit these by hand: change the script and rerun it instead.

Every file uses the same conventions: lowercase names with underscores, units at the end of column names, the shared columns `site_id`, `site_name`, `latitude`, `longitude`, `date`, and `source`, dates as `YYYY-MM-DD`, and blank cells for missing values. The full rules are on the [Data cleaning page](https://pdjordj11.github.io/eng_220_aquifer_project/data-cleaning/).

| File | Contents | Made from |
|---|---|---|
| `groundwater_levels_monthly.csv` | 2,673 monthly depth-to-water values at the 9 USGS monitoring wells, 1998 to 2026 | Dataset 1, `water_flow_data_sandoval_county_sources.csv` |
| `aquifer_tests.csv` | 179 aquifer tests in Sandoval County: well construction, formation, and hydraulic properties | `ose_aquifer_test_wells.csv` (OSE Aquifer Test Index) |

Both are made by `cleaning/clean_csvs.m`. Datasets still to be cleaned are listed on the [Data cleaning page](https://pdjordj11.github.io/eng_220_aquifer_project/data-cleaning/#still-to-clean).
