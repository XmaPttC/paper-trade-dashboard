import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Terminal")

# Load data
df = pd.read_csv("mock_stock_data.csv")

# Define and enforce column order
column_order = [
    "Ticker", "Price", "TerminalScore", "PEG", "PE", "EPSGr", "MktCap",
    "30DayVol", "AnalystSc", "TrgtUpside", "Sector", "InsiderSc",
    "SentSc", "RedditSc", "52wH"
]
df = df[[col for col in column_order if col in df.columns]]

# --- CSS Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
html, body, .stApp, .block-container {
    font-family: 'Lato', sans-serif;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
}
.custom-panel {
    background-color: #334155;
    padding: 12px 16px;
    margin-bottom: 14px;
    border-radius: 4px;
    font-size: 13px;
}
.custom-panel h5 {
    margin: 0 0 8px 0;
    color: #93c5fd;
}
.inline-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.inline-row label {
    flex: 1;
}
.inline-row input, .inline-row .stSlider {
    flex: 2;
}
.apply-btn {
    background-color: #2563eb;
    color: white;
    border: none;
    padding: 8px 16px;
    font-size: 14px;
    border-radius: 4px;
    cursor: pointer;
}
.apply-btn:hover {
    background-color: #1d4ed8;
}
</style>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["Terminal", "Control Panel"])

with tab2:
    st.markdown("<h3 style='margin-bottom: 20px;'>Signal Settings</h3>", unsafe_allow_html=True)

    signals = [
        ("Web Traffic", "web", 0.25, 10),
        ("Mobile App Usage", "app", 0.20, 15),
        ("Institutional Spend", "spend", 0.20, 20),
        ("Job Postings", "jobs", 0.10, 5),
        ("Reddit Sentiment", "reddit", 0.10, 10),
        ("Shipping / Inventory", "ship", 0.10, 8),
        ("Options Flow", "options", 0.10, 20),
        ("Dark Pool Activity", "darkpool", 0.10, 20),
        ("Gamma Exposure (GEX)", "gex", 0.05, 1.5)
    ]

    cols = st.columns(3)
    for i, (label, key, default_weight, default_thresh) in enumerate(signals):
        col = cols[i % 3]
        with col:
            st.markdown(f"<div class='custom-panel'>", unsafe_allow_html=True)
            st.markdown(f"<h5>{label}</h5>", unsafe_allow_html=True)

            enabled = st.checkbox("Enable", key=f"{key}_enabled", value=True)
            weight = st.slider("Weight", 0.0, 1.0, value=default_weight, step=0.05, key=f"{key}_weight")
            threshold = st.number_input("Threshold", value=default_thresh, key=f"{key}_threshold")

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; margin-top: 24px;'>", unsafe_allow_html=True)
    if st.button("â Apply Settings"):
        st.success("Alt-data settings applied.")
    st.markdown("</div>", unsafe_allow_html=True)
