import streamlit as st
import pandas as pd
import boto3
import io
from datetime import datetime

st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("📊 Undervalued Growth Stock Screener")

# --- Utility Functions ---
def get_today_key():
    return f"finnhub-results/{datetime.now().strftime('%Y-%m-%d')}.csv"

def format_market_cap(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.0f}M"
        else:
            return str(int(value))
    except:
        return "N/A"

def load_screener_data():
    try:
        s3 = boto3.client("s3")
        bucket = "stock-screener-output-beta"
        key = get_today_key()
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(response["Body"].read()))
        return df
    except Exception as e:
        st.error(f"Failed to load screener data: {e}")
        return pd.DataFrame()

# --- UI State Initialization ---
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()
if "filters" not in st.session_state:
    st.session_state.filters = {
        "pe": (0.0, 30.0),
        "peg": (0.0, 2.0),
        "eps_growth": (10.0, 100.0)
    }

# --- Filter Controls ---
with st.expander("🔧 Filter Stocks", expanded=True):
    st.markdown("**Apply filters by adjusting sliders or typing values**")

    pe_min, pe_max = st.slider("P/E Ratio", 0.0, 100.0, st.session_state.filters["pe"], step=1.0)
    peg_min, peg_max = st.slider("PEG Ratio", 0.0, 5.0, st.session_state.filters["peg"], step=0.1)
    eps_min, eps_max = st.slider("EPS Growth %", 0.0, 200.0, st.session_state.filters["eps_growth"], step=1.0)

    if st.button("Apply Filters"):
        st.session_state.filters = {
            "pe": (pe_min, pe_max),
            "peg": (peg_min, peg_max),
            "eps_growth": (eps_min, eps_max)
        }

# --- Load and Filter Data ---
df = load_screener_data()
if not df.empty:
    # Clean and format
    df["market_cap"] = df["market_cap"].apply(format_market_cap)
    df = df.dropna(subset=["ticker", "price", "pe", "peg", "eps_growth"])

    # Convert types
    df["pe"] = df["pe"].astype(float)
    df["peg"] = df["peg"].astype(float)
    df["eps_growth"] = df["eps_growth"].astype(float)

    # Apply filters
    filters = st.session_state.filters
    df_filtered = df[
        (df["pe"].between(*filters["pe"])) &
        (df["peg"].between(*filters["peg"])) &
        (df["eps_growth"].between(*filters["eps_growth"]))
    ]

    # Apply hidden row filter
    df_filtered = df_filtered[~df_filtered["ticker"].isin(st.session_state.hidden_rows)]

    # Sortable table headers
    sort_column = st.selectbox("Sort by", ["ticker", "price", "pe", "peg", "eps_growth"])
    df_filtered = df_filtered.sort_values(by=sort_column)

    st.markdown("### Filtered Stocks")
    for _, row in df_filtered.iterrows():
        cols = st.columns([2, 2, 2, 2, 2, 2, 1, 1])
        link = f"https://finance.yahoo.com/quote/{row['ticker']}"
        cols[0].markdown(f"[{row['ticker']}]({link})")
        cols[1].write(f"${row['price']:.2f}")
        cols[2].write(f"{row['pe']:.1f}")
        cols[3].write(f"{row['peg']:.2f}")
        cols[4].write(f"{row['eps_growth']:.1f}%")
        cols[5].write(row["market_cap"])
        if cols[6].button("👁️", key=f"hide_{row['ticker']}"):
            st.session_state.hidden_rows.add(row["ticker"])
            st.experimental_rerun()
        if cols[7].button("➕", key=f"add_{row['ticker']}"):
            st.success(f"{row['ticker']} added to simulation (dummy)")

    if st.button("🔄 Show All Hidden Rows"):
        st.session_state.hidden_rows.clear()
        st.success("All rows restored!")
        st.experimental_rerun()
else:
    st.info("No screener data available for today.")
