import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Harbourne Terminal")

# --- Load data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Sorting ---
sort_column = st.selectbox("Sort by column", df.columns.tolist(), index=0)
df = df.sort_values(by=sort_column)

# --- Page and table styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
html, body, .stApp, .block-container {
    font-family: 'Lato', sans-serif;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
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
</style>
""", unsafe_allow_html=True)

# --- Title & meta info ---
st.title("Harbourne Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- Table Rendering ---
headers = ''.join(f"<th>{col}</th>" for col in df.columns)
rows = ""
for _, row in df.iterrows():
    row_html = ''.join(f"<td>{row[col]}</td>" for col in df.columns)
    rows += f"<tr>{row_html}</tr>"

table_html = f"""
<table class="custom-table">
    <thead><tr>{headers}</tr></thead>
    <tbody>{rows}</tbody>
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)
