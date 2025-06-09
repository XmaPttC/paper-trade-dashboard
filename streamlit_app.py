import streamlit as st
import pandas as pd

# -------------------------------
# Dummy Data for the Screener Table
# -------------------------------
data = [
    {"ticker": "AAPL", "price": 185.2, "pe": 29.8, "peg": 2.1, "eps_growth": 18.5, "market_cap": 2800000000000},
    {"ticker": "GOOGL", "price": 128.3, "pe": 26.4, "peg": 1.8, "eps_growth": 20.2, "market_cap": 1800000000000},
    {"ticker": "SMCI", "price": 900.5, "pe": 32.7, "peg": 0.9, "eps_growth": 75.0, "market_cap": 45000000000},
    {"ticker": "TSLA", "price": 180.7, "pe": 45.1, "peg": 2.9, "eps_growth": 25.3, "market_cap": 700000000000},
]
df = pd.DataFrame(data)

# -------------------------------
# Session State Initialization
# -------------------------------
st.session_state.setdefault("hidden_tickers", set())
st.session_state.setdefault("sort_by", "ticker")
st.session_state.setdefault("sort_ascending", True)
st.session_state.setdefault("show_restore_alert", False)
st.session_state.setdefault("show_filter_popup", False)

# Default standard filters
default_filters = {
    "pe_range": (0.0, 15.0),
    "peg_range": (0.0, 1.0),
    "eps_growth_min": 20.0,
    "market_cap_min": 300_000_000,
}
for k, v in default_filters.items():
    st.session_state.setdefault(f"standard_{k}", v)

# -------------------------------
# UI Title
# -------------------------------
st.title("📊 Stock Screener")

# -------------------------------
# Standard Filter Controls
# -------------------------------
st.subheader("Filters")
col_apply, col_edit = st.columns([2, 3])
if col_apply.button("✅ Apply Standard Filters"):
    st.session_state["pe_range"] = st.session_state["standard_pe_range"]
    st.session_state["peg_range"] = st.session_state["standard_peg_range"]
    st.session_state["eps_growth_min"] = st.session_state["standard_eps_growth_min"]
    st.session_state["market_cap_min"] = st.session_state["standard_market_cap_min"]

if col_edit.button("✏️ Change standard filters"):
    st.session_state["show_filter_popup"] = True

# -------------------------------
# Filter Popup
# -------------------------------
if st.session_state["show_filter_popup"]:
    with st.container():
        st.markdown("### ✏️ Edit Standard Filters")
        new_pe = st.slider("P/E Ratio", 0.0, 50.0, st.session_state["standard_pe_range"], key="edit_pe")
        new_peg = st.slider("PEG Ratio", 0.0, 5.0, st.session_state["standard_peg_range"], key="edit_peg")
        new_eps = st.slider("Min EPS Growth %", 0.0, 100.0, st.session_state["standard_eps_growth_min"], key="edit_eps")
        new_mcap = st.number_input("Min Market Cap ($)", value=st.session_state["standard_market_cap_min"], key="edit_mcap")

        if st.button("Apply"):
            st.session_state["standard_pe_range"] = new_pe
            st.session_state["standard_peg_range"] = new_peg
            st.session_state["standard_eps_growth_min"] = new_eps
            st.session_state["standard_market_cap_min"] = new_mcap

            st.session_state["pe_range"] = new_pe
            st.session_state["peg_range"] = new_peg
            st.session_state["eps_growth_min"] = new_eps
            st.session_state["market_cap_min"] = new_mcap

            st.session_state["show_filter_popup"] = False

# -------------------------------
# Live Filters
# -------------------------------
st.session_state.setdefault("pe_range", (0.0, 50.0))
st.session_state.setdefault("peg_range", (0.0, 5.0))
st.session_state.setdefault("eps_growth_min", 0.0)
st.session_state.setdefault("market_cap_min", 0)

filtered_df = df[
    (df["pe"].between(*st.session_state["pe_range"])) &
    (df["peg"].between(*st.session_state["peg_range"])) &
    (df["eps_growth"] >= st.session_state["eps_growth_min"]) &
    (df["market_cap"] >= st.session_state["market_cap_min"])
]
filtered_df = filtered_df[~filtered_df["ticker"].isin(st.session_state.hidden_tickers)]

# -------------------------------
# Table Controls
# -------------------------------
if st.session_state.show_restore_alert:
    col_alert, col_dismiss = st.columns([10, 1])
    with col_alert:
        st.success("All rows restored")
    with col_dismiss:
        if st.button("✖", key="dismiss_alert"):
            st.session_state.show_restore_alert = False

if st.button("👁 Show All Hidden Rows"):
    st.session_state.hidden_tickers.clear()
    st.session_state.show_restore_alert = True

# -------------------------------
# Table Display
# -------------------------------
st.markdown("### 📈 Filtered Stock List")

header_cols = st.columns([2, 2, 1, 1, 2, 1, 1])
sort_keys = ["ticker", "price", "pe", "peg", "eps_growth"]
labels = ["Stock", "Last Price", "PE", "PEG", "EPS Growth"]

for i, (label, key) in enumerate(zip(labels, sort_keys)):
    if header_cols[i].button(label, key=f"sort_{key}"):
        if st.session_state.sort_by == key:
            st.session_state.sort_ascending = not st.session_state.sort_ascending
        else:
            st.session_state.sort_by = key
            st.session_state.sort_ascending = True

filtered_df = filtered_df.sort_values(by=st.session_state.sort_by, ascending=st.session_state.sort_ascending)

for _, row in filtered_df.iterrows():
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 1, 1, 2, 1, 1])
    ticker = row["ticker"]
    link = f"https://finance.yahoo.com/quote/{ticker}"

    col1.markdown(f"[{ticker}]({link})")
    col2.write(f"${row['price']:.2f}")
    col3.write(f"{row['pe']:.1f}")
    col4.write(f"{row['peg']:.1f}")
    col5.write(f"{row['eps_growth']:.1f}%")

    if col6.button("👁‍🗨", key=f"hide_{ticker}"):
        st.session_state.hidden_tickers.add(ticker)

    if col7.button("➕", key=f"add_{ticker}"):
        st.success(f"{ticker} added to simulation (dummy)")

st.caption("📎 Showing dummy data. Live EODHD integration coming soon.")
