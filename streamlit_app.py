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

# --- CSS Styling ---
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
    width: 340px !important;
}
.sidebar-label {
    font-size: 13px;
    color: #f1f5f9 !important;
    margin-bottom: 4px;
    border-bottom: 0.5px solid #262a32;
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
</style>
""", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2 = st.tabs(["ð Terminal Dashboard", "ð§  Alt-Data Control Panel"])

# --- Terminal Dashboard ---
with tab1:
    st.title("Terminal Dashboard")
    st.markdown(f"""
    <div style='display: flex; gap: 20px; margin-bottom: 4px;'>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
    </div>
    <hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
    """, unsafe_allow_html=True)

    def format_mktcap(val):
        if val >= 1e12:
            return f"{val/1e12:.2f}<span class='suffix-T'>T</span>"
        elif val >= 1e9:
            return f"{val/1e9:.2f}<span class='suffix-B'>B</span>"
        else:
            return f"{val/1e6:.2f}<span class='suffix-M'>M</span>"

    def format_volume(val):
        return f"{val/1e6:.2f}M"

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

# --- Alt-Data Control Panel ---
with tab2:
    st.title("ð§  Alt-Data Control Panel")

    if "altdata_settings" not in st.session_state:
        st.session_state.altdata_settings = {}

    def render_signal_card(title, key_prefix, default_weight):
        if key_prefix not in st.session_state.altdata_settings:
            st.session_state.altdata_settings[key_prefix] = {
                "enabled": True,
                "weight": default_weight
            }
        with st.expander(f"{title}", expanded=True):
            enabled = st.checkbox("Enable", value=st.session_state.altdata_settings[key_prefix]["enabled"], key=f"{key_prefix}_toggle")
            weight = st.slider("Weight", 0.0, 1.0, float(st.session_state.altdata_settings[key_prefix]["weight"]), 0.01, key=f"{key_prefix}_weight")
            st.session_state.altdata_settings[key_prefix] = {
                "enabled": enabled,
                "weight": weight
            }

    st.markdown("### Tune Weights and Enable Signals")
    render_signal_card("ð° Options Flow", "options", 0.2)
    render_signal_card("ð¦ Dark Pool Activity", "darkpool", 0.15)
    render_signal_card("ð Gamma Exposure (GEX)", "gex", 0.1)
    render_signal_card("ð¬ Sentiment Score", "sentiment", 0.2)
    render_signal_card("ð§µ Reddit Buzz", "reddit", 0.15)

    st.divider()
    if st.button("â Apply Alt-Data Settings"):
        st.success("Alt-data signal settings saved.")
