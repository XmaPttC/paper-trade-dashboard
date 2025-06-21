import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="Terminal")

# Load data
df = pd.read_csv("mock_stock_data.csv")

# Define and enforce column order
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
            signal_col = f"{key.capitalize()}Sc"
            if signal_col in row:
                value = row[signal_col]
                weight = settings.get("weight", 0)
                score += value * weight
                total_weight += weight
    return round(score / total_weight, 2) if total_weight > 0 else 0.0

df["AltDataScore"] = df.apply(compute_altdata_score, axis=1)

# --- Terminal Score ---
df["TerminalScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * 0.2 +
    df["EPSGr"] * 0.15 +
    (5 - df["AnalystSc"]) * 0.2 +
    df["TrgtUpside"] * 0.15 +
    df["SentSc"] * 0.15 +
    df["InsiderSc"] * 0.15 +
    df["AltDataScore"]
).round(2)

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
.custom-table th { background-color: #334155; cursor: pointer; }
.custom-table tr:nth-child(even) { background-color: #3d5975; }
.custom-table tr:nth-child(odd) { background-color: #466686; }
.custom-table tr:hover { background-color: #64748b; }
a.ticker-link { color: #93c5fd; text-decoration: none; }
a.ticker-link:hover { text-decoration: underline; }
.suffix-M { color: #c084fc; font-weight: bold; }
.suffix-B { color: #86efac; font-weight: bold; }
.suffix-T { color: #f87171; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Tabbed Layout ---
tab1, tab2 = st.tabs(["📈 Terminal", "🧪 Alt-Data Control Panel"])

with tab1:
    st.title("Terminal")
    st.markdown(f"""
    <div style='display: flex; gap: 20px; margin-bottom: 4px;'>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
      <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
    </div>
    <hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
    """, unsafe_allow_html=True)

    # Display HTML table
    table_cols = ["Ticker", "Price", "TerminalScore", "AltDataScore", "PEG", "PE", "EPSGr", "MktCap", "30DayVol", "AnalystSc", "TrgtUpside"]
    header_html = ''.join(f"<th>{col}</th>" for col in table_cols)
    row_html = ""
    for _, row in df.iterrows():
        row_cells = ""
        for col in table_cols:
            val = row[col]
            if col == "Ticker":
                val = f"<a class='ticker-link' href='https://finance.yahoo.com/quote/{val}' target='_blank'>{val}</a>"
            elif col == "MktCap":
                val = f"{val/1e9:.1f}<span class='suffix-B'>B</span>" if val >= 1e9 else f"{val/1e6:.1f}<span class='suffix-M'>M</span>"
            elif col == "30DayVol":
                val = f"{val/1e6:.1f}M"
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

    # --- AG Grid Selection ---
    st.markdown("### 🔍 Select a Stock to View Signal Summary")
    ag_df = df[["Ticker", "Price", "AltDataScore"]]
    gb = GridOptionsBuilder.from_dataframe(ag_df)
    gb.configure_selection("single", use_checkbox=False)
    grid_response = AgGrid(
        ag_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=200,
        fit_columns_on_grid_load=True
    )

    selected_rows = grid_response["selected_rows"]
    if selected_rows and isinstance(selected_rows, list) and len(selected_rows) > 0:
        st.session_state["selected_ticker"] = selected_rows[0]["Ticker"]

    if "selected_ticker" in st.session_state:
        ticker = st.session_state["selected_ticker"]
        selected_row = df[df["Ticker"] == ticker]
        if not selected_row.empty:
            selected_row = selected_row.iloc[0]
            with st.sidebar:
                st.markdown(f"### 📊 Signal Summary: {ticker}")
                st.markdown("---")
                for col in ["AltDataScore", "SentSc", "RedditSc", "InsiderSc", "TrgtUpside", "AnalystSc"]:
                    if col in selected_row:
                        st.markdown(f"**{col}**: {selected_row[col]}")
