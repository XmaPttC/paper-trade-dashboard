import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Terminal")

# --- Load Data ---
df = pd.read_csv("mock_stock_data.csv")

# --- Sidebar Filters and Weights ---
with st.sidebar:
    st.header("📊 Filter Stocks")

    pe_min = st.number_input("Min PE", value=0.0)
    pe_max = st.number_input("Max PE", value=50.0)

    peg_max = st.slider("Max PEG", 0.0, 5.0, 2.0)
    eps_min = st.slider("Min EPS Growth (%)", 0, 100, 10)
    rating_max = st.slider("Max Analyst Rating", 1.0, 5.0, 3.5)
    upside_min = st.slider("Min Target Upside (%)", 0, 100, 10)

    st.divider()
    st.header("⚖️ Smart Score Weights")

    peg_w = st.slider("PEG Weight", 0, 100, 20)
    eps_w = st.slider("EPS Growth Weight", 0, 100, 15)
    rating_w = st.slider("Analyst Rating Weight", 0, 100, 20)
    upside_w = st.slider("Target Upside Weight", 0, 100, 15)
    sentiment_w = st.slider("Sentiment Score Weight", 0, 100, 15)
    insider_w = st.slider("Insider Depth Weight", 0, 100, 15)

# --- Apply Filters ---
df = df[
    (df["PE"] >= pe_min) & (df["PE"] <= pe_max) &
    (df["PEG"] <= peg_max) &
    (df["EPSGrowth"] >= eps_min) &
    (df["AnalystRating"] <= rating_max) &
    (df["TargetUpside"] >= upside_min)
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

# --- Info Header ---
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- HTML Table Rendering ---
table_html = f"""<table class="custom-table">
<thead>
<tr><th>Ticker</th><th>Price</th><th>SmartScore</th><th>PEG</th><th>PE</th><th>EPSGrowth</th>
<th>MarketCap</th><th>30DayVol</th><th>AnalystRating</th><th>TargetUpside</th><th>Sector</th>
<th>InsiderDepth</th><th>SentimentScore</th><th>RedditSentiment</th><th>HiLoProximity</th><th>Badge</th></tr>
</thead><tbody>
"""
for _, row in df.iterrows():
    yahoo_link = f"https://finance.yahoo.com/quote/{row['Ticker']}"
    table_html += f"""
    <tr>
        <td><a href="{yahoo_link}" target="_blank">{row['Ticker']}</a></td>
        <td>{row['Price']}</td>
        <td>{row['SmartScore']:.2f}</td>
        <td>{row['PEG']}</td>
        <td>{row['PE']}</td>
        <td>{row['EPSGrowth']}</td>
        <td>{row['MarketCap']}</td>
        <td>{row['30DayVol']}</td>
        <td>{row['AnalystRating']}</td>
        <td>{row['TargetUpside']}</td>
        <td>{row['Sector']}</td>
        <td>{row['InsiderDepth']}</td>
        <td>{row['SentimentScore']}</td>
        <td>{row['RedditSentiment']}</td>
        <td>{row['HiLoProximity']}</td>
        <td>{row['Badge']}</td>
    </tr>
    """
table_html += "</tbody></table>"
st.markdown(table_html, unsafe_allow_html=True)
