import streamlit as st

from analysis import charts
from analysis.st_helpers import finding_legend, show_chart

st.title("Cuba case study")
st.write(
    "A closer look at the Ojo Alamo Sandstone and San Jose Formation near Cuba, what "
    "nearby records show about groundwater there, and whether they are enough to evaluate "
    "concern about severe decline. Stream measurements on the Rio Puerco at Cuba are "
    "shown as surface-water context."
)
st.caption("Research questions 3 and 4.")

k = charts.cuba_key_numbers()
c1, c2, c3 = st.columns(3)
c1.metric("Nearest well with repeated water levels", f"{k['nearest_water_level_km']:.0f} km",
          help=f"{k['nearest_water_level_name']}: {k['nearest_water_level_n']} readings, last in "
               f"{k['nearest_water_level_last_year']}")
c2.metric(f"Wells with aquifer tests within {k['radius_km']} km", k["aquifer_test_wells_in_area"],
          help=f"One-time tests, {k['aquifer_test_years']}")
c3.metric("Rio Puerco visits with measurable flow", f"{k['rio_puerco_flowing']} of {k['rio_puerco_visits']}",
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
finding_legend()

show_chart(charts.cuba_area_map)
st.divider()
show_chart(charts.cuba_nearest_records)
st.divider()
show_chart(charts.ojo_alamo_depth_map)
st.divider()
show_chart(charts.ojo_alamo_vs_san_jose)
st.divider()
show_chart(charts.rio_puerco_visits)
