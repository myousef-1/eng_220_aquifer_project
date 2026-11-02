import streamlit as st

st.set_page_config(page_title="Beneath the Mesa", page_icon="💧", layout="wide")

# The sidebar menu. To add a page: create a file in app_pages/ and add a line here.
pg = st.navigation([
    st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("app_pages/county_map.py", title="County map", icon=":material/map:"),
    st.Page("app_pages/groundwater.py", title="Groundwater levels", icon=":material/water_drop:"),
    st.Page("app_pages/wells.py", title="Wells and aquifers", icon=":material/layers:"),
    st.Page("app_pages/cuba.py", title="Cuba case study", icon=":material/location_on:"),
    st.Page("app_pages/data_sources.py", title="Data sources", icon=":material/database:"),
    st.Page("app_pages/sandbox.py", title="Sandbox", icon=":material/construction:"),
])
pg.run()
