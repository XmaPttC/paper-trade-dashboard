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

# Shared Styling
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

    st.markdown("""
    <style>
    .signal-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }
    .signal-card {
        background-color: #263142;
        border: 1px solid #3b4454;
        border-radius: 4px;
        padding: 10px 12px;
        font-size: 12px;
    }
    .signal-card h4 {
        font-size: 13px;
        margin: 0 0 6px 0;
        color: #f8fafc;
    }
    .signal-card label {
        font-size: 11px !important;
        margin-bottom: 2px !important;
    }
    .signal-card .stSlider,
    .signal-card .stNumberInput,
    .signal-card .stCheckbox {
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("Use the controls below to configure which alt-data signals are enabled and how much weight they carry.")

    def render_signal_card(title, key_prefix, default_enabled, default_thresh, range_thresh, default_weight):
        with st.container():
            st.markdown("<div class='signal-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
            st.checkbox("Enable", value=default_enabled, key=f"{key_prefix}_toggle")
            st.number_input("Threshold", range_thresh[0], range_thresh[1], default_thresh, key=f"{key_prefix}_thresh")
            st.slider("Weight", 0.0, 1.0, default_weight, 0.01, key=f"{key_prefix}_weight")
            st.markdown("</div>", unsafe_allow_html=True)

    # Render the grid manually
    st.markdown('<div class="signal-grid">', unsafe_allow_html=True)
    render_signal_card("📊 Options Flow", "options", True, 10.0, (0.0, 100.0), 0.2)
    render_signal_card("🔒 Dark Pool Activity", "darkpool", True, 5.0, (0.0, 100.0), 0.2)
    render_signal_card("⚛️ GEX Exposure", "gex", True, 1.5, (0.0, 5.0), 0.1)
    render_signal_card("📢 Reddit Sentiment", "reddit", True, 10.0, (0.0, 100.0), 0.15)
    render_signal_card("📰 News Sentiment", "sent", True, 20.0, (0.0, 100.0), 0.15)
    render_signal_card("🧑‍💼 Insider Buying", "insider", True, 5.0, (0.0, 100.0), 0.2)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("✅ Apply Settings"):
        st.success("Alt-data settings saved.")
