# Beneath the Mesa

**Assessing Aquifer and Well Water Resources Across Sandoval County, New Mexico**

ENG 220 · Team 23

[Open the live app](https://eng220aquiferproject.streamlit.app/) · [View the code on GitHub](https://github.com/pdjordj11/eng_220_aquifer_project)

## About the project

Water scarcity is a persistent challenge across New Mexico. Sandoval County spans several hydrogeologic settings, and its communities depend on a mix of groundwater wells, surface water, and acequia irrigation systems.

This project focuses on groundwater: it evaluates the condition of the county's aquifers and wells, with Cuba, New Mexico, on the eastern edge of the San Juan Basin, as a focused case study. The project is motivated by concern about declining groundwater near Cuba, but rather than assume how severe that decline is or what is causing it, we test what the available public data actually show, and where they are too sparse to say.

## Approach

The study works at two levels:

- **County-wide screening.** Map and compare aquifers, wells, and groundwater levels across Sandoval County. Because the county crosses several geologic regions, comparisons are grouped by aquifer unit instead of treating the county as one uniform aquifer.
- **Cuba case study.** A closer look at the Ojo Alamo Sandstone and San Jose Formation near Cuba, using published maps of both formations, aquifer-test records from nearby wells, and stream measurements on the Rio Puerco at Cuba.

The analysis focuses on measurable indicators such as depth to water, water-level change over time, well depth, aquifer unit, and hydraulic properties from aquifer tests, rather than a full hydrologic model. Where records are sparse, the results say so instead of filling the gaps.

## Peace engineering

The project follows a peace-engineering approach: using engineering and science to support peace. Disagreements over water often begin with disagreement about the facts, so the project combines scattered public records into one open, reproducible analysis, labels every finding by how certain it is, and publishes the data, code, and dashboard for residents, the Village of Cuba, and state agencies to use. It also makes an equity issue visible: monitoring is concentrated where most people live, while small rural communities such as Cuba, which rely on their own wells, have the least information about their aquifers.

## Research questions

1. How have groundwater levels changed at monitored wells in Sandoval County, and which wells show sustained decline, stability, or recovery?
2. What do well records show about well depth, depth to water, and the aquifer units that wells in different parts of the county draw from?
3. What do available records show about groundwater near Cuba, and are they enough to evaluate the concern that its main aquifer is approaching severe depletion?
4. How do the Ojo Alamo Sandstone and San Jose Formation compare near Cuba in extent, thickness, and hydraulic properties?
5. Where is monitoring coverage strong, and where are the most important data gaps?
6. Which indicators can be combined into a dashboard that shows groundwater stress without overstating how certain the data are?

The project proposal had nine questions. Three of them, on groundwater quality, acequias, and links between groundwater and surface water, were dropped because the data needed to answer them weren't available (see [Not collected](data-collection.md#not-collected)).

## How this site is organized

The site follows the project's stages, from collecting data to presenting results. Each stage page explains what was done, which files it produced, and who led it.

| Page | What it covers |
|---|---|
| [1. Data collection](data-collection.md) | The datasets we use, where they come from, and why we chose them |
| [2. Data cleaning](data-cleaning.md) | How the raw data is filtered and prepared for analysis |
| [3. Analysis and visualizations](analysis.md) | The methods and charts used to answer each research question |
| [4. Streamlit app](streamlit-app.md) | What the interactive dashboard shows and how to run it |
| [5. Final report](report.md) | The written report and the project proposal |
| [6. Presentation and video](presentation.md) | The in-class presentation slides and each member's video |
| [Findings](findings.md) | What the data show, and where they are too limited to say |
| [Timeline](timeline.md) | What was completed at each course checkpoint |
| [Team](team.md) | Who did what |
