import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

st.title("County map")
st.write(
    "An interactive map of Sandoval County showing every site in the project's datasets: wells with "
    "water-level records, aquifer-test wells and drilling logs, and surface-water stations, including "
    "the Rio Puerco stream gage at Cuba."
)
st.caption(
    "Research questions 1 and 5. The Cuba case study page shows the aquifer-test wells near Cuba by "
    "formation. Scroll to zoom; hover a dot for its records."
)
finding_legend()

show_chart(charts.county_coverage_map)
