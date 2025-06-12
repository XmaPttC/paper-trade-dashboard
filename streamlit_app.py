import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG & FONT ----
st.set_page_config(layout="wide", page_title="Growth Stock Screener")

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Lato', sans-serif;
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

# ---- SIDEBAR FILTERS ----
with st.sidebar:
    st.title("📊 Filters + Smart Score")

    st.subheader("Smart Score Weights")
    peg_w = st.slider("PEG weight", 0.0, 1.0, 0.3)
    eps_w = st.slider("EPS Growth weight", 0.0, 1.0, 0.2)
    rating_w = st.slider("Analyst Rating weight", 0.0, 1.0, 0.3)
    target_w = st.slider("Target Upside weight", 0.0, 1.0, 0.2)

    # Normalize weights
    total_w = peg_w + eps_w + rating_w + target_w
    if total_w == 0: total_w = 1.0
    peg_w /= total_w
    eps_w /= total_w
    rating_w /= total_w
    target_w /= total_w

    # Visualize donut chart
    labels = ["PEG", "EPS Growth", "Rating", "Upside"]
    sizes = [peg_w, eps_w, rating_w, target_w]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, startangle=140,
           autopct='%1.0f%%', pctdistance=0.85, wedgeprops=dict(width=0.3))
    ax.axis('equal')
    st.pyplot(fig)

    # Core Filters
    st.subheader("Core Filters")
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

# ---- SMART SCORE COMPUTATION ----
df["SmartScore"] = (
    (1 / df["PEG"].clip(lower=0.01)) * peg_w +
    df["EPS_Growth"] * eps_w +
    (5 - df["AnalystRating"]) * rating_w +
    df["TargetUpside"] * target_w
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

# ---- HIDE ROWS ----
filtered = filtered[~filtered["Ticker"].isin(st.session_state.hidden_rows)]

# ---- MAIN PANEL ----
st.title("🚀 Undervalued Growth Stock Screener")

if st.button("Restore All Hidden Rows"):
    st.session_state.hidden_rows.clear()
    st.session_state.restored = True

if st.session_state.restored:
    st.success("All rows restored.")
    st.session_state.restored = False

if not filtered.empty:
    display_df = filtered.copy()
    display_df["Ticker"] = display_df.apply(
        lambda row: f"[{row['Ticker']}]({row['YahooFinanceLink']})", axis=1
    )
    display_df = display_df[[
        "Ticker", "Price", "PE", "PEG", "EPS_Growth", "AnalystRating",
        "TargetUpside", "SmartScore", "InsiderActivity"
    ]]
    display_df = display_df.sort_values("SmartScore", ascending=False)

    edited_df = st.data_editor(
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
            "TargetUpside": st.column_config.NumberColumn(format="%.0f%%")
        },
        disabled=["Ticker"]
    )

    for ticker in filtered["Ticker"]:
        col1, col2, _ = st.columns([3, 1, 5])
        col1.markdown(f"**{ticker}**")
        if col2.button(f"🙈 Hide {ticker}", key=f"hide_{ticker}"):
            st.session_state.hidden_rows.add(ticker)
            st.experimental_rerun()
else:
    st.warning("No stocks matched your filters or all have been hidden.")
