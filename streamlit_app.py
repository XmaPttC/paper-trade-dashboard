import streamlit as st
import pandas as pd
import boto3
from datetime import datetime

# --- S3 CONFIG ---
BUCKET_NAME = "stock-screener-output-beta"
FOLDER = "finnhub-results"
REGION = "us-east-1"

# --- Load Data from S3 ---
@st.cache_data
def load_data():
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{FOLDER}/{today}.csv"
    s3 = boto3.client("s3", region_name=REGION)
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        df = pd.read_csv(obj["Body"])
        return df
    except Exception as e:
        st.error(f"Failed to load screener data: {e}")
        return pd.DataFrame()

# --- Initialize Session State ---
for var in ["show_filters", "show_popup", "filtered_df", "apply_filters"]:
    if var not in st.session_state:
        st.session_state[var] = False if "show" in var else None

# --- Title ---
st.title("📊 Stock Screener")

# --- Load Data ---
df = load_data()
if df.empty:
    st.info("No screener data available for today.")
    st.stop()

# --- Default Filter Values ---
DEFAULTS = {
    "pe_max": 15.0,
    "peg_max": 1.0,
    "eps_min": 20.0
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Filter Area ---
with st.expander("🔍 Filters"):
    st.button("Apply Standard Filters", on_click=lambda: st.session_state.update({
        "pe_max": DEFAULTS["pe_max"],
        "peg_max": DEFAULTS["peg_max"],
        "eps_min": DEFAULTS["eps_min"],
        "apply_filters": True
    }))

    if st.toggle("Change Standard Filters", key="show_popup"):
        st.markdown("### Customize Standard Filters")
        st.session_state["pe_max"] = st.slider("Max P/E Ratio", 0.0, 100.0, st.session_state["pe_max"])
        st.session_state["peg_max"] = st.slider("Max PEG Ratio", 0.0, 5.0, st.session_state["peg_max"])
        st.session_state["eps_min"] = st.slider("Min EPS Growth (%)", 0.0, 100.0, st.session_state["eps_min"])
        if st.button("Apply Custom Filters"):
            st.session_state["apply_filters"] = True
            st.session_state["show_popup"] = False

# --- Apply Filters ---
if st.session_state.get("apply_filters"):
    df = df[
        (df["pe"] <= st.session_state["pe_max"]) &
        (df["peg"] <= st.session_state["peg_max"]) &
        (df["eps_growth"] >= st.session_state["eps_min"])
    ]
    st.session_state["apply_filters"] = False

# --- Table Display ---
st.markdown("### Filtered Stocks")

def make_yahoo_link(ticker):
    return f"[{ticker}](https://finance.yahoo.com/quote/{ticker})"

df_display = df.copy()
df_display["ticker"] = df_display["ticker"].apply(make_yahoo_link)

st.dataframe(df_display[['ticker', 'price', 'pe', 'peg', 'eps_growth']], use_container_width=True)
