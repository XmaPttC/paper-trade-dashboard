import streamlit as st
st.set_page_config(layout="wide", page_title="Harbourne Terminal")

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- DARK THEME CSS FIXES ---
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
}
div[data-testid="stDataFrameContainer"] {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    border-radius: 0px !important;
}
thead th, div[role="table"], div[role="gridcell"], div[role="columnheader"] {
    background-color: #334155 !important;
    color: #f1f5f9 !important;
    border-radius: 0px !important;
    font-family: monospace !important;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: Expanders ---
with st.sidebar:
    with st.expander("🎯 Smart Score Weights", expanded=True):
        peg_w = st.slider("PEG", 0, 100, 20, format="%d%%")
        eps_w = st.slider("EPS Growth", 0, 100, 15, format="%d%%")
        rating_w = st.slider("Analyst Rating", 0, 100, 20, format="%d%%")
        target_w = st.slider("Target Upside", 0, 100, 15, format="%d%%")
        sentiment_w = st.slider("Sentiment", 0, 100, 15, format="%d%%")
        insider_w = st.slider("Insider Depth", 0, 100, 15, format="%d%%")

        total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w
        if total == 0: total = 1
        weights = {
            "PEG": peg_w / total,
            "EPS": eps_w / total,
            "Rating": rating_w / total,
            "Upside": target_w / total,
            "Sentiment": sentiment_w / total,
            "Insider": insider_w / total
        }

        st.subheader("📊 Score Composition")
        labels = list(weights.keys())
        sizes = list(weights.values())
        colors = ['#3b82f6', '#10b981', '#facc15', '#f97316', '#8b5cf6', '#ec4899']
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        fig.patch.set_facecolor("#1e293b")
        ax.set_facecolor("#1e293b")
        ax.pie(sizes, labels=labels, colors=colors, startangle=140,
               autopct='%1.0f%%', pctdistance=0.85, wedgeprops=dict(width=0.3))
        ax.axis('equal')
        st.pyplot(fig)

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

# --- READ MOCK DATA ---
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

# --- FILTERING LOGIC ---
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

# --- SCORE CALC ---
df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * weights["PEG"] +
    df["EPS_Growth"] * weights["EPS"] +
    (5 - df["AnalystRating"]) * weights["Rating"] +
    df["TargetUpside"] * weights["Upside"] +
    df["SentimentScore"] * weights["Sentiment"] +
    df["InsiderDepth"] * weights["Insider"]
)

# --- BADGES ---
q1, q2, q3 = df["SmartScore"].quantile([0.25, 0.5, 0.75])
def badge(score):
    if score >= q3:
        return "🟩 Top Performer"
    elif score >= q2:
        return "🟨 Above Average"
    elif score >= q1:
        return "🟥 Below Average"
    else:
        return "⬛ Low Tier"
df["Badge"] = df["SmartScore"].apply(badge)

# --- DISPLAY TABLE ---
st.title("🚀 Harbourne Terminal")
st.data_editor(
    df[[
        "Ticker", "SmartScore", "Badge", "PE", "PEG", "EPS_Growth",
        "AnalystRating", "TargetUpside", "SentimentScore", "InsiderDepth"
    ]],
    use_container_width=True,
    hide_index=True,
    disabled=["Ticker", "Badge"]
)

# --- SCORE AUDIT TABLES ---
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
        rows = []
        for factor, value in factors.items():
            w = weights[factor]
            rows.append({
                "Factor": factor,
                "Input Value": round(value, 2),
                "Weight": f"{w*100:.0f}%",
                "Contribution": f"{value * w:.2f}"
            })
        st.table(pd.DataFrame(rows))
