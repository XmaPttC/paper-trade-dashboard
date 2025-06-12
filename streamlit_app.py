import streamlit as st
import pandas as pd

# ---- PAGE SETUP ----
st.set_page_config(layout="wide", page_title="Growth Stock Screener")
st.markdown("<style>body {background-color: #f8f9fa;}</style>", unsafe_allow_html=True)

# ---- LOAD MOCK DATA ----
df = pd.read_csv("mock_stock_data.csv")

# Preserve original for reset
if "original_data" not in st.session_state:
    st.session_state.original_data = df.copy()

# ---- FILTER PANEL ----
with st.sidebar:
    st.title("📊 Filters")

    st.subheader("Core Fundamentals")
    pe_filter = st.checkbox("Enable PE Filter", value=True)
    if pe_filter:
        pe_min = st.number_input("Min P/E", value=0.0)
        pe_max = st.number_input("Max P/E", value=30.0)

    peg_filter = st.checkbox("Enable PEG Filter", value=True)
    if peg_filter:
        peg_max = st.slider("Max PEG", 0.0, 5.0, 1.5)

    eps_filter = st.checkbox("Enable EPS Growth Filter", value=True)
    if eps_filter:
        eps_min = st.slider("Min EPS Growth (%)", 0, 100, 20)

    st.subheader("🔍 Analyst Ratings")
    analyst_filter = st.checkbox("Enable Analyst Rating Filter")
    if analyst_filter:
        rating_max = st.slider("Max Analyst Rating (1=Strong Buy, 5=Sell)", 1.0, 5.0, 3.0)

    st.subheader("🎯 Price Target")
    target_filter = st.checkbox("Enable Target Price Upside Filter")
    if target_filter:
        target_min = st.slider("Min Upside (%)", 0, 200, 30)

    st.subheader("🧑‍💼 Insider Activity")
    insider_filter = st.checkbox("Enable Insider Activity Filter")
    if insider_filter:
        allowed_activities = st.multiselect("Allowed Activities", ["Heavy Buying", "Net Buying"], default=["Heavy Buying"])

    # Apply Button
    apply = st.button("Apply Filters")

# ---- APPLY FILTERS ----
filtered = df.copy()

if apply:
    if pe_filter:
        filtered = filtered[(filtered["PE"] >= pe_min) & (filtered["PE"] <= pe_max)]
    if peg_filter:
        filtered = filtered[filtered["PEG"] <= peg_max]
    if eps_filter:
        filtered = filtered[filtered["EPS_Growth"] >= eps_min]
    if analyst_filter:
        filtered = filtered[filtered["AnalystRating"] <= rating_max]
    if target_filter:
        filtered = filtered[filtered["TargetUpside"] >= target_min]
    if insider_filter:
        filtered = filtered[filtered["InsiderActivity"].isin(allowed_activities)]

    st.success(f"Filtered to {len(filtered)} stocks")

# ---- MAIN VIEW ----
st.title("🚀 Undervalued Growth Stocks Screener")

# Row action placeholders
def render_row(row):
    simulate_button = st.button("📈 Simulate", key=f"sim_{row.Ticker}")
    hide_button = st.button("🙈 Hide", key=f"hide_{row.Ticker}")
    return simulate_button or hide_button

# Show table
if not filtered.empty:
    styled = filtered.style.format({
        "Price": "${:.2f}",
        "PE": "{:.1f}",
        "PEG": "{:.2f}",
        "EPS_Growth": "{:.0f}%",
        "TargetUpside": "{:.0f}%"
    })
    st.dataframe(styled, use_container_width=True)
else:
    st.warning("No stocks matched your filter criteria.")
