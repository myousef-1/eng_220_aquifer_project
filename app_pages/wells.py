import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

st.title("Wells and aquifers")
st.write(
    "Well depth, depth to water, and the aquifer units wells draw from, "
    "compared across the county."
)
st.caption("Research question 2, and part of research question 4.")
finding_legend()

show_chart(charts.well_depth_vs_water)
st.divider()
show_chart(charts.depth_by_area)
st.divider()

metric_labels = {k: v[0] for k, v in charts.FORMATION_METRICS.items()}
metric = st.selectbox(
    "Aquifer-test measurement to compare by formation",
    options=list(metric_labels),
    format_func=metric_labels.get,
)
show_chart(charts.formation_properties, metric=metric)
