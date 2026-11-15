# 4. Streamlit app

**Lead:** Meckrem Yousef

[Open the live app](https://eng220aquiferproject.streamlit.app/)

The interactive dashboard presents the project's results. It's built with Streamlit, pandas, and Plotly, and runs from `ProjectApp.py` in the repository.

## What the app shows

Each page shows its charts with a one-line takeaway, what is plotted, the chart's scope (Cuba, the Cuba area, or Sandoval County), a caption, the findings labeled *Measured*, *Hypothesis*, or *Insufficient data*, and a "Data behind this chart" table with a CSV download. Charts are interactive: hover for exact values, drag to zoom, double-click to reset. They follow the app's light or dark theme. Six charts show small pictograms (wells, stream gages, river visits, rating balls); the **Pictograph charts** switch in the sidebar turns them off to show the plain versions used in the report (see [Pictograph versions](analysis.md#pictograph-versions)).

| Page | What it shows | Research questions |
|---|---|---|
| Home | Project summary, links, and the research questions | All |
| County map | Every site in the project's datasets on a map, colored by what it measures | 1, 5 |
| Groundwater levels | Monthly water levels at the 9 USGS monitoring wells, their trends, and Placitas wells re-measured after 20 years | 1 |
| Wells and aquifers | Well depth vs depth to water, depth to water by area, and aquifer-test properties by formation (choose the measurement from a menu) | 2, 4 |
| Cuba case study | Key numbers, a short answer to research question 3, a map of sites near Cuba, the nearest record in each dataset, the USGS Ojo Alamo depth map around Cuba, Ojo Alamo vs San Jose tests, and Rio Puerco visits | 3, 4 |
| Data sources | Dataset list and links, a timeline of monitoring coverage, a dataset-by-question evidence matrix, aquifer-sensitivity classes, and a table of groundwater-stress indicators | 5, 6 |
| Sandbox | A test page with random data (not project results) | - |
| Water Estimator | Estimates a household's daily and monthly water use from everyday activities (showers, toilet flushes, faucet use, laundry, and dishwasher loads), compares the daily total with a New Mexico residential average of 81 gallons a day, and estimates a monthly water bill. The bill's base fee, included gallons, and rate per 1,000 gallons are starting values to replace with the numbers on a Village of Cuba utility statement. | - |

The chart code lives in `analysis/` (see [Analysis and visualizations](analysis.md)); each page file in `app_pages/` calls `show_chart(...)` for its charts. The maps use the free CARTO basemap, which needs an internet connection.

## Look and phone layout

The app's colors are set in `.streamlit/config.toml` under `[theme]`: a blue background, a green accent, and light text. On narrow screens such as phones, a few lines of CSS at the top of `ProjectApp.py` reduce the side padding and shrink the headings, for every page.

On Nov 12, the theme file was fixed so Streamlit could read it again. A block of Python had been pasted into it and its `[theme]` heading removed, so the app had been ignoring the file. The Python, which holds the phone-layout CSS, moved to `ProjectApp.py`.

## Running it yourself

In GitHub Codespaces, open a codespace from the repository's **Code** button and the app starts automatically. On your own computer:

```
pip install -r requirements.txt
streamlit run ProjectApp.py
```

## How the live app updates

The live app runs whatever is on the repository's `main` branch and redeploys within about a minute of each push.
