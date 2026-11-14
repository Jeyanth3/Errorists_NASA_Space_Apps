"""FireWise - entry point.  run:  streamlit run app.py"""
import streamlit as st

from firewise import ui

st.set_page_config(page_title="FireWise | Spacecraft fire-safety evidence", page_icon="assets/campfire.png",
                   layout="wide", initial_sidebar_state="expanded")
st.logo("assets/logo_wide.png", icon_image="assets/campfire.png", size="large")
ui.setup()

pages = {
    "Start": [
        st.Page("views/home.py", title="Overview", icon=":material/home:", default=True),
    ],
    "Explore": [
        st.Page("views/mission.py", title="Mission Explorer", icon=":material/rocket_launch:"),
        st.Page("views/atmosphere.py", title="Atmosphere Map", icon=":material/map:"),
        st.Page("views/pillars.py", title="Safety Pillars", icon=":material/local_fire_department:"),
        st.Page("views/compare.py", title="Compare Runs", icon=":material/balance:"),
        st.Page("views/ask.py", title="Ask FireWise", icon=":material/forum:"),
    ],
    "Trust": [
        st.Page("views/data_audit.py", title="Data Reliability", icon=":material/fact_check:"),
        st.Page("views/about.py", title="Method and Sources", icon=":material/menu_book:"),
    ],
}

st.navigation(pages).run()
