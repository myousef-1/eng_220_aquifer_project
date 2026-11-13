import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

# 1. Use wide layout to maximize screen width on mobile devices
st.set_page_config(page_title="Sandoval County Map", layout="wide")

# 2. Reduce excessive default padding and scale title font on mobile screens
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
            /* Prevent legend items from squishing horizontally */
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap;
                gap: 0.5rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("County map")

# 3. Update interaction hints for touchscreens
st.caption("Pinch to zoom; tap a dot for its records.")

# 4. Put the legend and lengthy context in an expander so the map stays above the fold
with st.expander("Map legend & dataset details", expanded=False):
    finding_legend()
    st.write(
        "An interactive map of Sandoval County showing every site in the project's datasets: "
        "wells with water-level records, aquifer-test wells and drilling logs, and surface-water "
        "stations, including the Rio Puerco stream gage at Cuba."
    )
    st.caption(
        "Research questions 1 and 5. The Cuba case study page shows the aquifer-test wells near "
        "Cuba by formation."
    )

# 5. Ensure your show_chart helper passes use_container_width=True to st.plotly_chart / st.altair_chart
show_chart(charts.county_coverage_map)