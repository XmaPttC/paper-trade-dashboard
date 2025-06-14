import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(layout="wide", page_title="Harbourne Terminal")

# Toggle logic
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if st.button("🧭 Toggle Sidebar"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open

# Styling
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
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] p {
    color: #f1f5f9 !important;
}
.custom-table {
    background-color: orange;
    color: black;
    border-collapse: collapse;
    font-family: monospace;
    font-size: 13px;
    width: 100%;
}
.custom-table th, .custom-table td {
    border: 1px solid #333;
    padding: 4px 6px;
    text-align: left;
}
.custom-table th {
    background-color: darkorange;
}
.custom-table tr:nth-child(even) {
    background-color: #466686;
}
.custom-table tr:nth-child(odd) {
    background-color: #3d5975;
}
.custom-table tr:hover {
    background-color: #64748b !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
if st.session_state.sidebar_open:
    with st.sidebar:
        with st.expander("🎯 Smart Score Weights", expanded=True):
            peg_w = st.slider("PEG", 0, 100, 20, format="%d%%")
            eps_w = st.slider("EPS Growth", 0, 100, 15, format="%d%%")
            rating_w = st.slider("Analyst Rating", 0, 100, 20, format="%d%%")
            target_w = st.slider("Target Upside", 0, 100, 15, format="%d%%")
            sentiment_w = st.slider("Sentiment", 0, 100, 15, format="%d%%")
            insider_w = st.slider("Insider Depth", 0, 100, 15, format="%d%%")
        total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w

        with st.expander("📈 Core Fundamentals", expanded=True):
            pe_filter = st.checkbox("Enable PE Filter", True)
            pe_min = st.number_input("Min PE", value=0.0)
            pe_max = st.number_input("Max PE", value=30.0)
            peg_filter = st.checkbox("Enable PEG Filter", True)
            peg_max = st.slider("Max PEG", 0.0, 5.0, 2.0)
            eps_filter = st.checkbox("Enable EPS Growth Filter", True)
            eps_min = st.slider("Min EPS Growth", 0, 100, 15)

        with st.expander("🧠 Analyst Signals", expanded=True):
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

weights = {
    "PEG": peg_w / total,
    "EPS": eps_w / total,
    "Rating": rating_w / total,
    "Upside": target_w / total,
    "Sentiment": sentiment_w / total,
    "Insider": insider_w / total
}

# Load data
try:
    df = pd.read_csv("mock_stock_data.csv")
except:
    df = pd.DataFrame({
        "Ticker": ["AAPL", "TSLA", "MSFT"],
        "PEG": [1.2, 2.5, 1.8],
        "PE": [24, 70, 30],
        "EPS_Growth": [18, 35, 20],
        "AnalystRating": [2.2, 3.2, 1.8],
        "TargetUpside": [15, 20, 40],
        "SentimentScore": [0.21, 0.61, 0.85],
        "InsiderDepth": [0.60, 0.02, 0.71],
    })

# Apply filters
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
# --- Smart Score calculation ---
df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * weights["PEG"] +
    df["EPS_Growth"] * weights["EPS"] +
    (5 - df["AnalystRating"]) * weights["Rating"] +
    df["TargetUpside"] * weights["Upside"] +
    df["SentimentScore"] * weights["Sentiment"] +
    df["InsiderDepth"] * weights["Insider"]
)

# --- Score badge ---
q1, q2, q3 = df["SmartScore"].quantile([0.25, 0.5, 0.75])
def badge(score):
    if score >= q3: return "🟩 Top Performer"
    elif score >= q2: return "🟨 Above Average"
    elif score >= q1: return "🟥 Below Average"
    else: return "⬛ Low Tier"
df["Badge"] = df["SmartScore"].apply(badge)

# --- Info boxes ---
st.title("🚀 Harbourne Terminal")
st.markdown(f"""
<div style='display: flex; align-items: center; gap: 20px; margin-bottom: 4px;'>
  <div style='border:1px solid #ccc; padding:4px 8px;'><strong>Total Results:</strong> {len(df)}</div>
  <div style='border:1px solid #ccc; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# --- HTML Table ---
table_html = f""" 
<table class="custom-table">
    <tr>
        <th>Ticker</th><th>SmartScore</th><th>Badge</th>
        <th>PE</th><th>PEG</th><th>EPS_Growth</th>
        <th>AnalystRating</th><th>TargetUpside</th>
        <th>SentimentScore</th><th>InsiderDepth</th>
    </tr>
    {''.join(f"<tr><td>{row.Ticker}</td><td>{row.SmartScore:.2f}</td><td>{row.Badge}</td><td>{row.PE}</td><td>{row.PEG}</td><td>{row.EPS_Growth}</td><td>{row.AnalystRating}</td><td>{row.TargetUpside}</td><td>{row.SentimentScore}</td><td>{row.InsiderDepth}</td></tr>" for _, row in df.iterrows())}
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)

# --- Score audit tables ---
st.markdown("### 🧠 Smart Score Breakdown")
for _, row in df.iterrows():
    with st.expander(f"🔍 {row['Ticker']} – {row['Badge']} – Score {row['SmartScore']:.2f}"):
        factors = {
            "PEG": 1 / row["PEG"],
            "EPS": row["EPS_Growth"],
            "Rating": 5 - row["AnalystRating"],
            "Upside": row["TargetUpside"],
            "Sentiment": row["SentimentScore"],
            "Insider": row["InsiderDepth"]
        }
        breakdown = []
        for factor, val in factors.items():
            w = weights[factor]
            breakdown.append({
                "Factor": factor,
                "Input": round(val, 2),
                "Weight": f"{w * 100:.0f}%",
                "Contribution": f"{val * w:.2f}"
            })
        st.table(pd.DataFrame(breakdown))
