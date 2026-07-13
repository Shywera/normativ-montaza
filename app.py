"""
app.py  —  Normativi 2025  (navigation shell)
"""
import streamlit as st

st.set_page_config(
    page_title="Normativi 2025",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("pages/kompleti.py",      title="Montaža kompleta",  icon="🗂️"),
    st.Page("pages/jedna_etiketa.py", title="Normativ — rezanje", icon="✂️"),
])
pg.run()
