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

# Initialize session state
if "hidden_tickers" not in st.session_state:
    st.session_state.hidden_tickers = set()

# Filters
st.title("📊 Stock Screener")

with st.expander("🔍 Filter Settings"):
    pe_range = st.slider("P/E Ratio", 0.0, 50.0, (0.0, 50.0))
    peg_range = st.slider("PEG Ratio", 0.0, 5.0, (0.0, 5.0))
    eps_growth_min = st.slider("Min EPS Growth %", 0.0, 100.0, 0.0)
    market_cap_min = st.number_input("Min Market Cap ($)", value=300_000_000)

# Apply filters
filtered_df = df[
    (df["pe"].between(*pe_range)) &
    (df["peg"].between(*peg_range)) &
    (df["eps_growth"] >= eps_growth_min) &
    (df["market_cap"] >= market_cap_min)
]

# Hide filtered-out tickers
filtered_df = filtered_df[~filtered_df["ticker"].isin(st.session_state.hidden_tickers)]

# Global reset button
if st.button("👁 Show All Hidden Rows"):
    st.session_state.hidden_tickers.clear()
    st.success("All rows restored")

# Display the table
st.markdown("### 📈 Filtered Stock List")
for _, row in filtered_df.iterrows():
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 1, 1, 2, 1, 1])
    ticker = row["ticker"]
    link = f"https://finance.yahoo.com/quote/{ticker}"

    col1.markdown(f"[{ticker}]({link})")
    col2.write(f"${row['price']:.2f}")
    col3.write(f"PE: {row['pe']:.1f}")
    col4.write(f"PEG: {row['peg']:.1f}")
    col5.write(f"EPS Growth: {row['eps_growth']:.1f}%")
    if col6.button("👁‍🗨", key=f"hide_{ticker}"):
        st.session_state.hidden_tickers.add(ticker)
        st.experimental_rerun()
    if col7.button("➕", key=f"add_{ticker}"):
        st.success(f"{ticker} added to simulation (dummy)")

# Note about dummy data
st.caption("Showing dummy data. Live data integration coming soon via EODHD fundamentals CSV.")
