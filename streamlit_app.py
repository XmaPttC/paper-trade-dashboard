import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG & THEME ----
st.set_page_config(layout="wide", page_title="Stock Screener Pro")

# 🌈 THEME OVERRIDE
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
        html, body, .stApp, .block-container {
            font-family: 'Lato', sans-serif;
            background-color: #f9fafb !important;
            color: #1f2937 !important;
        }
        h1, h2, h3 {
            color: #111827 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9 !important;
        }
        header[data-testid="stHeader"] {
            background-color: #f9fafb !important;
        }
        .stDataEditor {
            background-color: #ffffff !important;
        }
        button[kind="secondary"] {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 6px;
        }
        button[kind="secondary"]:hover {
            background-color: #1e40af !important;
        }
        .stNumberInput input, .stSelectbox, .stSlider {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
df = pd.read_csv("mock_stock_data.csv")

# ---- STATE INIT ----
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()
if "restored" not in st.session_state:
    st.session_state.restored = False

# ---- SIDEBAR SMART SCORE CONTROL ----
with st.sidebar:
    st.title("🎯 Smart Score Weights")

    peg_w = st.slider("PEG", 0.0, 1.0, 0.2)
    eps_w = st.slider("EPS Growth", 0.0, 1.0, 0.15)
    rating_w = st.slider("Analyst Rating", 0.0, 1.0, 0.2)
    target_w = st.slider("Target Upside", 0.0, 1.0, 0.15)
    sentiment_w = st.slider("Sentiment", 0.0, 1.0, 0.15)
    insider_w = st.slider("Insider Depth", 0.0, 1.0, 0.15)

    total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w
    if total == 0: total = 1.0
    peg_w, eps_w, rating_w, target_w, sentiment_w, insider_w = [x/total for x in [peg_w, eps_w, rating_w, target_w, sentiment_w, insider_w]]

    st.subheader("📊 Score Composition")
    labels = ["PEG", "EPS", "Rating", "Upside", "Sentiment", "Insider"]
    sizes = [peg_w, eps_w, rating_w, target_w, sentiment_w, insider_w]
    colors = ['#3b82f6', '#10b981', '#facc15', '#f97316', '#8b5cf6', '#ec4899']
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    fig.patch.set_facecolor('#f9fafb')
    ax.set_facecolor('#ffffff')
    ax.pie(sizes, labels=labels, colors=colors, startangle=140,
           autopct='%1.0f%%', pctdistance=0.85, wedgeprops=dict(width=0.3))
    ax.axis('equal')
    st.pyplot(fig)

# ---- SMART SCORE COMPUTATION ----
df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * peg_w +
    df["EPS_Growth"] * eps_w +
    (5 - df["AnalystRating"]) * rating_w +
    df["TargetUpside"] * target_w +
    df["SentimentScore"] * sentiment_w +
    df["InsiderDepth"] * insider_w
)

# ---- FILTERS ----
with st.sidebar.expander("📈 Core Fundamentals", expanded=True):
    pe_filter = st.checkbox("Enable PE", value=True)
    pe_min = st.number_input("Min PE", value=0.0)
    pe_max = st.number_input("Max PE", value=30.0)
    peg_filter = st.checkbox("Enable PEG", value=True)
    peg_max = st.slider("Max PEG", 0.0, 5.0, 1.5)
    eps_filter = st.checkbox("Enable EPS Growth", value=True)
    eps_min = st.slider("Min EPS Growth", 0, 100, 20)

with st.sidebar.expander("🧠 Analyst Signals"):
    analyst_filter = st.checkbox("Enable Analyst Rating")
    rating_max = st.slider("Max Analyst Rating", 1.0, 5.0, 3.0)
    target_filter = st.checkbox("Enable Target Upside")
    target_min = st.slider("Min Upside (%)", 0, 200, 30)

with st.sidebar.expander("🔍 Alt Data"):
    insider_filter = st.checkbox("Enable Insider Filter")
    allowed = st.multiselect("Insider Activity", ["Heavy Buying", "Net Buying"], default=["Heavy Buying"])

# ---- TOP TOOLBAR ----
col1, col2, col3 = st.columns([2, 1, 1])
apply_filters = col1.button("🔎 Apply Filters")
if col2.button("♻️ Restore Hidden Rows"):
    st.session_state.hidden_rows.clear()
    st.session_state.restored = True
col3.download_button("⬇️ Export CSV", df.to_csv(index=False), file_name="filtered_stocks.csv")

# ---- FILTER LOGIC ----
filtered = df.copy()
if apply_filters:
    if pe_filter:
        filtered = filtered[(filtered["PE"] >= pe_min) & (filtered["PE"] <= pe_max)]
    if peg_filter:
        filtered = filtered[filtered["PEG"] <= peg_max]
    if eps_filter:
        filtered = filtered[filtered["EPS_Growth"] >= eps_min]
    if analyst_filter:
        filtered = filtered[filtered["AnalystRating"] <= rating_max]
    if target_filter:
        filtered = filtered[filtered["TargetUpside"] >= target_min]
    if insider_filter:
        filtered = filtered[filtered["InsiderActivity"].isin(allowed)]

filtered = filtered[~filtered["Ticker"].isin(st.session_state.hidden_rows)]

# ---- MAIN PANEL ----
st.title("🚀 Undervalued Growth Stock Screener")
if st.session_state.restored:
    st.success("All rows restored.")
    st.session_state.restored = False

if not filtered.empty:
    display_df = filtered[[
        "Ticker", "Price", "PE", "PEG", "EPS_Growth", "AnalystRating",
        "TargetUpside", "SentimentScore", "InsiderDepth", "SmartScore"
    ]].sort_values("SmartScore", ascending=False)

    st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SmartScore": st.column_config.NumberColumn(format="%.2f"),
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "PE": st.column_config.NumberColumn(format="%.1f"),
            "PEG": st.column_config.NumberColumn(format="%.2f"),
            "EPS_Growth": st.column_config.NumberColumn(format="%.0f%%"),
            "AnalystRating": st.column_config.NumberColumn(format="%.1f"),
            "TargetUpside": st.column_config.NumberColumn(format="%.0f%%"),
            "SentimentScore": st.column_config.NumberColumn(format="%.2f"),
            "InsiderDepth": st.column_config.NumberColumn(format="%.2f")
        },
        disabled=["Ticker"]
    )
else:
    st.warning("No stocks matched your filters or all have been hidden.")
