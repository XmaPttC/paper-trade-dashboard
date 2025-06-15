import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Terminal")

# --- Page + sidebar styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
html, body, .stApp, .block-container {
    font-family: 'Lato', sans-serif;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
}
section[data-testid="stSidebar"] {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    width: 220px !important;
}
section[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.custom-table th, .custom-table td {
    padding: 6px 8px;
    text-align: left;
}
.custom-table th {
    background-color: #1e293b;
    color: #f1f5f9;
}
.custom-table tr:nth-child(even) {
    background-color: #466686;
}
.custom-table tr:nth-child(odd) {
    background-color: #3d5975;
}
.custom-table tr:hover {
    background-color: #64748b !important;
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

# --- Load data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Title and meta ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- Define column order ---
ordered_cols = [
    "Ticker", "Price", "SmartScore", "PEG", "PE", "EPSGrowth", "MarketCap", "30DayVol",
    "AnalystRating", "TargetUpside", "Sector", "InsiderDepth", "SentimentScore",
    "RedditSentiment", "HiLoProximity"
]
df = df[ordered_cols]

# --- Generate HTML table ---
rows_html = ""
for _, row in df.iterrows():
    link = f"https://finance.yahoo.com/quote/{row['Ticker']}"
    rows_html += f"""
    <tr>
        <td><a class="ticker-link" href="{link}" target="_blank">{row['Ticker']}</a></td>
        <td>${row['Price']}</td>
        <td>{row['SmartScore']}</td>
        <td>{row['PEG']}</td>
        <td>{row['PE']}</td>
        <td>{row['EPSGrowth']}%</td>
        <td>{row['MarketCap']}</td>
        <td>{row['30DayVol']}</td>
        <td>{row['AnalystRating']}</td>
        <td>{row['TargetUpside']}%</td>
        <td>{row['Sector']}</td>
        <td>{row['InsiderDepth']}</td>
        <td>{row['SentimentScore']}</td>
        <td>{row['RedditSentiment']}</td>
        <td>{row['HiLoProximity']}%</td>
    </tr>
    """

table_html = f"""
<table class="custom-table">
    <thead>
        <tr>
            <th>Ticker</th><th>Price</th><th>SmartScore</th><th>PEG</th><th>PE</th>
            <th>EPSGrowth</th><th>MarketCap</th><th>30DayVol</th><th>AnalystRating</th>
            <th>TargetUpside</th><th>Sector</th><th>InsiderDepth</th>
            <th>SentimentScore</th><th>RedditSentiment</th><th>HiLoProximity</th>
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>
"""

st.markdown(table_html, unsafe_allow_html=True)
