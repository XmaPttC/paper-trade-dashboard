import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="Harbourne Terminal")

# Sidebar toggle
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if st.button("Toggle Sidebar"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open

# --- Styling ---
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
.ag-theme-streamlit {
    font-size: 13px !important;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
if st.session_state.sidebar_open:
    with st.sidebar:
        with st.expander("⚙ Smart Score Weights"):
            peg_w = st.slider("PEG", 0, 100, 20)
            eps_w = st.slider("EPS Growth", 0, 100, 15)
            rating_w = st.slider("Analyst Rating", 0, 100, 20)
            target_w = st.slider("Target Upside", 0, 100, 15)
            sentiment_w = st.slider("Sentiment", 0, 100, 15)
            insider_w = st.slider("Insider Depth", 0, 100, 15)
        total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w

        with st.expander("⚙ Core Fundamentals"):
            pe_filter = st.checkbox("Enable PE Filter", True)
            pe_min = st.number_input("Min PE", value=0.0)
            pe_max = st.number_input("Max PE", value=30.0)
            peg_filter = st.checkbox("Enable PEG Filter", True)
            peg_max = st.slider("Max PEG", 0.0, 5.0, 2.0)
            eps_filter = st.checkbox("Enable EPS Growth Filter", True)
            eps_min = st.slider("Min EPS Growth", 0, 100, 15)

        with st.expander("⚙ Analyst Signals"):
            analyst_filter = st.checkbox("Enable Analyst Rating Filter", True)
            rating_max = st.slider("Max Analyst Rating", 1.0, 5.0, 3.5)
            target_filter = st.checkbox("Enable Target Upside Filter", True)
            target_min = st.slider("Min Target Upside", 0, 100, 20)
else:
    peg_w = eps_w = rating_w = target_w = sentiment_w = insider_w = 1
    pe_filter = peg_filter = eps_filter = analyst_filter = target_filter = False
    pe_min = 0
    pe_max = 100
    peg_max = 10.0
    eps_min = 0
    rating_max = 5.0
    target_min = 0
    total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w

# --- Load Data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Filters ---
if pe_filter:
    df = df[(df["PE"] >= pe_min) & (df["PE"] <= pe_max)]
if peg_filter:
    df = df[df["PEG"] <= peg_max]
if eps_filter:
    df = df[df["EPS_Growth"] >= eps_min]
if analyst_filter:
    df = df[df["AnalystRating"] <= rating_max]
if target_filter:
    df = df[df["TargetUpside"] >= target_min]

# --- SmartScore Calculation ---
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

# --- Badge Ranking ---
q1, q2, q3 = df["SmartScore"].quantile([0.25, 0.5, 0.75])
def badge(score):
    if score >= q3: return "🟩 Top Quartile"
    elif score >= q2: return "🟨 Top Half"
    elif score >= q1: return "🟥 Bottom Half"
    else: return "⬛ Bottom Quartile"
df["Badge"] = df["SmartScore"].apply(badge)

# --- Add Notes Placeholder ---
for ticker in df["Ticker"]:
    note_key = f"note_{ticker}"
    if note_key not in st.session_state:
        st.session_state[note_key] = ""

df["Notes"] = df["Ticker"].apply(lambda x: st.session_state.get(f"note_{x}", ""))

# --- Info Header ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- Display Table with st_aggrid ---
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True)
gb.configure_column("Notes", editable=True)
gb.configure_grid_options(domLayout='normal', suppressRowClickSelection=False)
gb.configure_selection(selection_mode="single", use_checkbox=False)

# --- Apply custom row style ---
gb.configure_grid_options(
    getRowStyle="""
    function(params) {
        return {
            background: '#3d5975',
            color: '#f1f5f9',
            fontSize: '13px'
        };
    }
    """
)

grid_options = gb.build()

AgGrid(
    df,
    gridOptions=grid_options,
    height=500,
    width='100%',
    update_mode=GridUpdateMode.VALUE_CHANGED,
    fit_columns_on_grid_load=True,
    theme="streamlit"
)
