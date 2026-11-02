# 1. Data collection

**Lead:** Dylan Gonzales

This stage covers finding public datasets that can answer the [research questions](index.md#research-questions), downloading them, and recording where each one comes from.

For each dataset, Dylan wrote a one-page brief. It covers what the dataset contains, which research questions it can help answer, which plots to make, and what the data can't show. A one-page guide compares all seven:

- [Data plotting guide for datasets 1–7 (PDF)](files/Overview_doc1thru7_Cuba_Water_Project_Data_Plotting_Guide.pdf)

The briefs and the guide use the proposal's original nine research questions. Three of those were later dropped (see [Not collected](#not-collected)) and the rest were renumbered: Q1 to Q4 are unchanged, the proposal's Q8 is now Q5, and its Q9 is now Q6. This page uses the new numbers.

## What the data can and can't show

Together, the datasets are strongest for groundwater trends at monitored wells (Q1), well characteristics (Q2), comparing the Ojo Alamo Sandstone and San Jose Formation (Q4), monitoring coverage and gaps (Q5), and dashboard indicators (Q6). The Rio Puerco measurements are the only data from Cuba itself, and they describe the river, not groundwater.

None of them shows on its own whether Cuba's municipal aquifer is being depleted, or which formation Cuba's wells draw from. Every chart and caption should say whether it describes Cuba itself, Sandoval County, or the wider San Juan Basin.

## Datasets

| # | Dataset | From | Relevance to Cuba | Best for | Brief |
|---|---|---|---|---|---|
| 1 | Groundwater-level statistics | USGS | Countywide; no Cuba wells | Q1, Q5, Q6 | [PDF](files/support_doc1_Sandoval_Groundwater_Data_Research_Brief.pdf) |
| 2 | Groundwater levels | NM Bureau of Geology | Countywide; nearest well about 24 miles from Cuba | Q2, Q5, Q1 | [PDF](files/support_doc2_NMBGMR_Sandoval_Groundwater_Research_Brief_RECREATED.pdf) |
| 3 | Aquifer sensitivity | NM Water Data | Not established; the file has no locations | Q6, once checked | [PDF](files/support_doc3_Aquifer_Sensitivity_Research_Brief.pdf) |
| 4 | Rio Puerco at Cuba | USGS | At Cuba (river, not groundwater) | Q3 (context), Q5, Q6 | [PDF](files/support_doc4_Rio_Puerco_Cuba_USGS_Research_Brief.pdf) |
| 5 | Ojo Alamo Sandstone | USGS map plate | Regional geology | Q4, Q2 | [PDF](files/support_doc5_Ojo_Alamo_Sandstone_Research_Brief.pdf) |
| 6 | San Jose Formation near Lindrith | NM Geological Society | Regional geology | Q4, Q2 | [PDF](files/support_doc6_San_Jose_Formation_Lindrith_Research_Brief.pdf) |
| 7 | Wells with well logs | NM Office of the State Engineer | 6 Sandoval well logs; Cuba link not verified | Q2, Q5 | [PDF](files/support_doc7_San_Juan_Wells_With_Well_Log_Research_Brief.pdf) |

The raw files are in the repository's [`data/` folder](https://github.com/pdjordj11/eng_220_aquifer_project/tree/main/data), and Word versions of the briefs are in `docs/files/`.

### 1. USGS groundwater-level statistics

**File:** `data1_water_flow_data_sandoval_county_sources.csv`<br>
**Source:** [USGS Water Data statistics download](https://api.waterdata.usgs.gov/download/statistics/?statistics=intervals&site_type_code=GW&computation_type=arithmetic_mean&computation_type=maximum&computation_type=median&computation_type=minimum&computation_type=percentile&state_code=US%3A35&county_code=US%3A35%3A043&normal_type=DOY&normal_type=MOY&interval_type=M&interval_type=CY&interval_type=WY)

USGS monthly and yearly statistics for 30 monitoring sites in Sandoval County (9 wells, 17 stream gages, 2 canals, and 2 reservoirs), with records from 1926 to 2026. Besides depth to groundwater, it covers streamflow, reservoir storage, suspended sediment, water temperature, and water quality (specific conductance, dissolved oxygen, pH, and turbidity). Dylan's brief covers the groundwater part: 9,462 records from 9 wells at four sites (Sandia, Lincoln Middle School, Bernalillo, and Dome Road), from about 1998 to 2026.

- **Use for:** depth-to-water trends at each well, a map of the wells, and a timeline of monitoring coverage.
- **Cautions:** none of the wells are in Cuba. Monthly, calendar-year, and water-year rows summarize the same measurements, so use one type at a time. A larger depth to water means a lower water table.

### 2. NM Bureau of Geology groundwater levels

**File:** `data2_groundwater_sandoval_county.csv`<br>
**Source:** [New Mexico Water Data: groundwater levels](https://catalog.newmexicowaterdata.org/dataset/groundwater-levels/resource/de88e71a-3f5b-4bc9-8fb0-28b81c198952)

456 depth-to-water measurements from 87 wells in Sandoval County, 1997 to 2019, from the New Mexico Bureau of Geology and Mineral Resources. Each record has the well's location (UTM easting and northing), well depth, hole depth, measurement date, and depth to water below ground.

- **Use for:** a map of the wells, well depth compared with depth to water, time series for wells measured more than once, and measurement counts per well.
- **Cautions:** the nearest well is about 24 miles from Cuba. Many wells were measured only once, which can't show a trend. Check the UTM zone and datum before mapping.

### 3. Aquifer sensitivity

**File:** `data3_Aquifer_Sensitivity.csv`<br>
**Source:** [New Mexico Water Data: aquifer sensitivity](https://catalog.newmexicowaterdata.org/dataset/aquifer-sensitivity) ([map layer](https://catalog.newmexicowaterdata.org/dataset/aquifer-sensitivity/resource/edf278aa-7c5b-4b65-97aa-c6825fa9015c))

613 mapped areas, each with a sensitivity class (339 Moderate, 152 High, and 122 Less) and the area's size and perimeter. The CSV has no coordinates or shapes, so it can't be mapped or matched to Cuba on its own.

- **Use for:** a sensitivity indicator on the dashboard (Q6), once the map layer is downloaded and it's clear what "sensitivity" measures.
- **Cautions:** the class counts are numbers of mapped areas, not shares of land. The file doesn't state the units for area and perimeter.

### 4. Rio Puerco at Cuba

**Files:** `data4_monitoring-location-metadata.csv`, `data4_field-measurements.csv`, `data4_channel-measurements.csv`<br>
**Source:** [USGS station 08332525 on the Water Quality Portal](https://www.waterqualitydata.us/provider/NWIS/USGS-NM/USGS-08332525/)

The only dataset measured at Cuba itself: USGS station 08332525 on the Rio Puerco. The three files hold the station's details and coordinates, 4 gage-height readings (2019 to 2024), and 10 streamflow measurements (2019 to 2026). Six of the streamflow visits found no flow, and the other four measured 6.89 to 20.40 cubic feet per second.

- **Use for:** surface-water context in the Cuba case study (Q3): a scatter plot of flow by date, a count of zero-flow and flowing visits, and a map of the station relative to Cuba.
- **Cautions:** these are occasional visits, not a continuous record, so zero-flow readings don't mean the river is dry all year. The station measures the river, not Cuba's groundwater or water supply.

### 5. Ojo Alamo Sandstone

**File:** `data5_ojo_alamo_sandstone_pub.pdf`<br>
**Source:** [USGS, *Hydrogeology of the Ojo Alamo Sandstone in the San Juan Structural Basin* (Hydrologic Atlas 720-B)](https://www.usgs.gov/publications/hydrogeology-ojo-alamo-sandstone-san-juan-structural-basin-new-mexico-colorado-arizona)

A USGS map plate (1990) of the Ojo Alamo Sandstone across the San Juan Basin, showing depth to the top of the sandstone, its thickness, and wells completed in it.

- **Use for:** an annotated map, or a side-by-side comparison with the San Jose Formation (Q4).
- **Cautions:** this is a historical regional map, not current conditions, and it isn't a table to plot. It doesn't show that Cuba's wells draw from this formation.

### 6. San Jose Formation near Lindrith

**File:** `data6_cuba_mesa_member_of_san_jose_formation.pdf`<br>
**Source:** Blandford et al. (2025), "[San Jose Formation Hydrostratigraphy and Groundwater Conditions in the Vicinity of Lindrith, New Mexico](https://nmgs.nmt.edu/publications/guidebooks/details.cfml?ID=134492)," New Mexico Geological Society Guidebook 75, pp. 235–246, [doi:10.56577/FFC-75.235](https://doi.org/10.56577/FFC-75.235)

A study of about 840 km² near Lindrith that uses more than 350 geophysical logs and 85 well-drilling logs. It identifies four water-bearing units in the San Jose Formation, maps the thickness of the Cuba Mesa Member, and maps groundwater levels.

- **Use for:** comparing with the Ojo Alamo Sandstone (Q4), and explaining which units wells reach (Q2).
- **Cautions:** the study is centered near Lindrith, not on Cuba's wells. The Cuba Mesa Member is a candidate water-bearing unit around Cuba, but the paper doesn't show that Cuba pumps from it.

### 7. Wells with well logs

**File:** `data7_Wells With Well Log Information.csv`<br>
**Source:** NM Office of the State Engineer, Water Rights Reporting System, "Wells With Well Log Information" report for the San Juan basin

Drilling records for 6 wells in Sandoval County, drilled between 1978 and 2022, with location, borehole depth, depth where water was first found, and driller. They come from a San Juan basin download of 1,379 well logs across four counties, which Dylan's brief describes.

- **Use for:** comparing borehole depth with first-water depth (Q2), and mapping where well logs exist (Q5).
- **Cautions:** first-water depth was recorded on drilling day, not as a current water level. The file doesn't identify Cuba's municipal wells or the formation each well draws from.

### Other raw data in the repository

**`ose_aquifer_test_wells.csv`:** New Mexico Office of the State Engineer aquifer-test records, 3,455 statewide and 179 in Sandoval County, including well depth, screened interval, geologic formation, and hydraulic properties such as transmissivity and storativity. It's cleaned into `data/clean/aquifer_tests.csv` (see [Data cleaning](data-cleaning.md)).<br>
**Source:** *To be added: link to the page this file was downloaded from.*

**`water_flow_data_sandoval_county_sources.csv`:** an identical copy of dataset 1. The cleaning script reads this copy.

## Not collected

These sources were identified in the proposal but weren't collected during the project. The report's Limitations section explains what their absence means for the findings.

- **Cuba's municipal well records:** well IDs, the formation each well draws from, pumping volumes, and water-level history, from the Village of Cuba or the NM Office of the State Engineer. Every brief points to these records as the missing piece for answering whether Cuba's aquifer is being depleted (Q3).
- **Aquifer sensitivity map layer:** the map layer for dataset 3 and documentation of what its classes mean, to check whether it covers Cuba.
- **Digital aquifer data near Cuba:** USGS San Juan Basin digital aquifer data for the Ojo Alamo Sandstone and San Jose Formation, to go beyond the maps in datasets 5 and 6.
- **Water quality and salinity:** the NM Bureau of Geology San Juan Basin Brackish Water Assessment and New Mexico Water Data records. Without them, the proposal's question on groundwater quality was dropped.
- **Acequias:** locations and service areas of acequias and community ditches from the NM Interstate Stream Commission. Without them, the proposal's questions on acequias and on links between groundwater and surface water were dropped.
- **More water-level records:** National Ground-Water Monitoring Network and Healy Collaborative Groundwater Monitoring Network data.
- **Shallow groundwater depth:** the [mean annual depth to groundwater for the shallow riparian aquifer](https://catalog.newmexicowaterdata.org/dataset/mean-annual-depth-to-groundwater-for-the-shallow-riparian-aquifer) dataset.
- **County boundary:** a Sandoval County boundary layer to organize the maps.

## Sources

- [USGS Water Data statistics download (Sandoval County groundwater)](https://api.waterdata.usgs.gov/download/statistics/?statistics=intervals&site_type_code=GW&computation_type=arithmetic_mean&computation_type=maximum&computation_type=median&computation_type=minimum&computation_type=percentile&state_code=US%3A35&county_code=US%3A35%3A043&normal_type=DOY&normal_type=MOY&interval_type=M&interval_type=CY&interval_type=WY)
- [New Mexico Water Data: groundwater levels](https://catalog.newmexicowaterdata.org/dataset/groundwater-levels/resource/de88e71a-3f5b-4bc9-8fb0-28b81c198952)
- [New Mexico Water Data: aquifer sensitivity](https://catalog.newmexicowaterdata.org/dataset/aquifer-sensitivity)
- [USGS station 08332525, Rio Puerco at Cuba (Water Quality Portal)](https://www.waterqualitydata.us/provider/NWIS/USGS-NM/USGS-08332525/)
- [USGS: Hydrogeology of the Ojo Alamo Sandstone in the San Juan Structural Basin](https://www.usgs.gov/publications/hydrogeology-ojo-alamo-sandstone-san-juan-structural-basin-new-mexico-colorado-arizona)
- [NM Geological Society: San Jose Formation Hydrostratigraphy near Lindrith](https://nmgs.nmt.edu/publications/guidebooks/details.cfml?ID=134492)
- [USGS San Juan Basin digital aquifer data (ScienceBase)](https://www.sciencebase.gov/catalog/item/5d8e350be4b0c4f70d0cc484)
- [USGS groundwater-flow model report, WRI 95-4187](https://pubs.usgs.gov/publication/wri954187)
- [NM Bureau of Geology: San Juan Basin Brackish Water Assessment](https://geoinfo.nmt.edu/resources/water/projects/bwa/sjb/home.html)
- [New Mexico Office of the State Engineer](https://www.ose.nm.gov/)
- [National Ground-Water Monitoring Network](https://www.usgs.gov/apps/ngwmn/index.jsp)
- [Healy Collaborative Groundwater Monitoring Network](https://geoinfo.nmt.edu/resources/water/cgmn/home.cfml)
- [New Mexico Water Data Catalog](https://catalog.newmexicowaterdata.org/)
- [NM Interstate Stream Commission: Acequias](https://www.ose.nm.gov/Acequias/isc_acequias.php)
