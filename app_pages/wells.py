import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

# 1. Configure page title and wide layout support
st.set_page_config(page_title="Wells and Aquifers", layout="wide")

# 2. Add responsive CSS for mobile padding and clean headers
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

st.title("Wells and aquifers")
st.write(
    "Well depth, depth to water, and the aquifer units wells draw from, "
    "compared across the county."
)
st.caption("Research question 2, and part of research question 4.")

# 3. Put the legend inside an expander to save precious vertical space on small screens
with st.expander("Map legend details", expanded=False):
    finding_legend()

# 4. Organize charts and interactive formation selector into tabs to prevent mobile scroll fatigue
chart_tab1, chart_tab2, chart_tab3 = st.tabs([
    "Well Depth vs Water", "Depth by Area", "Formation Properties"
])

with chart_tab1:
    show_chart(charts.well_depth_vs_water)

with chart_tab2:
    show_chart(charts.depth_by_area)

with chart_tab3:
    metric_labels = {k: v[0] for k, v in charts.FORMATION_METRICS.items()}
    metric = st.selectbox(
        "Aquifer-test measurement to compare by formation",
        options=list(metric_labels),
        format_func=metric_labels.get,
    )
    show_chart(charts.formation_properties, metric=metric)