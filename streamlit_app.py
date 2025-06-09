import streamlit as st
import pandas as pd

# Dummy data
data = [
    {"ticker": "AAPL", "price": 185.2, "pe": 29.8, "peg": 2.1, "eps_growth": 18.5, "market_cap": 2800000000000},
    {"ticker": "GOOGL", "price": 128.3, "pe": 26.4, "peg": 1.8, "eps_growth": 20.2, "market_cap": 1800000000000},
    {"ticker": "SMCI", "price": 900.5, "pe": 32.7, "peg": 0.9, "eps_growth": 75.0, "market_cap": 45000000000},
    {"ticker": "TSLA", "price": 180.7, "pe": 45.1, "peg": 2.9, "eps_growth": 25.3, "market_cap": 700000000000},
]
df = pd.DataFrame(data)

# Session state
if "hidden_tickers" not in st.session_state:
    st.session_state.hidden_tickers = set()
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "ticker"
if "sort_ascending" not in st.session_state:
    st.session_state.sort_ascending = True
if "show_restore_alert" not in st.session_state:
    st.session_state.show_restore_alert = False

# Header
st.title("📊 Stock Screener")

# Filters
with st.expander("🔍 Filter Settings"):
    pe_range = st.slider("P/E Ratio", 0.0, 50.0, (0.0, 50.0))
    peg_range = st.slider("PEG Ratio", 0.0, 5.0, (0.0, 5.0))
    eps_growth_min = st.slider("Min EPS Growth %", 0.0, 100.0, 0.0)
    market_cap_min = st.number_input("Min Market Cap ($)", value=300_000_000)

# Filtered data
filtered_df = df[
    (df["pe"].between(*pe_range)) &
    (df["peg"].between(*peg_range)) &
    (df["eps_growth"] >= eps_growth_min) &
    (df["market_cap"] >= market_cap_min)
]
filtered_df = filtered_df[~filtered_df["ticker"].isin(st.session_state.hidden_tickers)]

# Show alert
if st.session_state.show_restore_alert:
    with st.container():
        col_alert, col_dismiss = st.columns([10, 1])
        col_alert.success("All rows restored")
        if col_dismiss.button("✖", key="dismiss_alert"):
            st.session_state.show_restore_alert = False
            st.experimental_rerun()

# Restore button
if st.button("👁 Show All Hidden Rows"):
    st.session_state.hidden_tickers.clear()
    st.session_state.show_restore_alert = True
    st.experimental_rerun()

# Column sorting UI
st.markdown("### 📈 Filtered Stock List")

columns = {
    "ticker": "Stock",
    "price": "Last Price",
    "pe": "PE",
    "peg": "PEG",
    "eps_growth": "EPS Growth"
}

header_cols = st.columns([2, 2, 1, 1, 2, 1, 1])

for i, (col_key, col_label) in enumerate(columns.items()):
    arrow = "⬇️" if (st.session_state.sort_by == col_key and st.session_state.sort_ascending) else "⬆️"
    if header_cols[i].button(f"{col_label} {arrow}", key=f"sort_{col_key}"):
        if st.session_state.sort_by == col_key:
            st.session_state.sort_ascending = not st.session_state.sort_ascending
        else:
            st.session_state.sort_by = col_key
            st.session_state.sort_ascending = True
        st.experimental_rerun()

# Sort data
filtered_df = filtered_df.sort_values(by=st.session_state.sort_by, ascending=st.session_state.sort_ascending)

# Display rows
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
        st.experimental_rerun()

    if col7.button("➕", key=f"add_{ticker}"):
        st.success(f"{ticker} added to simulation (dummy)")

# Footer
st.caption("📎 Showing dummy data. Live integration from EODHD fundamentals CSV coming soon.")
