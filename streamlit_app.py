import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Terminal")

# Load data
df = pd.read_csv("mock_stock_data.csv")

# Define column order
column_order = [
    "Ticker", "Price", "TerminalScore", "PEG", "PE", "EPSGr", "MktCap",
    "30DayVol", "AnalystSc", "TrgtUpside", "Sector", "InsiderSc",
    "SentSc", "RedditSc", "52wH"
]
df = df[[col for col in column_order if col in df.columns]]

# --- Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
html, body, .stApp, .block-container {
    font-family: 'Lato', sans-serif;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
}
section[data-testid="stSidebar"] {
    background-color: #070b15 !important;
    color: #f1f5f9 !important;
    font-size: 13px;
    padding: 8px 8px 8px 8px;
    width: 240px !important;
}
.sidebar-label {
    font-size: 13px;
    color: #f1f5f9 !important;
    margin-bottom: 4px;
    border-bottom: 0.5px solid #262a32;
}
.filter-row {
    display: flex;
    justify-content: space-between;
    gap: 6px;
    margin-bottom: 10px;
}
.filter-row input {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 2px;
    padding: 4px;
    width: 100%;
    font-size: 12px;
}
input:focus {
    outline: none;
    border: 1px solid #38bdf8;
}
.custom-table {
    background-color: #1e293b;
    color: #f1f5f9;
    border-collapse: collapse;
    font-size: 13px;
    width: 100%;
}
.custom-table th, .custom-table td {
    border: 1px solid #334155;
    padding: 6px 10px;
    text-align: left;
}
.custom-table th {
    background-color: #334155;
    cursor: pointer;
}
.custom-table tr:nth-child(even) {
    background-color: #3d5975;
}
.custom-table tr:nth-child(odd) {
    background-color: #466686;
}
.custom-table tr:hover {
    background-color: #64748b;
}
a.ticker-link {
    color: #93c5fd;
    text-decoration: none;
}
a.ticker-link:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    with st.expander("📊 Filter Stocks", expanded=True):
        def dual_input(label, colname):
            min_val = float(df[colname].min())
            max_val = float(df[colname].max())
            st.markdown(f'<div class="sidebar-label">{label}</div>', unsafe_allow_html=True)
            return st.columns([1,1])[0].number_input(f"{label} Min", value=min_val, key=f"{colname}_min"), \
                   st.columns([1,1])[1].number_input(f"{label} Max", value=max_val, key=f"{colname}_max")

        price_min, price_max = dual_input("Price", "Price")
        peg_min, peg_max = dual_input("PEG", "PEG")
        pe_min, pe_max = dual_input("PE", "PE")
        eps_min, eps_max = dual_input("EPS Growth", "EPSGr")
        rating_min, rating_max = dual_input("Analyst Rating", "AnalystSc")
        upside_min, upside_max = dual_input("Target Upside", "TrgtUpside")
        mcap_min, mcap_max = dual_input("Market Cap", "MktCap")
        vol_min, vol_max = dual_input("30-Day Volume", "30DayVol")

    st.toggle("🇺🇸 US Only")
    st.toggle("🟣 Nasdaq Only")
    st.toggle("🟠 NYSE Only")

# --- Apply Filters ---
df = df[
    (df["Price"].between(price_min, price_max)) &
    (df["PEG"].between(peg_min, peg_max)) &
    (df["PE"].between(pe_min, pe_max)) &
    (df["EPSGr"].between(eps_min, eps_max)) &
    (df["AnalystSc"].between(rating_min, rating_max)) &
    (df["TrgtUpside"].between(upside_min, upside_max)) &
    (df["MktCap"].between(mcap_min, mcap_max)) &
    (df["30DayVol"].between(vol_min, vol_max))
]

# --- Table Title and Meta ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- Format market cap and volume ---
def format_mcap(val):
    if val >= 1e12: return f"{val/1e12:.1f}<span style='color:#f87171;'>T</span>"
    elif val >= 1e9: return f"{val/1e9:.1f}<span style='color:#4ade80;'>B</span>"
    elif val >= 1e6: return f"{val/1e6:.1f}<span style='color:#a78bfa;'>M</span>"
    else: return f"{val:.0f}"

def format_volume(val):
    return f"{val/1e6:.1f}M"

# --- Render table ---
header_html = ''.join(f"<th>{col}</th>" for col in df.columns)
row_html = ""
for _, row in df.iterrows():
    row_cells = ""
    for col in df.columns:
        val = row[col]
        if col == "Ticker":
            val = f"<a class='ticker-link' href='https://finance.yahoo.com/quote/{val}' target='_blank'>{val}</a>"
        elif col == "MktCap":
            val = format_mcap(val)
        elif col == "30DayVol":
            val = format_volume(val)
        elif col == "TrgtUpside":
            val = f"{val:.1f}%"
        row_cells += f"<td>{val}</td>"
    row_html += f"<tr>{row_cells}</tr>"

st.markdown(f"""
<table class="custom-table">
    <thead><tr>{header_html}</tr></thead>
    <tbody>{row_html}</tbody>
</table>
""", unsafe_allow_html=True)
