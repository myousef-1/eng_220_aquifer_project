# 2. Data cleaning

**Lead:** James Wauneka

This stage turns the raw downloads into tables the analysis code can use directly. Cleaning makes the data correct and consistent; it doesn't draw conclusions. Averaging, trends, and narrowing to the Cuba area happen in the analysis stage.

James cleaned the first two datasets on Oct 30 and the remaining four on Nov 12, so every dataset the analysis uses now comes from a cleaned file. His report on the cleaning, [*Sandoval County Water Data Report* (PDF)](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/project_notes/Sandoval_County_Water_Data_Report.pdf), summarizes each file and lists the data problems the script found. This page draws on it.

## Cleaned files

| Cleaned file | Rows | Made from | What it holds |
|---|---|---|---|
| [`groundwater_levels_monthly.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/groundwater_levels_monthly.csv) | 2,673 | USGS statistics ([dataset 1](data-collection.md#1-usgs-groundwater-level-statistics)) | Monthly mean depth to water for 9 wells, June 1998 to September 2026 |
| [`groundwater_levels_nmbgmr.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/groundwater_levels_nmbgmr.csv) | 451 | NM Bureau of Geology groundwater levels ([dataset 2](data-collection.md#2-nm-bureau-of-geology-groundwater-levels)) | Depth to water at 87 wells, 1997 to 2019, with each well's depth, casing, and completion date |
| [`aquifer_tests.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/aquifer_tests.csv) | 179 | NM Office of the State Engineer aquifer tests ([other raw data](data-collection.md#other-raw-data-in-the-repository)) | One row per aquifer test in Sandoval County, 1930 to 2008, with formation, well construction, and hydraulic properties |
| [`streamflow_measurements.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/streamflow_measurements.csv) | 10 | Rio Puerco at Cuba, three files ([dataset 4](data-collection.md#4-rio-puerco-at-cuba)) | One row per USGS streamflow visit to gage 08332525, April 2019 to March 2026, with channel measurements and gage height |
| [`well_logs.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/well_logs.csv) | 6 | Wells with well logs ([dataset 7](data-collection.md#7-wells-with-well-logs)) | Drilling records for 6 wells in the San Juan sub-basin, finished 1979 to 2022 |
| [`aquifer_sensitivity.csv`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/data/clean/aquifer_sensitivity.csv) | 613 | Aquifer sensitivity ([dataset 3](data-collection.md#3-aquifer-sensitivity)) | One row per mapped area, with its sensitivity class and size; no locations |

James's MATLAB script, [`cleaning/clean_csvs_Revised_2.m`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/cleaning/clean_csvs_Revised_2.m), makes all six files. His first script, [`cleaning/clean_csvs.m`](https://github.com/pdjordj11/eng_220_aquifer_project/blob/main/cleaning/clean_csvs.m), makes only the first two, the same way. Every file follows the [conventions](#conventions-for-cleaned-files) below, except that the sensitivity file lists map areas rather than sites, so it doesn't have the shared site and date columns. The USGS groundwater file was checked against the raw data: it has the same rows, dates, and values, with no duplicates.

### Columns

**`groundwater_levels_monthly.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `depth_to_water_ft`

**`groundwater_levels_nmbgmr.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `depth_to_water_ft`, `level_status`, `measurement_method`, `altitude_ft`, `well_depth_ft`, `casing_depth_ft`, `casing_diameter_ft`, `completion_date`

**`aquifer_tests.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `formation`, `well_depth_ft`, `screen_top_ft`, `screen_bottom_ft`, `depth_to_water_ft`, `pumping_rate_gpm`, `transmissivity_drawdown_ft2_per_day`, `transmissivity_recovery_ft2_per_day`, `storativity`, `specific_capacity_gpm_per_ft`, `hydraulic_conductivity_ft_per_day`

**`streamflow_measurements.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `time_local`, `measurement_number`, `discharge_cfs`, `width_ft`, `area_ft2`, `velocity_ft_per_s`, `distance_from_gage_ft`, `location_from_gage`, `measurement_type`, `channel_stability`, `channel_material`, `channel_evenness`, `horizontal_velocity`, `vertical_velocity`, `longitudinal_velocity`, `gage_height_ft`, `measurement_rating`, `control_condition`

**`well_logs.csv`:** `site_id`, `site_name`, `latitude`, `longitude`, `date`, `source`, `start_date`, `log_file_date`, `borehole_depth_ft`, `depth_to_first_water_ft`, `water_source`, `sub_basin`, `plss_location`, `location_from_plss`, `utm_easting`, `utm_northing`, `driller`, `license_number`

**`aquifer_sensitivity.csv`:** `polygon_id`, `sensitivity`, `sensitivity_rank`, `area_sq_deg`, `perimeter_deg`

A few columns need a note:

- `depth_to_water_ft` is depth below land surface, so a larger number means a lower water table. In `well_logs.csv`, `depth_to_first_water_ft` is where water was first found while drilling, not a current level.
- `site_name` is blank in the NM Bureau of Geology and well-log files, because those sources don't name their wells. Use `site_id` (the well ID or POD number) instead.
- `level_status` marks readings that may not be static water levels, mostly R (the well was recently pumped) and T (a nearby well was recently pumped).
- In `streamflow_measurements.csv`, a `measurement_type` of Other means the visit found no measurable flow (`discharge_cfs` is 0).
- In `well_logs.csv`, `date` is when drilling finished; `start_date` is when it began.
- In `aquifer_sensitivity.csv`, `sensitivity` is Less, Moderate, or High (`sensitivity_rank` 1 to 3), and area and perimeter are in degrees because the map layer uses latitude and longitude.

### Wells in the USGS groundwater file

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

    clean_csvs_Revised_2                  % make every cleaned file whose raw file is present
    clean_csvs_Revised_2('groundwater')   % USGS groundwater levels only
    clean_csvs_Revised_2('aquifer')       % aquifer tests only
    clean_csvs_Revised_2('nmbgmr')        % NM Bureau of Geology groundwater levels only
    clean_csvs_Revised_2('streamflow')    % Rio Puerco at Cuba only (reads all three data4 files)
    clean_csvs_Revised_2('welllogs')      % well logs only
    clean_csvs_Revised_2('sensitivity')   % aquifer sensitivity only

The script reads the raw files from `data/` and writes to `data/clean/`. If a raw file is missing, it skips that dataset instead of stopping. If a file was saved with extra characters in its name, such as a number a browser added to the start of a download, it finds and uses it. As it runs, it prints checks such as row counts, duplicate rows, and values that look wrong, so problems are easy to spot.

## Where files go

| What | Where | Example |
|---|---|---|
| Raw downloads (never edited) | `data/` | `data/ose_aquifer_test_wells.csv` |
| Cleaning scripts | `cleaning/` | `cleaning/clean_csvs_Revised_2.m` |
| Cleaned files | `data/clean/` | `data/clean/aquifer_tests.csv` |
| James's report on the cleaning | `project_notes/` | `project_notes/Sandoval_County_Water_Data_Report.pdf` |

Every cleaned file is made by a script in `cleaning/` that reads the raw file and writes the cleaned one, so anyone can rerun it and get the same result. Python or MATLAB both work. If a step is done by hand in Excel, write it down under [How each file was cleaned](#how-each-file-was-cleaned).

## How each file was cleaned

### USGS groundwater levels

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

### NM Bureau of Geology groundwater levels

1. Reads every column as text and keeps Sandoval County rows. The county is spelled both `SANDOVAL` and `Sandoval`, so it compares them in capitals.
2. Converts UTM easting and northing (NAD83, zone 13N) to latitude and longitude. The script warns if any row uses a different datum; none do.
3. Renames columns to the shared names, such as `PointID` → `site_id`, `DateMeasured` → `date`, and `DepthToWaterBGS` → `depth_to_water_ft`, and sets `source` to `NMBGMR`. Leaves `site_name` blank, since the source doesn't name its wells. Converts `NULL` to blank and dates such as `8/12/1998` to `1998-08-12`. The measurement time isn't kept, because one well (PC-020) has its time in the time-zone column.
4. Drops the 5 readings with no depth to water (all from wells recorded as dry, status D), leaving 451 of the 456 rows.
5. Blanks one impossible casing diameter, 41 at PB-0019 (the others are 0.3 to 0.6 ft).
6. Flags but keeps readings deeper than the well itself (NM-26928 reads up to 103 ft in a 100 ft well), and counts the 226 readings with a level-status code.
7. Checks for duplicate site-and-date rows (there are none), then sorts by site and date and writes the file.

### Rio Puerco at Cuba

1. Reads the three USGS files: the channel measurements (one row per visit), the field measurements, and the station details.
2. Checks that every measurement uses the same unit on every row (ft³/s, ft, ft², and ft/s), so the units can go into the column names, such as `discharge_cfs`.
3. Takes the station name from the station file, and converts each visit's time from UTC to New Mexico time before taking the date.
4. Joins gage height (USGS parameter 00065) from the field-measurement file by visit, with its rating and control condition. Only the four visits with flow have a gage height.
5. Cleans the category columns: `Unspecified` becomes blank, and capitalization is made consistent (`main` and `Main`).
6. Checks that discharge equals channel area times velocity (the four flowing visits agree within 1%) and reports missing measurement numbers: 12 to 15 aren't in the file, so there are no visits between April 2021 and April 2024.
7. Drops columns that are the same on every row, such as the channel name, and writes one row per visit.

### Well logs

1. Drops the footnote line at the bottom of the file and keeps Sandoval County wells (county code `SA`): 6 wells.
2. Trims the extra spaces in the POD numbers (`SJ  00809` → `SJ 00809`), which become `site_id`. Leaves `site_name` blank.
3. Converts UTM coordinates (zone 13) to latitude and longitude, and records in `location_from_plss` whether a location was placed from the well's legal description (PLSS) rather than measured. Three were.
4. Uses the date drilling finished as `date`, and keeps the start date and the date the log was filed.
5. Blanks the latitude and longitude of SJ 04455 POD1, whose northing puts it about 80 km north, outside the county. Its UTM values are kept so it can be corrected.
6. Flags but keeps a log filed before drilling started (SJ 01824) and two spellings of one driller's name under license 1357.

### Aquifer sensitivity

1. Reads the file's four columns: `OBJECTID`, `SENSITIVITY`, `Shape__Area`, and `Shape__Length`.
2. Spells out the class names (`Mod` → `Moderate`) and adds `sensitivity_rank` (1 Less, 2 Moderate, 3 High) for sorting.
3. Renames the area and perimeter to `area_sq_deg` and `perimeter_deg`: the map layer uses latitude and longitude, so they're in degrees.
4. Checks for duplicate polygon IDs (there are none) and writes one row per mapped area, sorted by `polygon_id`.

## What the checks show

James's report also describes what the cleaned files contain. These points matter when using them:

- **NM Bureau of Geology groundwater levels:** most readings come from one survey. 383 of the 451 were taken in 1997-1998, 18 in 1999, and 50 in 2016-2019, and 32 of the 87 wells have only one reading. 226 readings carry a level-status code, so filter on `level_status` before looking at trends.
- **Aquifer tests:** transmissivity is reported in 117 of the 179 tests and differs more than tenfold between formations: the median is 690 ft²/day in the Santa Fe Group and 55 ft²/day in the Abo Sandstone. 54 tests have no formation listed.
- **Rio Puerco at Cuba:** gage height doesn't predict flow here. A flow of 20.4 ft³/s read 4.61 ft in 2020, and 20.2 ft³/s read 3.05 ft in 2024, after the streambed changed from silt and mud to gravel.
- **Aquifer sensitivity:** the areas add up to about 31 square degrees, roughly 310,000 km², which is about the size of New Mexico, and the largest single area (1.33 square degrees, High) is bigger than Sandoval County. So the file covers the whole state, not just the county. It has no shapes or coordinates, so it can't be matched to wells until the map layer itself is downloaded.
- **Well logs:** SJ 01824 and SJ 03562 have the same coordinates because both were placed at the center of the same quarter-quarter section, not because they're the same well.

## Conventions for cleaned files

Every cleaned file follows the same rules, so the files can be combined and charted the same way.

**File names:** lowercase with underscores, describing what's inside, such as `groundwater_levels_monthly.csv`. No dates, versions, or "final" in names; GitHub keeps the history.

**Column names:** lowercase with underscores, with the unit at the end, such as `well_depth_ft` or `transmissivity_drawdown_ft2_per_day`.

**Shared columns:** every file of sites starts with these, using the same names:

| Column | Contents |
|---|---|
| `site_id` | The source's ID for the well or site, as text |
| `site_name` | The well or site name, blank if the source doesn't name it |
| `latitude`, `longitude` | Decimal degrees |
| `date` | `YYYY-MM-DD` |
| `source` | Where the data came from, such as `USGS`, `NMBGMR`, or `NM OSE` |

**Rows:** one row per measurement, sorted by `site_id` and then `date`.

**Values:**

- Numbers only, with no units, commas, or ranges inside cells.
- Missing values left blank. Never use `0`, `N/A`, or `-9999`, which charts would plot as real values.
- Dates as `YYYY-MM-DD`.
- Text trimmed of extra spaces and spelled consistently.

**File format:** comma-separated, UTF-8, one header row, and no index column. In pandas, use `df.to_csv(path, index=False)`. From Excel, save as "CSV UTF-8".

**What to keep:** IDs, location, date, and every measurement the analysis might use. Drop columns that are empty or identical in every row.

## Problems and decisions

| Dataset | Problem | Decision |
|---|---|---|
| Aquifer tests | One hydraulic conductivity value is a range, `11 to 21` (Centex American Gypsum Company well) | Uses the midpoint, 16 ft/day |
| Aquifer tests | 104 tests have `1/1/1900` as the start water-level date, meaning the date is unknown | Treated as unknown. The date column isn't in the cleaned file. |
| Aquifer tests | 30 tests are dated January 1, which may mean only the year is known | Kept as is |
| Aquifer tests | Formation misspelled as `POINT LOOKOUT SAANDSTONE` | Fixed to `POINT LOOKOUT SANDSTONE` |
| Aquifer tests | Many tests are missing measurements, such as formation (blank for 54 of 179 tests) and storativity (blank for 165) | Left blank, as the conventions require |
| NM Bureau of Geology | County spelled both `SANDOVAL` and `Sandoval` | Treated as the same county |
| NM Bureau of Geology | Coordinates given only in UTM | Converted to latitude and longitude |
| NM Bureau of Geology | 5 readings from dry wells have no depth | Dropped |
| NM Bureau of Geology | PB-0019 has a casing diameter of 41 (the others are 0.3 to 0.6 ft) | Blanked |
| NM Bureau of Geology | NM-26928's water is deeper than the well (up to 103 ft in a 100 ft well) | Flagged and kept |
| NM Bureau of Geology | PC-020's time is in the time-zone column | Time not kept |
| Rio Puerco at Cuba | `Unspecified` categories, and `main` vs `Main` | Blanked, and capitalization fixed |
| Rio Puerco at Cuba | Measurements 12 to 15 are missing | Gap reported; nothing between April 2021 and April 2024 |
| Well logs | Extra spaces in the POD numbers, and a footnote line at the bottom of the file | Spaces trimmed and footnote dropped |
| Well logs | SJ 04455 POD1's northing puts it about 80 km north, outside the county | Latitude and longitude blanked; UTM kept so it can be corrected |
| Well logs | SJ 01824's log was filed before drilling started | Flagged and kept |

### Still open

- **Incomplete well IDs in the aquifer-test file.** In the raw file, 157 of the 179 `OSE POD ID` values are incomplete, and 85 are just `RG--`. As a result, `site_id` groups unrelated wells together: the cleaned file has 73 site IDs but about 149 distinct wells by name and location. Until this is fixed, the analysis tells wells apart by `site_name`, `latitude`, and `longitude`, not by `site_id`.
- **One formation name is still misspelled.** `AGUA ZARCA SANDSTONE MEMBER OF SIERRA NACIEMIENTO` should be `NACIMIENTO`. It can be added to the list of fixes in the script's `clean_formation` function.
- **Negative pumping rates.** Five aquifer tests have pumping rates below zero, all from one 1980 test series at RG-24834 (wells SH-1 to SH-5, Abiquiu Tuff). A pumping rate can't be negative, so they were probably entered with the wrong sign. They're kept as is for now. The fix is to flip the sign if the original test reports confirm the values, or to blank them; until then, treat the Abiquiu Tuff's numbers with caution.
- **Negative water levels.** Two aquifer tests have a depth to water below zero: the Wild Cherry Farm well (-25.84 ft, 2006) and Expl-3 (-9.1 ft, 2002). These probably aren't errors. They mean water stood above the ground, as in a flowing (artesian) well, so they're kept.
- **One large drop at PC-014.** Its 2019 reading is about 50 ft deeper than its 1997-1998 readings, but it's a single reading. Confirm it before treating it as a decline. The [Placitas chart](analysis.md#4-placitas_remeasured) on the Analysis page shows it.
- **One driller, two spellings.** License 1357 is listed as both `BAILEY, MARK` and `BAILEY, MARKMANLENENER`, probably a typo for the same driller. Flagged and kept.

## Not cleaned

- **Other USGS measurements in dataset 1.** The charts that use streamflow read it straight from the raw file with `load_usgs_stats()`, which keeps one measurement and one interval type at a time (see [Analysis](analysis.md#data-preparation-inside-the-analysis-code)). The stream water-quality measurements aren't cleaned, since the project no longer covers water quality.
- **Datasets 5 and 6** are publications rather than data tables.

## How the analysis uses these files

Since Nov 12, the analysis code reads all six cleaned files directly, with James's column names. How Micah's code was changed to use them is on the Analysis page, under [Switching to the cleaned files](analysis.md#switching-to-the-cleaned-files-nov-12).
