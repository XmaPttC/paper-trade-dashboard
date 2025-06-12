import streamlit as st
import pandas as pd

# ---- SETUP ----
st.set_page_config(layout="wide", page_title="Growth Stock Screener")
st.markdown("<style>body {background-color: #f8f9fa;}</style>", unsafe_allow_html=True)

# ---- LOAD DATA ----
df = pd.read_csv("mock_stock_data.csv")

# Initialize session state for hiding rows
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()

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

    st.subheader("🎯 Target Price Upside")
    target_filter = st.checkbox("Enable Target Upside Filter")
    if target_filter:
        target_min = st.slider("Min Upside (%)", 0, 200, 30)

    st.subheader("🧑‍💼 Insider Activity")
    insider_filter = st.checkbox("Enable Insider Filter")
    if insider_filter:
        allowed = st.multiselect("Allowed Activities", ["Heavy Buying", "Net Buying"], default=["Heavy Buying"])

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
        filtered = filtered[filtered["InsiderActivity"].isin(allowed)]

    st.success(f"Filtered to {len(filtered)} stocks")

# ---- REMOVE HIDDEN ROWS ----
filtered = filtered[~filtered["Ticker"].isin(st.session_state.hidden_rows)]

# ---- MAIN TABLE ----
st.title("🚀 Undervalued Growth Stocks Screener")

def format_link(ticker, url):
    return f"[{ticker}]({url})"

if not filtered.empty:
    # Create display DataFrame
    display_df = filtered.copy()
    display_df["Ticker"] = display_df.apply(lambda row: format_link(row["Ticker"], row["YahooFinanceLink"]), axis=1)
    display_df = display_df[["Ticker", "Price", "PE", "PEG", "EPS_Growth", "AnalystRating", "TargetUpside", "SmartScore", "InsiderActivity"]]
    display_df = display_df.sort_values("SmartScore", ascending=False)

    # Format and display
    st.dataframe(
        display_df.style.format({
            "Price": "${:.2f}",
            "PE": "{:.1f}",
            "PEG": "{:.2f}",
            "EPS_Growth": "{:.0f}%",
            "TargetUpside": "{:.0f}%",
            "SmartScore": "{:.2f}"
        }),
        use_container_width=True
    )

    # Row-level actions
    st.subheader("Row Actions")
    for ticker in filtered["Ticker"]:
        cols = st.columns([3, 1, 1])
        cols[0].markdown(f"**{ticker}**")
        if cols[1].button("🙈 Hide", key=f"hide_{ticker}"):
            st.session_state.hidden_rows.add(ticker)
            st.experimental_rerun()
        if cols[2].button("📈 Simulate", key=f"sim_{ticker}"):
            st.success(f"Simulated trade for {ticker}")

else:
    st.warning("No stocks matched your filters or all have been hidden.")
