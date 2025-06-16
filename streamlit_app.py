
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

# Sidebar styling
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
.sidebar-section {
    margin-bottom: 10px;
}
.sidebar-label {
    font-size: 13px;
    color: #f1f5f9 !important;
    margin-bottom: 4px;
    border-bottom: 0.5px solid #070b15;
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

# Sidebar content
with st.sidebar:
    with st.expander("Filter Stocks", expanded=True):
        st.markdown('<div class="sidebar-label">Price</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">PEG</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">PE</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)
    
        st.markdown('<div class="sidebar-label">EPS Growth</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Analyst Rating</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Target Upside</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Market Cap</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">30-Day Volume</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-row"><input type="number" placeholder="Min"/><input type="number" placeholder="Max"/></div>', unsafe_allow_html=True)    
            
    st.divider()
           
    st.toggle("US Only")
    st.toggle("Nasdaq Only")
    st.toggle("NYSE Only")
    
    st.divider()
    
    with st.expander("Smart Score Weights", expanded=False):
        st.slider("PEG", 0, 100, 50)
        st.slider("EPS Growth", 0, 100, 50)
        st.slider("Analyst Rating", 0, 100, 50)
        st.slider("Target Upside", 0, 100, 50)
        st.slider("Sentiment", 0, 100, 50)
        st.slider("Insider Depth", 0, 100, 50)

    st.divider()
    st.markdown("Charts")
    st.markdown("Research")
    st.markdown("Misc")
    st.markdown("Information Hub")

# Main area
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# Table rendering
header_html = ''.join(f"<th>{col}</th>" for col in df.columns)
row_html = ""
for _, row in df.iterrows():
    row_cells = ""
    for col in df.columns:
        val = row[col]
        if col == "Ticker":
            link = f"https://finance.yahoo.com/quote/{val}"
            val = f"<a class='ticker-link' href='{link}' target='_blank'>{val}</a>"
        row_cells += f"<td>{val}</td>"
    row_html += f"<tr>{row_cells}</tr>"

st.markdown(f"""
<table class="custom-table">
    <thead><tr>{header_html}</tr></thead>
    <tbody>{row_html}</tbody>
</table>
""", unsafe_allow_html=True)
