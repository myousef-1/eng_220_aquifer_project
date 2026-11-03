import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

st.title("Groundwater levels")
st.write(
    "Water-level trends over time for wells with repeated measurements, "
    "showing where levels are declining, stable, or recovering."
)
st.caption(
    "Research question 1. None of these wells are near Cuba; each chart's scope line says how far away "
    "its wells are. The Cuba case study page shows what data exist there."
)
finding_legend()

show_chart(charts.groundwater_hydrographs)
st.divider()
show_chart(charts.groundwater_trends)
st.divider()
show_chart(charts.placitas_remeasured)
