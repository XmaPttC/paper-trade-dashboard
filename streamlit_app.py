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

# --- Global Style ---
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
}
.custom-table tr:nth-child(even) {
    background-color: #3d5975;
}
.custom-table tr:nth-child(odd) {
    background-color: #466686;
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
.signal-card {
    background-color: #263041;
    padding: 12px;
    border: 1px solid #334155;
    border-radius: 6px;
    margin-bottom: 10px;
}
.signal-card h4 {
    margin-top: 0;
    font-size: 15px;
    color: #f1f5f9;
}
</style>
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

tab1, tab2 = st.tabs(["Terminal", "Control Panel"])

with tab1:
    st.title("Terminal")
    st.markdown(f"""
    <div style='display: flex; gap: 20px; margin-bottom: 4px;'>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
    </div>
    <hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
    """, unsafe_allow_html=True)

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

    st.markdown(f"<table class='custom-table'><thead><tr>{header_html}</tr></thead><tbody>{row_html}</tbody></table>", unsafe_allow_html=True)

with tab2:
    st.title("Alt-Data Control Panel")
    st.markdown("Use the toggles and sliders below to adjust alternative data signal settings for scoring.")

    # --- Styling for Cards ---
    st.markdown("""
    <style>
    .signal-card-container {
        border: 1px solid #475569;
        background-color: #2a3b4d;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .signal-card-title {
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 6px;
        color: #f1f5f9;
    }
    .signal-card-container input, .signal-card-container .stSlider {
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Render Card Helper ---
    def render_signal_card(col, title, key_prefix, default_enabled, default_thresh, range_thresh, default_weight):
        with col:
            with st.container():
                st.markdown(f"<div class='signal-card-container'>", unsafe_allow_html=True)
                st.markdown(f"<div class='signal-card-title'>{title}</div>", unsafe_allow_html=True)
                st.checkbox("Enable", value=default_enabled, key=f"{key_prefix}_toggle")
                st.number_input("Threshold", range_thresh[0], range_thresh[1], default_thresh, key=f"{key_prefix}_thresh")
                st.slider("Weight", 0.0, 1.0, default_weight, 0.01, key=f"{key_prefix}_weight")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- Row 1 ---
    col1, col2, col3 = st.columns(3)
    render_signal_card(col1, "Options Flow", "options", True, 10.0, (0.0, 100.0), 0.2)
    render_signal_card(col2, "Dark Pool Activity", "darkpool", True, 5.0, (0.0, 100.0), 0.2)
    render_signal_card(col3, "GEX Exposure", "gex", True, 1.5, (0.0, 5.0), 0.1)

    # --- Row 2 ---
    col4, col5, col6 = st.columns(3)
    render_signal_card(col4, "Reddit Sentiment", "reddit", True, 10.0, (0.0, 100.0), 0.15)
    render_signal_card(col5, "News Sentiment", "sent", True, 20.0, (0.0, 100.0), 0.15)
    render_signal_card(col6, "Insider Buying", "insider", True, 5.0, (0.0, 100.0), 0.2)

    st.divider()
    if st.button("✅ Apply Settings"):
        st.success("Alt-data settings saved.")
