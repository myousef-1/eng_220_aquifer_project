# 2. Data cleaning

**Lead:** James Wauneka

This stage turns the raw downloads into tables the analysis code can use directly. Cleaning makes the data correct and consistent; it doesn't draw conclusions. Averaging, trends, and narrowing to the Cuba area happen in the analysis stage.

## Cleaned files

| Cleaned file | Rows | Made from | What it holds |
|---|---|---|---|
| [`groundwater_levels_monthly.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/groundwater_levels_monthly.csv) | 2,673 | USGS statistics ([dataset 1](data-collection.md#1-usgs-groundwater-level-statistics)) | Monthly mean depth to water for 9 wells, June 1998 to September 2026 |
| [`aquifer_tests.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/aquifer_tests.csv) | 179 | NM Office of the State Engineer aquifer tests | One row per aquifer test in Sandoval County, 1930 to 2008, with formation, well construction, and hydraulic properties |

James's MATLAB script, [`cleaning/clean_csvs.m`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/cleaning/clean_csvs.m), makes both files. Both follow the [conventions](#conventions-for-cleaned-files) below. The groundwater file was checked against the raw data: it has the same rows, dates, and values, with no duplicates.

### Columns

**`groundwater_levels_monthly.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `depth_to_water_ft`

**`aquifer_tests.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `formation`, `well_depth_ft`, `screen_top_ft`, `screen_bottom_ft`, `depth_to_water_ft`, `pumping_rate_gpm`, `transmissivity_drawdown_ft2_per_day`, `transmissivity_recovery_ft2_per_day`, `storativity`, `specific_capacity_gpm_per_ft`, `hydraulic_conductivity_ft_per_day`

In both files, `depth_to_water_ft` is depth below land surface, so a larger number means a lower water table.

### Wells in the groundwater file

| `site_id` | Site name | Months | First | Last |
|---|---|---|---|---|
| USGS-351357106323001 | 12N.04E.29.433 SANDIA SITE | 323 | 1999-02 | 2026-04 |
| USGS-351357106323002 | 12N.04E.29.433A SANDIA SITE | 328 | 1999-01 | 2026-04 |
| USGS-351357106323003 | 12N.04E.29.433B SANDIA SITE | 198 | 1999-01 | 2015-09 |
| USGS-351515106410401 | 12N.02E.24.144 LINCOLN MIDDLE SCHOOL | 325 | 1998-06 | 2026-09 |
| USGS-351515106410402 | 12N.02E.24.144A LINCOLN MIDDLE SCHOOL | 310 | 1998-06 | 2026-09 |
| USGS-351515106410403 | 12N.02E.24.144B LINCOLN MIDDLE SCHOOL | 317 | 1998-06 | 2026-09 |
| USGS-351821106333901 | 13N.04E.31.343 BERNALILLO SITE | 306 | 1999-09 | 2026-08 |
| USGS-351821106333902 | 13N.04E.31.343A BERNALILLO SITE PIEZ 2 | 238 | 1999-09 | 2021-02 |
| USGS-354056106215801 | 17N.05E.24.344 DOME ROAD WELL | 328 | 1999-02 | 2026-06 |

Wells with an A or B suffix are at the same location as the well without one but are measured at different depths, so they stay separate.

## Running the script

In MATLAB, set the current folder to the repository's root folder (the one that contains `data/`), then run one of these:

    clean_csvs                  % make both cleaned files
    clean_csvs('groundwater')   % groundwater levels only
    clean_csvs('aquifer')       % aquifer tests only

The script reads `data/water_flow_data_sandoval_county_sources.csv` (an identical copy of dataset 1) and `data/ose_aquifer_test_wells.csv`, and writes to `data/clean/`. As it runs, it prints checks such as row counts, duplicate rows, and the list of formation names, so problems are easy to spot.

## Where files go

| What | Where | Example |
|---|---|---|
| Raw downloads (never edited) | `data/` | `data/ose_aquifer_test_wells.csv` |
| Cleaning scripts | `cleaning/` | `cleaning/clean_csvs.m` |
| Cleaned files | `data/clean/` | `data/clean/aquifer_tests.csv` |

