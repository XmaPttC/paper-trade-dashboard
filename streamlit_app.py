import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- Streamlit Page Setup ---
st.set_page_config(layout="wide", page_title="Terminal")

# --- Load and Format Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("mock_stock_data.csv")
    df["AltDataScore"] = (
        df["InsiderSc"] * 0.3 +
        df["SentSc"] * 0.3 +
        df["RedditSc"] * 0.3 +
        df["TrgtUpside"] * 0.1
    ).round(2)
    df["TerminalScore"] = (
        (1 / df["PEG"].clip(lower=0.01)) * 0.2 +
        df["EPSGr"] * 0.15 +
        (5 - df["AnalystSc"]) * 0.2 +
        df["TrgtUpside"] * 0.15 +
        df["SentSc"] * 0.15 +
        df["InsiderSc"] * 0.15 +
        df["AltDataScore"]
    ).round(2)
    return df

df = load_data()

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
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
    font-size: 13px;
    padding: 8px;
    width: 320px !important;
}
.sidebar-label {
    font-size: 13px;
    margin-bottom: 4px;
    border-bottom: 0.5px solid #334155;
}
.filter-row {
    display: flex;
    justify-content: space-between;
    gap: 6px;
    margin-bottom: 10px;
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

# --- Header ---
st.title("📈 Harbourne Terminal")
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

def format_upside(val):
    return f"{val:.1f}%"

# --- Render Custom HTML Table ---
columns = ["Ticker", "Price", "TerminalScore", "PEG", "PE", "EPSGr", "MktCap",
           "30DayVol", "AnalystSc", "TrgtUpside", "AltDataScore"]

header_html = ''.join(f"<th>{col}</th>" for col in columns)
rows_html = ""
for _, row in df.iterrows():
    row_cells = ""
    for col in columns:
        val = row[col]
        if col == "Ticker":
            val = f"<a class='ticker-link' href='https://finance.yahoo.com/quote/{val}' target='_blank'>{val}</a>"
        elif col == "MktCap":
            val = format_mktcap(val)
        elif col == "30DayVol":
            val = format_volume(val)
        elif col == "TrgtUpside":
            val = format_upside(val)
        row_cells += f"<td>{val}</td>"
    rows_html += f"<tr>{row_cells}</tr>"

st.markdown(f"""
<table class="custom-table">
<thead><tr>{header_html}</tr></thead>
<tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)

# --- Hidden AG Grid to Capture Row Clicks ---
ag_df = df[["Ticker", "Price", "AltDataScore"]].copy()
gb = GridOptionsBuilder.from_dataframe(ag_df)
gb.configure_selection("single", use_checkbox=False)
grid_options = gb.build()

grid_response = AgGrid(
    ag_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=1,  # Minimized
    fit_columns_on_grid_load=True,
    theme="streamlit"
)

# --- Store Selected Ticker ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

selected_rows = grid_response.get("selected_rows", [])
if isinstance(selected_rows, list) and selected_rows:
    st.session_state.selected_ticker = selected_rows[0]["Ticker"]

# --- Right Sidebar: Signal Summary ---
if st.session_state.selected_ticker:
    selected = df[df["Ticker"] == st.session_state.selected_ticker].iloc[0]
    with st.sidebar:
        st.markdown(f"### 🧪 Signal Summary: {selected['Ticker']}")
        st.markdown("---")
        st.markdown(f"**AltDataScore**: {selected['AltDataScore']}")
        st.markdown(f"**Sentiment**: {selected['SentSc']}")
        st.markdown(f"**Reddit**: {selected['RedditSc']}")
        st.markdown(f"**Insider**: {selected['InsiderSc']}")
        st.markdown(f"**Target Upside**: {selected['TrgtUpside']}%")
        st.markdown(f"**Analyst Score**: {selected['AnalystSc']}")
