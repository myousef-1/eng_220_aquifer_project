import streamlit as st

st.title("Beneath the Mesa")
st.subheader("Assessing Aquifer and Well Water Resources Across Sandoval County, New Mexico")
st.caption("ENG 220 · Team 23")

st.write(
    "Sandoval County's communities depend on a mix of groundwater wells, surface water, "
    "and acequia irrigation systems. This app focuses on groundwater: it explores what "
    "public data show about the county's aquifers and wells, with a closer look at Cuba, "
    "New Mexico, on the eastern edge of the San Juan Basin, and shows where the data are "
    "too sparse to say."
)

st.write(
    "Use the menu on the left to explore each part of the project. "
    "On a phone, tap the **»** button at the top left to open it."
)

col1, col2, col3, _ = st.columns([1, 1, 1, 1])
with col1:
    st.link_button("Project documentation", "https://pdjordj11.github.io/eng_220_aquifer_project/")
with col2:
    st.link_button("Code on GitHub", "https://github.com/pdjordj11/eng_220_aquifer_project")
with col3:
    st.link_button("Slides and video", "https://pdjordj11.github.io/eng_220_aquifer_project/presentation/")

with st.expander("Research questions"):
    st.markdown(
        """
1. How have groundwater levels changed at monitored wells in Sandoval County, and which wells show sustained decline, stability, or recovery?
2. What do well records show about well depth, depth to water, and the aquifer units that wells in different parts of the county draw from?
3. What do available records show about groundwater near Cuba, and are they enough to evaluate the concern that its main aquifer is approaching severe depletion?
4. How do the Ojo Alamo Sandstone and San Jose Formation compare near Cuba in extent, thickness, and hydraulic properties?
5. Where is monitoring coverage strong, and where are the most important data gaps?
6. Which indicators can be combined into a dashboard that shows groundwater stress without overstating how certain the data are?
"""
    )
