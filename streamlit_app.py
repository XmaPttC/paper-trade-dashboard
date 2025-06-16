import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Terminal")

# --- Load data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Define and enforce column order ---
column_order = [
    "Ticker", "Price", "SmartScore", "PEG", "PE", "EPSGrowth", "MarketCap",
    "30DayVol", "AnalystRating", "TargetUpside", "Sector", "InsiderDepth",
    "SentimentScore", "RedditSentiment", "HiLoProximity"
]
df = df[[col for col in column_order if col in df.columns]]

# --- Sorting ---
sort_column = st.selectbox("Sort by column", df.columns.tolist(), index=0)
df = df.sort_values(by=sort_column)

# --- Sidebar Layout ---
with st.sidebar:
    st.markdown("""
        <style>
        /* Sidebar container */
        section[data-testid="stSidebar"] {
            background-color: #000000;
            padding: 16px;
        }
        
        /* General text and inputs */
        section[data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
            font-family: 'Lato', sans-serif;
            font-size: 14px !important;
        }
        
        /* Labels */
        section[data-testid="stSidebar"] label {
            font-size: 13px !important;
            font-weight: 500;
            color: #cbd5e1 !important;
        }
        
        /* Text inputs */
        section[data-testid="stSidebar"] input[type="number"],
        section[data-testid="stSidebar"] input[type="text"] {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            padding: 6px 8px !important;
            font-size: 13px !important;
        }
        
        /* Toggle switches */
        div[data-testid="stToggle"] {
            padding-top: 6px;
            padding-bottom: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.expander("📊 Filter Stocks", expanded=True):
        st.markdown("#### PEG Range")
        peg_col1, peg_col2 = st.columns(2)
        peg_min = peg_col1.number_input("Min PEG", key="peg_min", value=0.0, label_visibility="collapsed")
        peg_max = peg_col2.number_input("Max PEG", key="peg_max", value=2.0, label_visibility="collapsed")
    
        st.markdown("#### EPS Growth (%) Range")
        eps_col1, eps_col2 = st.columns(2)
        eps_min = eps_col1.number_input("Min EPS Growth", key="eps_min", value=10, label_visibility="collapsed")
        eps_max = eps_col2.number_input("Max EPS Growth", key="eps_max", value=100, label_visibility="collapsed")
    
        st.markdown("#### Analyst Rating Range")
        rating_col1, rating_col2 = st.columns(2)
        rating_min = rating_col1.number_input("Min Rating", key="rating_min", value=1.0, step=0.1, label_visibility="collapsed")
        rating_max = rating_col2.number_input("Max Rating", key="rating_max", value=3.5, step=0.1, label_visibility="collapsed")

        st.divider()
        # Dummy toggle filters
        with st.expander("🌐 Market Filters"):
            us_only = st.toggle("US Only", value=True)
            nasdaq_only = st.toggle("Nasdaq Only", value=False)
            nyse_only = st.toggle("NYSE Only", value=False)

    with st.expander("Smart Score Weights"):
        peg_w = st.slider("PEG Weight", 0, 100, 20)
        eps_w = st.slider("EPS Growth Weight", 0, 100, 15)
        rating_w = st.slider("Analyst Rating Weight", 0, 100, 20)
        upside_w = st.slider("Target Upside Weight", 0, 100, 15)
        sentiment_w = st.slider("Sentiment Score Weight", 0, 100, 15)
        insider_w = st.slider("Insider Depth Weight", 0, 100, 15)

    st.divider()
    st.header("📈 Charts")
    st.header("📚 Research")
    st.header("🧪 Misc")
    st.header("🧠 Information Hub")

# --- Apply Filters ---
df = df[
    (df["PEG"] >= peg_min) & (df["PEG"] <= peg_max) &
    (df["EPSGrowth"] >= eps_min) & (df["EPSGrowth"] <= eps_max) &
    (df["AnalystRating"] >= rating_min) & (df["AnalystRating"] <= rating_max) &
    (df["TargetUpside"] >= upside_min) & (df["TargetUpside"] <= upside_max)
]

# --- SmartScore Calculation ---
total = sum([peg_w, eps_w, rating_w, upside_w, sentiment_w, insider_w]) or 1
weights = {
    "PEG": peg_w / total,
    "EPSGrowth": eps_w / total,
    "Rating": rating_w / total,
    "Upside": upside_w / total,
    "SentimentScore": sentiment_w / total,
    "InsiderDepth": insider_w / total
}
df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * weights["PEG"] +
    df["EPSGrowth"] * weights["EPSGrowth"] +
    (5 - df["AnalystRating"]) * weights["Rating"] +
    df["TargetUpside"] * weights["Upside"] +
    df["SentimentScore"] * weights["SentimentScore"] +
    df["InsiderDepth"] * weights["InsiderDepth"]
).round(2)

# --- Badge Ranking ---
q1, q2, q3 = df["SmartScore"].quantile([0.25, 0.5, 0.75])
def badge(score):
    if score >= q3: return "🟩 Top Quartile"
    elif score >= q2: return "🟨 Top Half"
    elif score >= q1: return "🟥 Bottom Half"
    else: return "⬛ Bottom Quartile"
df["Badge"] = df["SmartScore"].apply(badge)

# --- Styling ---
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
</style>
""", unsafe_allow_html=True)

# --- Title & meta info ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- Table Rendering ---
header_html = ''.join(f"<th>{col}</th>" for col in df.columns)
row_html = ""
for _, row in df.iterrows():
    row_cells = ""
    for col in df.columns:
        val = row[col]
        if col == "Ticker":
            link = f"https://finance.yahoo.com/quote/{val}"
            val = f"<a class='ticker-link' href='{link}' target='_blank'>{val}</a>"
        row_cells += f"<td>{val}</td>"
    row_html += f"<tr>{row_cells}</tr>"

st.markdown(f"""
<table class="custom-table">
    <thead><tr>{header_html}</tr></thead>
    <tbody>{row_html}</tbody>
</table>
""", unsafe_allow_html=True)
