import streamlit as st
import pandas as pd

# ---- SETUP ----
st.set_page_config(layout="wide", page_title="Growth Stock Screener")
st.markdown("<style>body {background-color: #f8f9fa;}</style>", unsafe_allow_html=True)

# ---- LOAD DATA ----
df = pd.read_csv("mock_stock_data.csv")

# ---- INIT STATE ----
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()

if "standard_filters" not in st.session_state:
    st.session_state.standard_filters = {
        "pe_min": 0.0,
        "pe_max": 30.0,
        "peg_max": 1.5,
        "eps_min": 20,
        "rating_max": 3.0,
        "target_min": 30,
        "insider_allowed": ["Heavy Buying"]
    }

# ---- FILTER PANEL ----
with st.sidebar:
    st.title("📊 Filters")

    # Core Filters
    st.subheader("Core Fundamentals")
    pe_filter = st.checkbox("Enable PE Filter", value=True)
    if pe_filter:
        pe_min = st.number_input("Min P/E", value=st.session_state.standard_filters["pe_min"])
        pe_max = st.number_input("Max P/E", value=st.session_state.standard_filters["pe_max"])

    peg_filter = st.checkbox("Enable PEG Filter", value=True)
    if peg_filter:
        peg_max = st.slider("Max PEG", 0.0, 5.0, st.session_state.standard_filters["peg_max"])

    eps_filter = st.checkbox("Enable EPS Growth Filter", value=True)
    if eps_filter:
        eps_min = st.slider("Min EPS Growth (%)", 0, 100, st.session_state.standard_filters["eps_min"])

    # Analyst
    st.subheader("🔍 Analyst Ratings")
    analyst_filter = st.checkbox("Enable Analyst Rating Filter")
    if analyst_filter:
        rating_max = st.slider("Max Analyst Rating", 1.0, 5.0, st.session_state.standard_filters["rating_max"])

    # Target
    st.subheader("🎯 Target Price Upside")
    target_filter = st.checkbox("Enable Target Upside Filter")
    if target_filter:
        target_min = st.slider("Min Upside (%)", 0, 200, st.session_state.standard_filters["target_min"])

    # Insider
    st.subheader("🧑‍💼 Insider Activity")
    insider_filter = st.checkbox("Enable Insider Filter")
    if insider_filter:
        allowed = st.multiselect("Allowed Activities", ["Heavy Buying", "Net Buying"], default=st.session_state.standard_filters["insider_allowed"])

    # Buttons
    colA, colB = st.columns(2)
    if colA.button("Apply Filters"):
        st.session_state.filters_applied = True
    if colB.button("Apply Standard Filters"):
        st.session_state.filters_applied = True
        pe_min = st.session_state.standard_filters["pe_min"]
        pe_max = st.session_state.standard_filters["pe_max"]
        peg_max = st.session_state.standard_filters["peg_max"]
        eps_min = st.session_state.standard_filters["eps_min"]
        rating_max = st.session_state.standard_filters["rating_max"]
        target_min = st.session_state.standard_filters["target_min"]
        allowed = st.session_state.standard_filters["insider_allowed"]

    st.markdown("---")
    with st.expander("Change Standard Filters"):
        new_pe_min = st.number_input("PE Min", value=st.session_state.standard_filters["pe_min"], key="new_pe_min")
        new_pe_max = st.number_input("PE Max", value=st.session_state.standard_filters["pe_max"], key="new_pe_max")
        new_peg_max = st.slider("PEG Max", 0.0, 5.0, st.session_state.standard_filters["peg_max"], key="new_peg_max")
        new_eps_min = st.slider("EPS Growth Min", 0, 100, st.session_state.standard_filters["eps_min"], key="new_eps_min")
        new_rating_max = st.slider("Analyst Rating Max", 1.0, 5.0, st.session_state.standard_filters["rating_max"], key="new_rating_max")
        new_target_min = st.slider("Target Upside Min", 0, 200, st.session_state.standard_filters["target_min"], key="new_target_min")
        new_insider_allowed = st.multiselect("Insider Activities", ["Heavy Buying", "Net Buying"], default=st.session_state.standard_filters["insider_allowed"], key="new_insider_allowed")
        if st.button("Save as Standard Filters"):
            st.session_state.standard_filters.update({
                "pe_min": new_pe_min,
                "pe_max": new_pe_max,
                "peg_max": new_peg_max,
                "eps_min": new_eps_min,
                "rating_max": new_rating_max,
                "target_min": new_target_min,
                "insider_allowed": new_insider_allowed
            })
            st.success("Standard filters updated.")

# ---- FILTER LOGIC ----
filtered = df.copy()

if st.session_state.get("filters_applied"):
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

filtered = filtered[~filtered["Ticker"].isin(st.session_state.hidden_rows)]

# ---- MAIN VIEW ----
st.title("🚀 Undervalued Growth Stocks Screener")

if st.button("Restore All Hidden Rows"):
    st.session_state.hidden_rows.clear()
    st.success("All rows restored.")
    st.experimental_rerun()

if not filtered.empty:
    def make_row_html(row):
        ticker_link = f'<a href="{row.YahooFinanceLink}" target="_blank">{row.Ticker}</a>'
        simulate_btn = f'<button onclick="fetch(\'/_simulate_{row.Ticker}\')">Simulate</button>'
        hide_btn = f'<button onclick="fetch(\'/_hide_{row.Ticker}\')">Hide</button>'
        return pd.Series({
            "Ticker": ticker_link,
            "Price": f"${row.Price:.2f}",
            "PE": f"{row.PE:.1f}",
            "PEG": f"{row.PEG:.2f}",
            "EPS Growth": f"{row.EPS_Growth:.0f}%",
            "Rating": f"{row.AnalystRating:.1f}",
            "Upside": f"{row.TargetUpside:.0f}%",
            "Smart Score": f"{row.SmartScore:.2f}",
            "Insider": row.InsiderActivity,
            "Actions": f"<button onclick=\"window.location.reload();\">🙈 Hide {row.Ticker}</button> <button>📈 Simulate</button>"
        })

    styled = filtered.apply(make_row_html, axis=1)
    st.write(styled.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.warning("No stocks matched your filters or all have been hidden.")
