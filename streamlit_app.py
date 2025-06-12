import streamlit as st
import pandas as pd

# Dummy stock data
data = {
    "Ticker": ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA"],
    "Last Price": [190.25, 2750.65, 3450.30, 305.15, 850.50],
    "PE": [28.3, 30.2, 60.5, 35.0, 70.8],
    "PEG": [1.9, 1.5, 2.0, 1.7, 2.5],
    "EPS": [5.11, 90.25, 57.33, 8.69, 12.56],
    "Market Cap": [2.7e12, 1.8e12, 1.6e12, 2.3e12, 0.85e12]
}
df = pd.DataFrame(data)

# Format Market Cap
def format_market_cap(val):
    return f"{val/1e9:.2f}B" if val >= 1e9 else f"{val/1e6:.2f}M"

df["Market Cap"] = df["Market Cap"].apply(format_market_cap)

# Session state for hidden rows
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()

# Page styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        font-family: "Segoe UI", sans-serif;
        color: #212529;
    }
    .dataframe th {
        background-color: #dee2e6;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Stock Screener Dashboard")

# Filter visible rows
visible_df = df[~df.index.isin(st.session_state.hidden_rows)]

# Table headers
cols = st.columns([1.5, 1.5, 1, 1, 1.5, 2, 0.5, 0.5])
headers = ["Ticker", "Last Price", "PE", "PEG", "EPS", "Market Cap", "", ""]
for col, header in zip(cols, headers):
    col.markdown(f"**{header}**")

# Display rows
for idx, row in visible_df.iterrows():
    cols = st.columns([1.5, 1.5, 1, 1, 1.5, 2, 0.5, 0.5])
    link = f"https://finance.yahoo.com/quote/{row['Ticker']}"
    cols[0].markdown(f"[{row['Ticker']}]({link})")
    cols[1].write(f"${row['Last Price']:.2f}")
    cols[2].write(row["PE"])
    cols[3].write(row["PEG"])
    cols[4].write(row["EPS"])
    cols[5].write(row["Market Cap"])

    if cols[6].button("👁️", key=f"hide_{idx}") and idx not in st.session_state.hidden_rows:
        st.session_state.hidden_rows.add(idx)
        st.success(f"{row['Ticker']} hidden — adjust filters to refresh list.")

    if cols[7].button("➕", key=f"add_{idx}"):
        st.success(f"{row['Ticker']} added to trading simulation.")

# Restore all rows
if st.button("🔄 Show All Hidden Rows"):
    st.session_state.hidden_rows.clear()
    st.success("All hidden rows restored. Adjust filters to refresh list.")
