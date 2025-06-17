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

# --- Sidebar Styling ---
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
    padding: 8px;
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
.suffix-M { color: #c084fc; font-weight: bold; }
.suffix-B { color: #86efac; font-weight: bold; }
.suffix-T { color: #f87171; font-weight: bold; }

[data-baseweb="base-input"]{
background-color: #1e293b !important;
border: 1px solid #475569 !important;
border-radius: 1px !important;
}

input[class]{
font-size:14px;
color: #f1f5f9;
border: 1px solid #475569 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    def filter_input(label, min_default=0, max_default=10000000):
        st.markdown(f'<div class="sidebar-label">{label}</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            min_val = st.number_input(f"{label}_min", label_visibility="collapsed", value=min_default, key=f"{label}_min")
        with col2:
            max_val = st.number_input(f"{label}_max", label_visibility="collapsed", value=max_default, key=f"{label}_max")
        return min_val, max_val

    with st.expander("Filter Stocks", expanded=True):
        price_min, price_max = filter_input("Price", 0, 2000)
        peg_min, peg_max = filter_input("PEG", 0.0, 5.0)
        pe_min, pe_max = filter_input("PE", 0.0, 50.0)
        eps_min, eps_max = filter_input("EPSGr", 0, 100)
        rating_min, rating_max = filter_input("AnalystSc", 1.0, 5.0)
        upside_min, upside_max = filter_input("TrgtUpside", 0, 200)
        mcap_min, mcap_max = filter_input("MktCap", 0, 10_000_000_000_000)
        vol_min, vol_max = filter_input("30DayVol", 0, 1_000_000_000)

    st.divider()
    st.toggle("US Only")
    st.toggle("Nasdaq Only")
    st.toggle("NYSE Only")
    st.divider()

    with st.expander("Smart Score Weights", expanded=False):
        peg_w = st.slider("PEG", 0, 100, 20)
        eps_w = st.slider("EPS Growth", 0, 100, 15)
        rating_w = st.slider("Analyst Rating", 0, 100, 20)
        upside_w = st.slider("Target Upside", 0, 100, 15)
        sentiment_w = st.slider("Sentiment", 0, 100, 15)
        insider_w = st.slider("Insider Depth", 0, 100, 15)

    st.divider()
    st.markdown("Charts")
    st.markdown("Research")
    st.markdown("Misc")
    st.markdown("Information Hub")

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

# --- SmartScore Calculation ---
total_weight = sum([peg_w, eps_w, rating_w, upside_w, sentiment_w, insider_w]) or 1
weights = {
    "PEG": peg_w / total_weight,
    "EPSGr": eps_w / total_weight,
    "AnalystSc": rating_w / total_weight,
    "TrgtUpside": upside_w / total_weight,
    "SentSc": sentiment_w / total_weight,
    "InsiderSc": insider_w / total_weight
}
df["TerminalScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * weights["PEG"] +
    df["EPSGr"] * weights["EPSGr"] +
    (5 - df["AnalystSc"]) * weights["AnalystSc"] +
    df["TrgtUpside"] * weights["TrgtUpside"] +
    df["SentSc"] * weights["SentSc"] +
    df["InsiderSc"] * weights["InsiderSc"]
).round(2)

# --- Display Header ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- Format Helpers ---
def format_mktcap(val):
    if val >= 1e12:
        return f"{val/1e12:.2f}<span class='suffix-T'>T</span>"
    elif val >= 1e9:
        return f"{val/1e9:.2f}<span class='suffix-B'>B</span>"
    else:
        return f"{val/1e6:.2f}<span class='suffix-M'>M</span>"

def format_volume(val):
    return f"{val/1e6:.2f}M"

# --- Render HTML Table ---
header_html = ''.join(f"<th>{col}</th>" for col in df.columns)
row_html = ""
for _, row in df.iterrows():
    row_cells = ""
    for col in df.columns:
        val = row[col]
        if col == "Ticker":
            val = f"<a class='ticker-link' href='https://finance.yahoo.com/quote/{val}' target='_blank'>{val}</a>"
        elif col == "MktCap":
            val = format_mktcap(val)
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
