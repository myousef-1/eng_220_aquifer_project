# Cleaned data

Cleaned CSV files, each made by James's script in `cleaning/`. Don't edit these by hand: change the script and rerun it instead.

Every file uses the same conventions: lowercase names with underscores, units at the end of column names, the shared columns `site_id`, `site_name`, `latitude`, `longitude`, `date`, and `source` (except the sensitivity file, which lists map areas rather than sites), dates as `YYYY-MM-DD`, and blank cells for missing values. The full rules are on the [Data cleaning page](https://pdjordj11.github.io/eng_220_aquifer_project/data-cleaning/).

| File | Contents | Made from |
|---|---|---|
| `groundwater_levels_monthly.csv` | 2,673 monthly depth-to-water values at the 9 USGS monitoring wells, 1998 to 2026 | Dataset 1, `water_flow_data_sandoval_county_sources.csv` |
| `groundwater_levels_nmbgmr.csv` | 451 depth-to-water readings at 87 wells, 1997 to 2019 | Dataset 2, `data2_groundwater_sandoval_county.csv` |
| `aquifer_tests.csv` | 179 aquifer tests in Sandoval County: well construction, formation, and hydraulic properties | `ose_aquifer_test_wells.csv` (OSE Aquifer Test Index) |
| `streamflow_measurements.csv` | 10 USGS streamflow visits to the Rio Puerco at Cuba, 2019 to 2026 | Dataset 4, the three `data4_*.csv` files |
| `well_logs.csv` | Drilling records for 6 wells, finished 1979 to 2022 | Dataset 7, `data7_Wells With Well Log Information.csv` |
| `aquifer_sensitivity.csv` | 613 mapped areas with a sensitivity class and size, no locations | Dataset 3, `data3_Aquifer_Sensitivity.csv` |

All six are made by `cleaning/clean_csvs_Revised_2.m`.
