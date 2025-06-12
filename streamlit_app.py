import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG & FONT ----
st.set_page_config(layout="wide", page_title="Growth Stock Dashboard")

st.markdown("""
    <style>
        /* Import custom font */
        @import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');

        /* Global layout: app body, sidebar, block content */
        html, body, .stApp, .block-container, .sidebar .sidebar-content {
            font-family: 'Lato', sans-serif;
            background-color: #EAEDED !important;
            color: #283747 !important;
        }

        /* Headings */
        h1, h2, h3, h4 {
            color: #283747 !important;
        }

        /* Sidebar area */
        section[data-testid="stSidebar"] {
            background-color: #BFC9CA !important;
        }

        /* Top menu bar */
        header[data-testid="stHeader"] {
            background-color: #EAEDED !important;
            color: #283747 !important;
        }

        /* Data editor/table background */
        .stDataFrame, .stDataEditor {
            background-color: #FAD7A0 !important;
            color: #283747 !important;
        }

        /* Fix editor scrollable inner div background */
        .stDataFrame .css-1siy2j7, .stDataEditor .css-1siy2j7 {
            background-color: #BFC9CA !important;
        }

        /* Button styling (e.g. Restore button) */
        button[kind="secondary"] {
            background-color: #BFC9CA !important;   /* Tailwind blue-600 */
            color: 283747 !important;
            border-radius: 6px !important;
            padding: 0.5em 1em !important;
            border: none !important;
        }
        button[kind="secondary"]:hover {
            background-color: #BFC9CA !important;
        }

        /* Field input color */
        .stNumberInput input, .stSlider .st-c2 {
            background-color: #BFC9CA !important;
            color: #283747 !important;
        }

        /* Slider track styling */
        .stSlider > div[data-baseweb="slider"] {
            background-color: #e0e7ff !important;
        }

        /* Dropdowns / multiselects */
        .stSelectbox, .stMultiSelect {
            background-color: #BFC9CA !important;
        }

    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
df = pd.read_csv("mock_stock_data.csv")

# ---- INIT STATE ----
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()
if "restored" not in st.session_state:
    st.session_state.restored = False

# ---- SIDEBAR ----
with st.sidebar:
    st.title("📊 Filters + Smart Score")

    st.subheader("Smart Score Weights")
    peg_w = st.slider("PEG", 0.0, 1.0, 0.2)
    eps_w = st.slider("EPS Growth", 0.0, 1.0, 0.15)
    rating_w = st.slider("Analyst Rating", 0.0, 1.0, 0.2)
    target_w = st.slider("Target Upside", 0.0, 1.0, 0.15)
    sentiment_w = st.slider("Sentiment", 0.0, 1.0, 0.15)
    insider_w = st.slider("Insider Depth", 0.0, 1.0, 0.15)

    # Normalize
    total = peg_w + eps_w + rating_w + target_w + sentiment_w + insider_w
    peg_w /= total
    eps_w /= total
    rating_w /= total
    target_w /= total
    sentiment_w /= total
    insider_w /= total

    # Donut chart
    labels = ["PEG", "EPS", "Rating", "Upside", "Sentiment", "Insider"]
    sizes = [peg_w, eps_w, rating_w, target_w, sentiment_w, insider_w]
    colors = ['#7fb3d5', '#85c1e9', '#76d7c4', '#73c6b6', '#7dcea0','7dcea0']
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, startangle=140,
           autopct='%1.0f%%', pctdistance=0.85, wedgeprops=dict(width=0.3))
    ax.axis('equal')
    st.pyplot(fig)

    # Filters
    st.subheader("Fundamental Filters")
    pe_filter = st.checkbox("Enable PE", value=True)
    pe_min = st.number_input("Min PE", value=0.0)
    pe_max = st.number_input("Max PE", value=30.0)

    peg_filter = st.checkbox("Enable PEG", value=True)
    peg_max = st.slider("Max PEG", 0.0, 5.0, 1.5)

    eps_filter = st.checkbox("Enable EPS Growth", value=True)
    eps_min = st.slider("Min EPS Growth", 0, 100, 20)

    analyst_filter = st.checkbox("Enable Analyst Rating")
    rating_max = st.slider("Max Analyst Rating", 1.0, 5.0, 3.0)

    target_filter = st.checkbox("Enable Target Upside")
    target_min = st.slider("Min Upside (%)", 0, 200, 30)

    insider_filter = st.checkbox("Enable Insider Filter")
    allowed = st.multiselect("Allowed Activities", ["Heavy Buying", "Net Buying"], default=["Heavy Buying"])

    apply_filters = st.button("Apply Filters")

# ---- SMART SCORE ----
df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * peg_w +
    df["EPS_Growth"] * eps_w +
    (5 - df["AnalystRating"]) * rating_w +
    df["TargetUpside"] * target_w +
    df["SentimentScore"] * sentiment_w +
    df["InsiderDepth"] * insider_w
)

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
st.title("🚀 Undervalued Growth Stocks: Dashboard")

if st.button("Restore All Hidden Rows"):
    st.session_state.hidden_rows.clear()
    st.session_state.restored = True

if st.session_state.restored:
    st.success("All rows restored.")
    st.session_state.restored = False

if not filtered.empty:
    display_df = filtered.copy()
    display_df = display_df[[
        "Ticker", "Price", "PE", "PEG", "EPS_Growth", "AnalystRating",
        "TargetUpside", "SentimentScore", "InsiderDepth", "SmartScore"
    ]]
    display_df = display_df.sort_values("SmartScore", ascending=False)

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
