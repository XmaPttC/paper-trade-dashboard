import streamlit as st
import pandas as pd
import datetime

# ---------- Setup ----------
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.markdown(
    """
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 6px;
        padding: 0.4rem 1.2rem;
    }
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Session State ----------
if "filters" not in st.session_state:
    st.session_state.filters = {
        "pe": (0, 40),
        "peg": (0.0, 2.0),
        "eps": (10, 100),
        "market_cap": (300, 100000)
    }

if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()

# ---------- Dummy Data ----------
def load_dummy_data():
    return pd.DataFrame([
        {"ticker": "AAPL", "price": 180.5, "pe": 29, "peg": 1.3, "eps": 12.1, "market_cap": 2500},
        {"ticker": "TSLA", "price": 195.1, "pe": 72, "peg": 2.5, "eps": 80.5, "market_cap": 600},
        {"ticker": "NVDA", "price": 430.3, "pe": 35, "peg": 1.8, "eps": 65.3, "market_cap": 1000},
        {"ticker": "ZM", "price": 62.7, "pe": 22, "peg": 1.0, "eps": 25.4, "market_cap": 400},
    ])

# ---------- Filter Logic ----------
def filter_dataframe(df):
    f = st.session_state.filters
    return df[
        (df["pe"].between(*f["pe"])) &
        (df["peg"].between(*f["peg"])) &
        (df["eps"].between(*f["eps"])) &
        (df["market_cap"].between(*f["market_cap"]))
    ]

# ---------- UI Layout ----------
tab1, tab2 = st.tabs(["📊 Stock Screener", "📈 Trading Simulation"])

# ---------- Tab 1: Screener ----------
with tab1:
    st.title("📊 Stock Screener")

    with st.expander("🔧 Filter Settings", expanded=False):
        st.write("Use these controls to filter the stock list:")

        col1, col2 = st.columns(2)
        st.session_state.filters["pe"] = col1.slider("PE Ratio", 0, 100, st.session_state.filters["pe"])
        st.session_state.filters["peg"] = col2.slider("PEG Ratio", 0.0, 5.0, st.session_state.filters["peg"])

        col3, col4 = st.columns(2)
        st.session_state.filters["eps"] = col3.slider("EPS Growth (%)", 0, 150, st.session_state.filters["eps"])
        st.session_state.filters["market_cap"] = col4.slider("Market Cap ($M)", 100, 10000, st.session_state.filters["market_cap"])

        st.markdown("---")

    df = load_dummy_data()
    df = filter_dataframe(df)
    df = df[~df["ticker"].isin(st.session_state.hidden_rows)]

    if df.empty:
        st.warning("No results match your filters.")
    else:
        for idx, row in df.iterrows():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1.5, 1.5, 1, 1])

            ticker_link = f"https://finance.yahoo.com/quote/{row['ticker']}"
            c1.markdown(f"[{row['ticker']}]({ticker_link})")
            c2.write(f"${row['price']:.2f}")
            c3.write(f"PE: {row['pe']}")
            c4.write(f"PEG: {row['peg']}")
            c5.write(f"EPS: {row['eps']}%")
            c6.write(f"{row['market_cap']}B")

            if c7.button("👁️", key=f"hide_{row['ticker']}"):
                st.session_state.hidden_rows.add(row["ticker"])
                st.experimental_rerun()

        if st.button("🔄 Show All Hidden Rows"):
            st.session_state.hidden_rows.clear()
            st.experimental_rerun()

# ---------- Tab 2: Placeholder ----------
with tab2:
    st.title("📈 Trading Simulation")
    st.info("This section will display all simulated trades. Coming soon!")
