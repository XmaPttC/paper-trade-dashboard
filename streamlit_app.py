import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Terminal")

# --- Load data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Enforce column order ---
column_order = [
    "Ticker", "Price", "TerminalScore", "PEG", "PE", "EPSGr", "MktCap",
    "30DayVol", "AnalystSc", "TrgtUpside", "Sector", "InsiderSc",
    "SentSc", "RedditSc", "52wH"
]
df = df[[col for col in column_order if col in df.columns]]

# --- Sidebar CSS and layout ---
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
    padding: 8px;
    width: 240px !important;
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
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    with st.expander("Filter Stocks", expanded=True):
        def number_input_pair(label):
            st.markdown(f'<div class="sidebar-label">{label}</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col_min = float(df[label].min()) if label in df.columns else 0.0
            col_max = float(df[label].max()) if label in df.columns else 100.0
            with col1: min_val = st.number_input(f"Min {label}", value=col_min, key=f"{label}_min")
            with col2: max_val = st.number_input(f"Max {label}", value=col_max, key=f"{label}_max")
            return min_val, max_val

        price_min, price_max = number_input_pair("Price")
        peg_min, peg_max = number_input_pair("PEG")
        pe_min, pe_max = number_input_pair("PE")
        eps_min, eps_max = number_input_pair("EPSGr")
        rating_min, rating_max = number_input_pair("AnalystSc")
        upside_min, upside_max = number_input_pair("TrgtUpside")
        mcap_min, mcap_max = number_input_pair("MktCap (M)")
        vol_min, vol_max = number_input_pair("30DayVol (M)")

    st.toggle("US Only")
    st.toggle("Nasdaq Only")
    st.toggle("NYSE Only")

    with st.expander("Smart Score Weights", expanded=False):
        peg_w = st.slider("PEG", 0, 100, 50)
        eps_w = st.slider("EPS Growth", 0, 100, 50)
        rating_w = st.slider("Analyst Rating", 0, 100, 50)
        upside_w = st.slider("Target Upside", 0, 100, 50)
        sentiment_w = st.slider("Sentiment", 0, 100, 50)
        insider_w = st.slider("Insider Depth", 0, 100, 50)

    st.markdown("---")
    st.markdown("📈 Charts")
    st.markdown("🔬 Research")
    st.markdown("🧪 Misc")
    st.markdown("📚 Information Hub")

# --- Convert fields for filtering ---
df["MktCap"] = pd.to_numeric(df["MktCap"], errors="coerce") / 1e6  # Convert to millions
df["30DayVol"] = pd.to_numeric(df["30DayVol"], errors="coerce") / 1e6

# --- Filtering ---
df = df[
    (df["Price"].between(price_min, price_max)) &
    (df["PEG"].between(peg_min, peg_max)) &
    (df["PE"].between(pe_min, pe_max)) &
    (df["EPSGr"].between(eps_min, eps_max)) &
    (df["AnalystSc"].between(rating_min, rating_max)) &
    (df["TrgtUpside"].between(upside_min, upside_max)) &
    (df["MktCap"].between(mcap_min, mcap_max)) &
    (df["30DayVol"].between(vol_min, vol_max))
]

# --- TerminalScore Calculation ---
total = sum([peg_w, eps_w, rating_w, upside_w, sentiment_w, insider_w]) or 1
weights = {
    "PEG": peg_w / total,
    "EPSGr": eps_w / total,
    "AnalystSc": rating_w / total,
    "TrgtUpside": upside_w / total,
    "SentSc": sentiment_w / total,
    "InsiderSc": insider_w / total
}
df["TerminalScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * weights["PEG"] +
    df["EPSGr"] * weights["EPSGr"] +
    (5 - df["AnalystSc"]) * weights["AnalystSc"] +
    df["TrgtUpside"] * weights["TrgtUpside"] +
    df["SentSc"] * weights["SentSc"] +
    df["InsiderSc"] * weights["InsiderSc"]
).round(2)

# --- Format display fields ---
def format_market_cap(m):
    if m >= 1e6: return f"<span style='color:#f87171'>{m/1e6:.1f}T</span>"
    elif m >= 1e3: return f"<span style='color:#4ade80'>{m/1e3:.1f}B</span>"
    else: return f"<span style='color:#c084fc'>{m:.0f}M</span>"

df["MktCapDisplay"] = df["MktCap"].apply(format_market_cap)
df["30DayVolDisplay"] = df["30DayVol"].apply(lambda v: f"{v:.1f}M")
df["TrgtUpsideDisplay"] = df["TrgtUpside"].apply(lambda x: f"{x:.1f}%")

# --- Display ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'>
    <strong>Total Results:</strong> {len(df)}
  </div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'>
    <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}
  </div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- Table Rendering ---
visible_columns = ["Ticker", "Price", "TerminalScore", "PEG", "PE", "EPSGr", "MktCapDisplay",
                   "30DayVolDisplay", "AnalystSc", "TrgtUpsideDisplay", "Sector", "InsiderSc",
                   "SentSc", "RedditSc", "52wH"]

header_html = ''.join(f"<th>{col}</th>" for col in visible_columns)
row_html = ""
for _, row in df.iterrows():
    row_cells = ""
    for col in visible_columns:
        val = row[col]
        if col == "Ticker":
            val = f"<a class='ticker-link' href='https://finance.yahoo.com/quote/{val}' target='_blank'>{val}</a>"
        row_cells += f"<td>{val}</td>"
    row_html += f"<tr>{row_cells}</tr>"

st.markdown(f"""
<table class="custom-table">
    <thead><tr>{header_html}</tr></thead>
    <tbody>{row_html}</tbody>
</table>
""", unsafe_allow_html=True)
