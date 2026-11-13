import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

# 1. Enable wide layout and mobile viewport support
st.set_page_config(page_title="Cuba Case Study", layout="wide")

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
            /* Stack columns gracefully on mobile */
            [data-testid="stHorizontalBlock"] {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Cuba case study")
st.write(
    "A closer look at the Ojo Alamo Sandstone and San Jose Formation near Cuba, what "
    "nearby records show about groundwater there, and whether they are enough to evaluate "
    "concern about severe decline. Stream measurements on the Rio Puerco at Cuba are "
    "shown as surface-water context."
)
st.caption("Research questions 3 and 4.")

k = charts.cuba_key_numbers()

# 2. Key Metrics: On mobile, columns automatically stack due to the CSS above, 
# ensuring large, readable metric cards.
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Nearest repeated water level", f"{k['nearest_water_level_km']:.0f} km",
              help=f"{k['nearest_water_level_name']}: {k['nearest_water_level_n']} readings, last in {k['nearest_water_level_last_year']}")
with c2:
    st.metric(f"Aquifer tests within {k['radius_km']} km", k["aquifer_test_wells_in_area"],
              help=f"One-time tests, {k['aquifer_test_years']}")
with c3:
    st.metric("Rio Puerco measurable flow", f"{k['rio_puerco_flowing']} of {k['rio_puerco_visits']}",
              help=f"USGS spot visits at Cuba, {k['rio_puerco_years']}")

st.info(
    "**Short answer to research question 3:** the collected data can't confirm or rule out severe "
    "decline in Cuba's aquifer. Wells near Cuba have only one-time water levels from aquifer tests "
    f"({k['aquifer_test_years']}); the nearest well measured more than once is "
    f"{k['nearest_water_level_km']:.0f} km away. Answering it needs Cuba's municipal well records "
    "(well IDs, the formation each well uses, pumping volumes, and water-level history) from the "
    "Village of Cuba or the NM Office of the State Engineer.",
    icon=":material/info:",
)

with st.expander("Map legend & context details", expanded=False):
    finding_legend()

# 3. Organize charts into tabs or expanders to prevent endless vertical scrolling on phones
chart_tab1, chart_tab2, chart_tab3, chart_tab4, chart_tab5 = st.tabs([
    "Area Map", "Nearest Records", "Ojo Alamo Depth", "Formations", "Rio Puerco"
])

with chart_tab1:
    show_chart(charts.cuba_area_map)
with chart_tab2:
    show_chart(charts.cuba_nearest_records)
with chart_tab3:
    show_chart(charts.ojo_alamo_depth_map)
with chart_tab4:
    show_chart(charts.ojo_alamo_vs_san_jose)
with chart_tab5:
    show_chart(charts.rio_puerco_visits)