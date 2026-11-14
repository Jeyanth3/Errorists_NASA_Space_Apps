"""FireWise - entry point.  run:  streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="FireWise | Spacecraft fire-safety evidence", page_icon="🔥", layout="wide")

pages = {
    "Start": [
        st.Page("views/home.py", title="Overview", icon="🔥", default=True),
    ],
    "Explore": [
        st.Page("views/mission.py", title="Mission Explorer", icon="🚀"),
        st.Page("views/atmosphere.py", title="Atmosphere Map", icon="🗺️"),
        st.Page("views/pillars.py", title="Prevent · Detect · Suppress", icon="🧯"),
        st.Page("views/compare.py", title="Compare Runs", icon="⚖️"),
        st.Page("views/ask.py", title="Ask FireWise", icon="💬"),
    ],
    "Trust": [
        st.Page("views/data_audit.py", title="Data Reliability", icon="🔎"),
        st.Page("views/about.py", title="Method & Sources", icon="📚"),
    ],
}

st.navigation(pages).run()
