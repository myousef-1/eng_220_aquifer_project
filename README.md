# Beneath the Mesa
### Assessing Aquifer and Well Water Resources Across Sandoval County, New Mexico

**ENG 220 – Team 23**

**[Live app](https://eng220aquiferproject.streamlit.app/)** | **[Documentation site](https://pdjordj11.github.io/eng_220_aquifer_project/)** | **[Slides and video](https://pdjordj11.github.io/eng_220_aquifer_project/presentation/)** | **[Report](https://pdjordj11.github.io/eng_220_aquifer_project/report/)**

## Team Roles

- **Petar Djordjevic (Prime Minister):** Video editing; building the PowerPoint presentation; writing documentation and the final project report; assisting other members as needed.
- **Dylan Gonzales:** Data acquisition and dataset justification.
- **James Wauneka:** Data cleaning and preprocessing.
- **Micah Watkins:** Writing analysis code and producing visualizations.
- **Meckrem Yousef:** Managing GitHub workflow and building the Streamlit application.


## Running the App

Streamlit apps must be started with `streamlit run`. The ▶ play button and `python ProjectApp.py` won't open the app; they only print "missing ScriptRunContext" warnings.

**In GitHub Codespaces (recommended):** On the repo page, click **Code → Codespaces** and open a codespace. The app starts automatically in a preview pane. If it doesn't, run this in the terminal:

```
streamlit run ProjectApp.py
```

**On your own computer:**

```
pip install -r requirements.txt
streamlit run ProjectApp.py
```

The app opens at http://localhost:8501. Press **Ctrl+C** in the terminal to stop it.

## Updating the Live App

The live app runs whatever is on the `main` branch on GitHub. Running the app in a codespace or on your computer does **not** update it. To publish changes:

```
git pull
git add -A
git commit -m "Describe your change"
git push
```

The live app updates within about a minute.

- Always run `git pull` before you start working, to avoid merge conflicts.
- If you use a new Python package, add it to `requirements.txt` and double-check the spelling, or the live app will fail to start.

## Updating the Documentation Site

The documentation site is built with [MkDocs](https://www.mkdocs.org). Its pages are the Markdown files in `docs/`, and the site settings are in `mkdocs.yml`.

1. Edit or add `.md` files in `docs/`.
2. Preview the site (opens at http://127.0.0.1:8000; press **Ctrl+C** to stop):

```
   pip install mkdocs mkdocs-cinder
   mkdocs serve
```

3. Publish it to the documentation site:

```
   mkdocs gh-deploy
```

4. Commit and push your Markdown changes to `main` as usual, so the source stays in sync with the site.

`mkdocs gh-deploy` builds the site and pushes it to the `gh-pages` branch, which is what the documentation link serves. The built `site/` folder is listed in `.gitignore`, so it is never committed to `main`.

## Project Structure

```
ProjectApp.py        Streamlit app entry point and sidebar menu (do not rename: the live app runs this file)
app_pages/           One file per page of the Streamlit app
requirements.txt     Python packages the live app installs
mkdocs.yml           Documentation site settings
data/                Raw datasets as downloaded (never edited)
data/clean/          Cleaned datasets, made by the scripts in cleaning/
cleaning/            Data cleaning scripts
docs/                Documentation site pages (MkDocs)
docs/files/          Presentation slides, report PDF, and other downloads
report/              Final report LaTeX source (see report/README.md)
project_notes/       Proposal, deadlines, and notes
.devcontainer/       Codespaces setup
```

## Adding a Page to the App

Each page of the app is its own file in `app_pages/`, and `ProjectApp.py` lists them in the sidebar menu.

1. Create a new file in `app_pages/`, for example `app_pages/my_page.py`. Don't call `st.set_page_config` in it; `ProjectApp.py` already does.
2. Add a line for it to the list in `ProjectApp.py`:

```python
st.Page("app_pages/my_page.py", title="My page", icon=":material/insights:"),
```

Icons are optional. Any name from [Google's Material Symbols](https://fonts.google.com/icons) works.

## Loading Data in the App

Build file paths from the file's location so they work in Codespaces, on your computer, and on the live app. Pages live one folder down in `app_pages/`, so go up one level to reach `data/`. Load the cleaned files in `data/clean/`, not the raw downloads:

```python
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "clean"
levels = pd.read_csv(DATA / "groundwater_levels_monthly.csv")
```
