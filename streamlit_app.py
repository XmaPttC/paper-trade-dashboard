import streamlit as st
import pandas as pd

# ----------------------------
# Dummy Data Setup
# ----------------------------
data = [
    {"ticker": "AAPL", "price": 185.2, "pe": 29.8, "peg": 2.1, "eps_growth": 18.5, "market_cap": 2800000000000},
    {"ticker": "GOOGL", "price": 128.3, "pe": 26.4, "peg": 1.8, "eps_growth": 20.2, "market_cap": 1800000000000},
    {"ticker": "SMCI", "price": 900.5, "pe": 32.7, "peg": 0.9, "eps_growth": 75.0, "market_cap": 45000000000},
    {"ticker": "TSLA", "price": 180.7, "pe": 45.1, "peg": 2.9, "eps_growth": 25.3, "market_cap": 700000000000},
]
df = pd.DataFrame(data)

# ----------------------------
# Session State Defaults
# ----------------------------
st.session_state.setdefault("hidden_tickers", set())
st.session_state.setdefault("sort_by", "ticker")
st.session_state.setdefault("sort_ascending", True)
st.session_state.setdefault("show_restore_alert", False)
st.session_state.setdefault("show_filter_popup", False)

# Default standard filters (editable by user)
default_filters = {
    "pe": (0.0, 15.0),
    "peg": (0.0, 1.0),
    "eps_growth": 20.0,
    "market_cap": 300_000_000
}
st.session_state.setdefault("standard_filters", default_filters.copy())

# ----------------------------
# Title & Layout
# ----------------------------
st.title("📊 Stock Screener")

# ----------------------------
# Filter Section
# ----------------------------
st.subheader("🎛️ Filters")

# Apply standard filters button
col_std_btn, col_std_link = st.columns([2, 3])
if col_std_btn.button("Apply Standard Filters"):
    filters = st.session_state["standard_filters"]
    st.session_state["pe_range"] = filters["pe"]
    st.session_state["peg_range"] = filters["peg"]
    st.session_state["eps_growth_min"] = filters["eps_growth"]
    st.session_state["market_cap_min"] = filters["market_cap"]

# Change standard filters link
if col_std_link.button("Change standard filters"):
    st.session_state["show_filter_popup"] = True

# Filter popup modal
if st.session_state["show_filter_popup"]:
    with st.expander("🔧 Edit Standard Filters", expanded=True):
        pe = st.slider("Standard PE Range", 0.0, 50.0, st.session_state["standard_filters"]["pe"], key="std_pe")
        peg = st.slider("Standard PEG Range", 0.0, 5.0, st.session_state["standard_filters"]["peg"], key="std_peg")
        eps = st.slider("Standard Min EPS Growth %", 0.0, 100.0, st.session_state["standard_filters"]["eps_growth"], key="std_eps")
        mc = st.number_input("Standard Min Market Cap ($)", value=st.session_state["standard_filters"]["market_cap"], key="std_mc")

        if st.button("💾 Save Filters"):
            st.session_state["standard_filters"] = {
                "pe": pe,
                "peg": peg,
                "eps_growth": eps,
                "market_cap": mc
            }
            st.success("Saved!")
            st.session_state["show_filter_popup"] = False

# Live filter inputs
pe_range = st.slider("P/E Ratio", 0.0, 50.0, st.session_state.get("pe_range", (0.0, 50.0)))
peg_range = st.slider("PEG Ratio", 0.0, 5.0, st.session_state.get("peg_range", (0.0, 5.0)))
eps_growth_min = st.slider("Min EPS Growth %", 0.0, 100.0, st.session_state.get("eps_growth_min", 0.0))
market_cap_min = st.number_input("Min Market Cap ($)", value=st.session_state.get("market_cap_min", 0))

# ----------------------------
# Apply Filters
# ----------------------------
filtered_df = df[
    (df["pe"].between(*pe_range)) &
    (df["peg"].between(*peg_range)) &
    (df["eps_growth"] >= eps_growth_min) &
    (df["market_cap"] >= market_cap_min)
]
filtered_df = filtered_df[~filtered_df["ticker"].isin(st.session_state.hidden_tickers)]

# ----------------------------
# Restore Panel
# ----------------------------
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

# ----------------------------
# Sortable Table Header
# ----------------------------
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

# ----------------------------
# Display Table Rows
# ----------------------------
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
