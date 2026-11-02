import streamlit as st

st.title("Data sources")
st.write("The datasets behind this app and where they come from.")

st.subheader("In the app")
st.markdown(
    """
- **USGS monitoring statistics** (`water_flow_data_sandoval_county_sources.csv`): monthly and yearly
  statistics for 30 monitoring sites in Sandoval County, covering streamflow, groundwater levels,
  reservoir storage, sediment, temperature, and water quality, from 1926 to 2026.
- **OSE aquifer tests** (`ose_aquifer_test_wells.csv`): New Mexico Office of the State Engineer
  aquifer-test records, including well depth, geologic formation, and hydraulic properties.
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

st.info("Monitoring coverage and data gaps (research question 5) will be added here.", icon=":material/construction:")