Every cleaned file is made by a script in `cleaning/` that reads the raw file and writes the cleaned one, so anyone can rerun it and get the same result. Python or MATLAB both work. If a step is done by hand in Excel, write it down under [How each file was cleaned](#how-each-file-was-cleaned).

## How each file was cleaned

### Groundwater levels

1. Reads every column as text and standardizes the column names.
2. Keeps groundwater-level rows (`parameter_code` 72019) that are monthly means (`interval_type` is `month` and `parent_statistic_name` is `Mean`). That leaves 2,673 rows.
3. Renames columns to the shared names: `monitoring_location_id` → `site_id`, `monitoring_location_name` → `site_name`, `y` → `latitude`, `x` → `longitude`, `start_date` → `date`, and `arithmetic_mean` → `depth_to_water_ft`. Sets `source` to `USGS`.
4. Keeps wells with an A or B suffix as separate sites.
5. Checks for duplicate site-and-date rows (there are none) and counts the wells (9).
6. Sorts by site and date, and writes the file with blank cells for missing values.

### Aquifer tests

1. Reads every column as text and standardizes the column names. This also removes the hidden byte-order mark from the first column name.
2. Keeps Sandoval County rows (`COUNTY NAME` is `SANDOVAL`): 179 tests. Every test is kept, even when a well has more than one.
3. Keeps the 16 columns the analysis needs, renamed as listed under [Columns](#columns). Empty and administrative columns are left out, such as ground surface elevation (blank for every Sandoval row), `GlobalID`, and `Entered By`.
4. Converts numbers stored as text, removes commas, and leaves placeholders such as `NA` and `-9999` blank.
5. Converts dates such as `11/12/2002 12:00:00 AM` to `2002-11-12`.
6. Cleans formation names: trims extra spaces, converts them to uppercase, and fixes the misspelling `SAANDSTONE`.
7. Sets `source` to `NM OSE` and puts the shared columns first.
8. Checks for columns that are empty or identical in every row (none were), then sorts by site and date and writes the file.

## Conventions for cleaned files

Every cleaned file follows the same rules, so the files can be combined and charted the same way.

**File names:** lowercase with underscores, describing what's inside, such as `groundwater_levels_monthly.csv`. No dates, versions, or "final" in names; GitHub keeps the history.

**Column names:** lowercase with underscores, with the unit at the end, such as `well_depth_ft` or `transmissivity_drawdown_ft2_per_day`.

**Shared columns:** every file starts with these, using the same names:

| Column | Contents |
|---|---|
| `site_id` | The source's ID for the well or site, as text |
| `site_name` | The well or site name |
| `latitude`, `longitude` | Decimal degrees |
| `date` | `YYYY-MM-DD` |
| `source` | Where the data came from, such as `USGS` or `NM OSE` |

**Rows:** one row per measurement, sorted by `site_id` and then `date`.

**Values:**

- Numbers only, with no units, commas, or ranges inside cells.
- Missing values left blank. Never use `0`, `N/A`, or `-9999`, which charts would plot as real values.
- Dates as `YYYY-MM-DD`.
- Text trimmed of extra spaces and spelled consistently.

**File format:** comma-separated, UTF-8, one header row, and no index column. In pandas, use `df.to_csv(path, index=False)`. From Excel, save as "CSV UTF-8".

**What to keep:** IDs, location, date, and every measurement the analysis might use. Drop columns that are empty or identical in every row.

## Problems and decisions

| Problem | Decision |
|---|---|
| One hydraulic conductivity value is a range, `11 to 21` (Centex American Gypsum Company well) | Uses the midpoint, 16 ft/day |
| 104 tests have `1/1/1900` as the start water-level date, meaning the date is unknown | Treated as unknown. The date column isn't in the cleaned file. |
| 30 tests are dated January 1, which may mean only the year is known | Kept as is |
| Formation misspelled as `POINT LOOKOUT SAANDSTONE` | Fixed to `POINT LOOKOUT SANDSTONE` |
| Many tests are missing measurements, such as formation (blank for 54 of 179 tests) and storativity (blank for 165) | Left blank, as the conventions require |

### Still open

- **Incomplete well IDs in the aquifer-test file.** In the raw file, 157 of the 179 `OSE POD ID` values are incomplete, and 85 are just `RG--`. As a result, `site_id` groups unrelated wells together: the cleaned file has 73 site IDs but about 149 distinct wells by name and location. Until this is fixed, the analysis should tell wells apart by `site_name`, `latitude`, and `longitude`, not by `site_id`.
- **One formation name is still misspelled.** `AGUA ZARCA SANDSTONE MEMBER OF SIERRA NACIEMIENTO` should be `NACIMIENTO`. It can be added to the list of fixes in the script's `clean_formation` function.

## Still to clean

These raw files aren't cleaned yet. See [Data collection](data-collection.md) for what each one contains.

- **NM Bureau of Geology groundwater levels** (dataset 2): convert UTM easting and northing to latitude and longitude, after checking the zone and datum.
- **Rio Puerco at Cuba** (dataset 4): the streamflow and gage-height measurements.
- **Wells with well logs** (dataset 7): convert UTM coordinates to latitude and longitude, and trim the extra spaces in well IDs.
- **Other USGS measurements in dataset 1:** streamflow and reservoir storage, if the analysis uses them, one cleaned file per measurement, following the groundwater-levels pattern. The stream water-quality measurements don't need cleaning, since the project no longer covers water quality.

Datasets 3, 5, and 6 don't need cleaning: dataset 3 has no locations until its map layer is downloaded, and datasets 5 and 6 are publications rather than data tables.
