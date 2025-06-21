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

    import pandas as pd
    from datetime import datetime

    # === Load and Process Stock Data ===
    df = pd.read_csv("mock_stock_data.csv")
    column_order = [
        "Ticker", "Price", "PEG", "PE", "EPSGr", "MktCap", "30DayVol",
        "AnalystSc", "TrgtUpside", "Sector", "InsiderSc", "SentSc", "RedditSc", "52wH"
    ]
    df = df[[col for col in column_order if col in df.columns]]

    # --- AltData Score Calculation ---
    def compute_altdata_score(row):
        score = 0.0
        total_weight = 0.0
        for key, settings in st.session_state.get("altdata_settings", {}).items():
            if settings["enabled"]:
                value = row.get(f"{key.capitalize()}Sc", 0)
                weight = settings.get("weight", 0)
                score += value * weight
                total_weight += weight
        return round(score / total_weight, 2) if total_weight > 0 else 0.0

    df["AltDataScore"] = df.apply(compute_altdata_score, axis=1)

    # --- Terminal Score Calculation ---
    df["TerminalScore"] = (
        (1 / df["PEG"].clip(lower=0.01)) * 0.2 +
        df["EPSGr"] * 0.15 +
        (5 - df["AnalystSc"]) * 0.2 +
        df["TrgtUpside"] * 0.15 +
        df["SentSc"] * 0.15 +
        df["InsiderSc"] * 0.15 +
        df["AltDataScore"]
    ).round(2)

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

    # --- Display Table ---
    st.title("Terminal")
    st.markdown(f"""
    <div style='display: flex; gap: 20px; margin-bottom: 4px;'>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
    </div>
    <hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
    """, unsafe_allow_html=True)

    header_html = ''.join(f"<th>{col}</th>" for col in df.columns.insert(2, "AltDataScore"))
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
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

# --- AG Grid Setup (Hidden or Minimal Table for Row Selection) ---
with st.expander("ð¦ Row Selector", expanded=False):
    gb = GridOptionsBuilder.from_dataframe(df[["Ticker"]])
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()
    grid_response = AgGrid(
        df[["Ticker"]],
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=150,
        theme="streamlit",
    )
    selected_rows = grid_response["selected_rows"]
    selected_ticker = selected_rows[0]["Ticker"] if selected_rows else None
    st.session_state.selected_ticker = selected_ticker



# --- Signal Summary Panel ---
if st.session_state.get("selected_ticker"):
    st.sidebar.markdown("### ð Signal Summary")
    row = df[df["Ticker"] == st.session_state.selected_ticker].iloc[0]
    for signal_key in ["AltDataScore", "SentSc", "RedditSc", "InsiderSc", "TrgtUpside", "AnalystSc"]:
        st.sidebar.markdown(f"**{signal_key}**: {row[signal_key]}")
