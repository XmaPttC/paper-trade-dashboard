import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="Harbourne Terminal")

# --- Basic dark styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
html, body, .stApp, .block-container {
    font-family: 'Lato', sans-serif;
    background-color: #1e293b;
    color: #f1f5f9;
}
section[data-testid="stSidebar"] {
    background-color: #1e293b;
    color: #f1f5f9;
}
section[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Load data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Smart Score Calculation ---
peg_w, eps_w, rating_w, target_w, sentiment_w, insider_w = 20, 15, 20, 15, 15, 15
total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w

weights = {
    "PEG": peg_w / total,
    "EPS": eps_w / total,
    "Rating": rating_w / total,
    "Upside": target_w / total,
    "Sentiment": sentiment_w / total,
    "Insider": insider_w / total
}

df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * weights["PEG"] +
    df["EPS_Growth"] * weights["EPS"] +
    (5 - df["AnalystRating"]) * weights["Rating"] +
    df["TargetUpside"] * weights["Upside"] +
    df["SentimentScore"] * weights["Sentiment"] +
    df["InsiderDepth"] * weights["Insider"]
).round(2)

# --- Score badges ---
q1, q2, q3 = df["SmartScore"].quantile([0.25, 0.5, 0.75])
def badge(score):
    if score >= q3: return "🟩 Top Quartile"
    elif score >= q2: return "🟨 Top Half"
    elif score >= q1: return "🟥 Bottom Half"
    else: return "⬛ Bottom Quartile"
df["Badge"] = df["SmartScore"].apply(badge)

# --- Header Info ---
st.title("📊 Harbourne Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 8px;'>
  <div style='border:1px solid #ccc; font-size: 11px; padding:4px 8px;'>📈 <strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 11px; padding:4px 8px;'>🗓️ <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc;' />
""", unsafe_allow_html=True)

# --- Configure AG Grid ---
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True)
gb.configure_selection(selection_mode="single", use_checkbox=False)

# ✅ Set row styling
gb.configure_grid_options(getRowStyle="""
function(params) {
    if (params.node.rowIndex % 2 === 0) {
        return { style: { background: "#3d5975", color: "#f1f5f9", fontSize: "13px", fontFamily: "Lato" } };
    } else {
        return { style: { background: "#466686", color: "#f1f5f9", fontSize: "13px", fontFamily: "Lato" } };
    }
}
""")

grid_options = gb.build()

# --- Render Table ---
AgGrid(
    df,
    gridOptions=grid_options,
    theme="streamlit",  # You can try "balham-dark" or "material-dark" as well
    update_mode=GridUpdateMode.NO_UPDATE,
    height=600,
    fit_columns_on_grid_load=True
)
