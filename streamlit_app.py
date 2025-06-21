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
</style>
""", unsafe_allow_html=True)

# --- Tabbed Layout ---
tab1, tab2 = st.tabs(["ð Terminal", "ð§ª Alt-Data Control Panel"])

with tab1:
    st.title("Terminal Dashboard")
    st.info("â Use the sidebar to filter and score stocks.")

    # Filter sliders & inputs would go here...
    # (Truncated for brevity â reuse your current filters and scoring logic)

    st.markdown("### Results Table Goes Here")
    st.markdown("Mock HTML table output or AG Grid.")

with tab2:

    st.title("Alt-Data Control Panel")

    st.markdown("Use the sliders and toggles below to tune the signal thresholds and weights for each alt-data input. Settings will be saved when you click **Apply Settings**.")

    # --- Helper Function to Render Signal Cards ---
    def render_signal_card(col, title, key_prefix, default_enabled, default_thresh, range_thresh, default_weight):
        with col:
            st.markdown(f"#### {title}")
            if "altdata_settings" not in st.session_state:
                st.session_state.altdata_settings = {}
            if key_prefix not in st.session_state.altdata_settings:
                st.session_state.altdata_settings[key_prefix] = {
                    "enabled": default_enabled,
                    "threshold": default_thresh,
                    "weight": default_weight
                }
            enabled = st.checkbox("Enable", value=st.session_state.altdata_settings[key_prefix]["enabled"], key=f"{key_prefix}_toggle_{key_prefix}")
            threshold = st.number_input("Change Threshold (%)", range_thresh[0], range_thresh[1], float(st.session_state.altdata_settings[key_prefix]["threshold"]), key=f"{key_prefix}_thresh_{key_prefix}")
            weight = st.slider("Weight", 0.0, 1.0, float(st.session_state.altdata_settings[key_prefix]["weight"]), 0.01, key=f"{key_prefix}_weight_{key_prefix}")
            st.session_state.altdata_settings[key_prefix] = {
                "enabled": enabled,
                "threshold": threshold,
                "weight": weight
            }

    st.markdown("### ð¦ Alt-Data Signals")

    col1, col2, col3 = st.columns(3)
    render_signal_card(col1, "ð Web Traffic", "web", True, 10, (0.0, 100.0), 0.25)
    render_signal_card(col2, "ð± Mobile App Usage", "app", True, 15, (0.0, 100.0), 0.20)
    render_signal_card(col3, "ð¦ Institutional Spend", "spend", True, 20, (0.0, 100.0), 0.20)

    col4, col5, col6 = st.columns(3)
    render_signal_card(col4, "ð¼ Job Postings", "jobs", True, 5, (0.0, 100.0), 0.10)
    render_signal_card(col5, "ð§µ Reddit Sentiment", "reddit", True, 10, (0.0, 100.0), 0.10)
    render_signal_card(col6, "ð¦ Shipping / Inventory", "ship", True, 8, (0.0, 100.0), 0.10)

    col7, col8, col9 = st.columns(3)
    render_signal_card(col7, "ð° Options Flow", "options", True, 20, (0.0, 100.0), 0.10)
    render_signal_card(col8, "ð¦ Dark Pool Activity", "darkpool", True, 20, (0.0, 100.0), 0.10)
    render_signal_card(col9, "ð Gamma Exposure (GEX)", "gex", True, 1.5, (0.0, 5.0), 0.05)

    st.divider()
    if st.button("â Apply Alt-Data Settings"):
        st.success("Alt-data weights and thresholds applied.")

    st.title("ð§ª Alt-Data Control Panel")

    st.markdown("Adjust signal inputs and weights per alt-data source. Coming next:")
    st.markdown("- Toggle signals on/off")
    st.markdown("- Adjust thresholds and weights")
    st.markdown("- Store signal settings in session state")
    st.markdown("- Visual signal breakdowns per ticker")

    st.success("â This tab is ready to be populated with your existing signal card layout.")
