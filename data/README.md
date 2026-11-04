# Data

Raw datasets as downloaded. **Never edit these files.** Cleaning scripts in `cleaning/` read them and write cleaned versions to `data/clean/`, and the analysis code in `analysis/data.py` reads them directly when no cleaned version exists yet.

Datasets 1 to 7 match Dylan's dataset briefs. What each dataset contains, where it came from, and what it can and can't show are on the docs site's [Data collection page](https://pdjordj11.github.io/eng_220_aquifer_project/data-collection/).

| # | File | Contents | Source |
|---|---|---|---|
| 1 | `water_flow_data_sandoval_county_sources.csv` | USGS monthly and yearly statistics for 30 monitoring sites in Sandoval County; the project uses the depth-to-water records for 9 wells | USGS Water Data statistics download |
| 2 | `data2_groundwater_sandoval_county.csv` | 456 depth-to-water measurements at 87 wells, 1997 to 2019 | NM Bureau of Geology and Mineral Resources, via New Mexico Water Data |
| 3 | `data3_Aquifer_Sensitivity.csv` | Sensitivity class for 613 mapped areas (no coordinates) | NM Environment Department, via New Mexico Water Data |
| 4 | `data4_monitoring-location-metadata.csv`, `data4_field-measurements.csv`, `data4_channel-measurements.csv` | Rio Puerco at Cuba (USGS station 08332525): station details, 4 gage-height readings, and 10 streamflow measurements | USGS Water Data for the Nation |
| 5 | `data5_ojo_alamo_sandstone_pub.pdf` | Map plate: hydrogeology of the Ojo Alamo Sandstone (USGS Hydrologic Atlas 720-B, 1990) | USGS |
| 6 | `data6_cuba_mesa_member_of_san_jose_formation.pdf` | Paper: San Jose Formation hydrostratigraphy near Lindrith (NMGS Guidebook 75, 2025) | New Mexico Geological Society |
| 7 | `data7_Wells With Well Log Information.csv` | Drilling records for 6 Sandoval County wells, 1978 to 2022 | NM Office of the State Engineer, Water Rights Reporting System |
| | `ose_aquifer_test_wells.csv` | Aquifer tests statewide, 179 of them in Sandoval County: well construction, formation, and hydraulic properties | NM Office of the State Engineer, Aquifer Test Index |
| | `sandoval_county_boundary.geojson` | Simplified county outline used as map context | US Census Bureau, via plotly/datasets |

`clean/` holds the cleaned files; see [`clean/README.md`](clean/README.md).
