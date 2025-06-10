import streamlit as st
import pandas as pd

# ---------- Setup ----------
st.set_page_config(page_title="Stock Screener", layout="wide")
st.markdown(
    """
    <style>
        .main { background-color: #f5f7fa; }
        .title { font-size: 40px; font-weight: 700; color: #203656; }
        .filter-box { background-color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; }
        .table-box { background-color: white; padding: 1rem; border-radius: 10px; }
        .btn { border-radius: 5px; padding: 0.25rem 0.75rem; font-size: 14px; }
        .ticker-link { font-weight: 600; color: #1a73e8; text-decoration: none; }
        .ticker-link:hover { text-decoration: underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Dummy Data ----------
df = pd.DataFrame([
    {"ticker": "AAPL", "price": 189.75, "pe": 29.1, "peg": 2.2, "eps": 12.5, "market_cap": 2.9e12},
    {"ticker": "MSFT", "price": 324.00, "pe": 32.0, "peg": 2.0, "eps": 15.2, "market_cap": 2.6e12},
    {"ticker": "NVDA", "price": 109.82, "pe": 55.3, "peg": 1.5, "eps": 27.3, "market_cap": 1.1e12},
    {"ticker": "GOOG", "price": 132.55, "pe": 28.4, "peg": 1.3, "eps": 8.2, "market_cap": 1.9e12},
])

if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()

if "filters" not in st.session_state:
    st.session_state.filters = {"pe": 100, "peg": 5.0, "eps": 0.0, "market_cap": 0.0}


# ---------- Title ----------
st.markdown('<h1 class="title">📊 Stock Screener Dashboard</h1>', unsafe_allow_html=True)


# ---------- Filters ----------
with st.container():
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    st.subheader("Filters")

    col1, col2, col3, col4 = st.columns(4)

    pe = col1.slider("Max PE", 0, 100, st.session_state.filters["pe"])
    peg = col2.slider("Max PEG", 0.0, 5.0, st.session_state.filters["peg"])
    eps = col3.slider("Min EPS Growth (%)", 0.0, 50.0, st.session_state.filters["eps"])
    market_cap = col4.slider("Min Market Cap (B)", 0.0, 5.0, st.session_state.filters["market_cap"] / 1e9)

    if st.button("Apply Filters"):
        st.session_state.filters = {
            "pe": pe,
            "peg": peg,
            "eps": eps,
            "market_cap": market_cap * 1e9
        }
    st.markdown('</div>', unsafe_allow_html=True)


# ---------- Table ----------
st.markdown('<div class="table-box">', unsafe_allow_html=True)

filtered_df = df[
    (df["pe"] <= st.session_state.filters["pe"]) &
    (df["peg"] <= st.session_state.filters["peg"]) &
    (df["eps"] >= st.session_state.filters["eps"]) &
    (df["market_cap"] >= st.session_state.filters["market_cap"])
].copy()

# Exclude hidden rows
filtered_df = filtered_df[~filtered_df["ticker"].isin(st.session_state.hidden_rows)]

if filtered_df.empty:
    st.warning("No stocks match your criteria.")
else:
    for _, row in filtered_df.iterrows():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 2, 1, 1])
        col1.markdown(f'<a class="ticker-link" href="https://finance.yahoo.com/quote/{row["ticker"]}" target="_blank">{row["ticker"]}</a>', unsafe_allow_html=True)
        col2.write(f"${row['price']:.2f}")
        col3.write(f"{row['pe']:.1f}")
        col4.write(f"{row['peg']:.1f}")
        col5.write(f"{row['eps']:.1f}%")
        col6.button("👁️‍🗨️", key=f"hide_{row['ticker']}", help="Hide row")
        col7.button("➕", key=f"add_{row['ticker']}", help="Add to Trading Bot")

        if st.session_state.get(f"hide_{row['ticker']}", False):
            st.session_state.hidden_rows.add(row["ticker"])

st.markdown('</div>', unsafe_allow_html=True)
