import streamlit as st

from analysis import charts, data
from analysis.st_helpers import finding_legend, show_chart

st.title("Data sources")
st.write("The datasets behind this app and where they come from.")

_nm, _rp, _wl = data.load_nmbgmr_levels(), data.load_rio_puerco(), data.load_well_logs()
nm_rows, nm_wells = len(_nm), _nm["site_id"].nunique()
nm_years = f"{_nm['date'].dt.year.min()} to {_nm['date'].dt.year.max()}"
rp_n, rp_years = len(_rp), f"{_rp['date'].dt.year.min()} to {_rp['date'].dt.year.max()}"
wl_n, wl_years = len(_wl), f"{_wl['date'].dt.year.min()} to {_wl['date'].dt.year.max()}"

st.subheader("In the app")
st.markdown(
    f"""
- **USGS monitoring statistics** (`water_flow_data_sandoval_county_sources.csv`): monthly and yearly
  statistics for 30 monitoring sites in Sandoval County, covering streamflow, groundwater levels,
  reservoir storage, sediment, temperature, and water quality, from 1926 to 2026.
- **OSE aquifer tests** (`ose_aquifer_test_wells.csv`, cleaned into `data/clean/aquifer_tests.csv`, which
  the charts use): New Mexico Office of the State Engineer aquifer-test records, including well depth,
  geologic formation, and hydraulic properties.
- **NMBGMR groundwater levels** (`data2_groundwater_sandoval_county.csv`): {nm_rows} depth-to-water
  measurements from {nm_wells} wells, mostly around Placitas, {nm_years}.
- **Rio Puerco at Cuba** (`data4_*.csv`): {rp_n} USGS streamflow visits at Cuba, {rp_years}.
- **OSE well logs** (`data7_Wells With Well Log Information.csv`): drilling records for {wl_n} wells in
  the northwest of the county, {wl_years}.
- **Aquifer sensitivity** (`data3_Aquifer_Sensitivity.csv`): mapped areas with a sensitivity class,
  but no locations yet, so it is summarized below rather than mapped.
- **San Jose Formation study** (`data6_...pdf`, Blandford et al. 2025): published transmissivity values
  shown on the Cuba case study page. The Ojo Alamo map plate (`data5_...pdf`) is a scanned image; a
  labeled crop of its depth map is shown on the Cuba case study page, but it isn't digitized.
"""
)

st.subheader("Other sources")
st.markdown(
    """
- [USGS San Juan Basin digital aquifer data](https://www.sciencebase.gov/catalog/item/5d8e350be4b0c4f70d0cc484)
- [New Mexico Office of the State Engineer](https://www.ose.nm.gov/)
- [National Ground-Water Monitoring Network](https://www.usgs.gov/apps/ngwmn/index.jsp)
- [New Mexico Water Data Catalog](https://catalog.newmexicowaterdata.org/)
"""
)

st.divider()
st.header("Monitoring coverage and data gaps")
st.caption("Research questions 5 and 6.")
finding_legend()
show_chart(charts.coverage_timeline)
st.divider()
show_chart(charts.evidence_matrix)
st.divider()
show_chart(charts.aquifer_sensitivity_classes)
st.divider()
st.subheader("Indicators for a groundwater-stress dashboard")
st.caption(
    "Research question 6: indicators the data can support, where each applies, and how much to trust it. "
    "Values are computed from the data."
)
st.table(charts.indicator_table().set_index("Indicator"))  # st.table wraps long text instead of scrolling
