import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

# 1. Enable wide layout and mobile viewport configuration
st.set_page_config(page_title="Groundwater Levels", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        @media (max-width: 640px) {
            h1 {
                font-size: 1.75rem !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Groundwater levels")
st.write(
    "Water-level trends over time for wells with repeated measurements, "
    "showing where levels are declining, stable, or recovering."
)
st.caption(
    "Research question 1. None of these wells are near Cuba; each chart's scope line says how far away "
    "its wells are. The Cuba case study page shows what data exist there."
)

# 2. Put the legend inside an expander to keep the primary charts closer to the top on mobile
with st.expander("Map legend & scope details", expanded=False):
    finding_legend()

# 3. Organize the three detailed charts into tabs to prevent endless vertical scrolling on phones
chart_tab1, chart_tab2, chart_tab3 = st.tabs([
    "Hydrographs", "Trends", "Placitas Remeasured"
])

with chart_tab1:
    show_chart(charts.groundwater_hydrographs)
with chart_tab2:
    show_chart(charts.groundwater_trends)
with chart_tab3:
    show_chart(charts.placitas_remeasured)