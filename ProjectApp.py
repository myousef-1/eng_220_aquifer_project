import streamlit as st

st.set_page_config(page_title="Beneath the Mesa", page_icon="💧", layout="wide")

# Phone layout: less side padding and smaller headings on narrow screens (every page).
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stApp {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# The sidebar menu. To add a page: create a file in app_pages/ and add a line here.
pg = st.navigation([
    st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("app_pages/county_map.py", title="County map", icon=":material/map:"),
    st.Page("app_pages/groundwater.py", title="Groundwater levels", icon=":material/water_drop:"),
    st.Page("app_pages/wells.py", title="Wells and aquifers", icon=":material/layers:"),
    st.Page("app_pages/cuba.py", title="Cuba case study", icon=":material/location_on:"),
    st.Page("app_pages/Waterestimater.py", title="Water Estimater", icon=":material/water_drop:"),
    st.Page("app_pages/data_sources.py", title="Data sources", icon=":material/database:"),
])
# Chart style for every page: six charts can show small pictograms (wells, gages, river visits,
# rating balls) instead of plain dots and bars; see analysis/icons.py. Off = the report's plain versions.
st.sidebar.toggle("Pictograph charts", value=True, key="pictograph",
                  help="Show pictograms on six charts. Turn off to see the plain versions used in the report.")
pg.run()
