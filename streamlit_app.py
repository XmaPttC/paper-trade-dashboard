import streamlit as st
import boto3
import pandas as pd
from datetime import datetime
from io import StringIO
import json
import os

# Force AWS region to avoid NoRegionError
boto3.setup_default_session(region_name="us-east-1")

# AWS clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("PaperTrades")

# Constants
BUCKET_NAME = "stock-screener-output-beta"
S3_KEY_PREFIX = "finnhub-results"
TODAY = datetime.utcnow().strftime("%Y-%m-%d")

# Load screener data
def load_screener_data():
    try:
        key = f"{S3_KEY_PREFIX}/{TODAY}.csv"
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        df = pd.read_csv(response["Body"])
        return df
    except Exception as e:
        st.error(f"Failed to load screener data: {e}")
        return pd.DataFrame()

# Add a trade to DynamoDB
def add_trade(ticker, price, target):
    try:
        trade = {
            "ticker": ticker,
            "entry_price": str(price),
            "target_price": str(target),
            "stop_loss": str(round(price * 0.8, 2)),
            "entry_date": TODAY,
            "status": "open"
        }
        table.put_item(Item=trade)
        st.success(f"Added {ticker} to simulation.")
    except Exception as e:
        st.error(f"Failed to add trade: {e}")

# Load existing trades
def load_trades():
    try:
        response = table.scan()
        return pd.DataFrame(response.get("Items", []))
    except Exception as e:
        st.error(f"Failed to load trades: {e}")
        return pd.DataFrame()

# Dashboard layout
st.title("📊 Stock Screener & Paper Trading Simulator")

tabs = st.tabs(["🧪 Screener", "💼 Trading Simulation"])

# Screener tab
with tabs[0]:
    st.subheader("🧪 Screener Results")
    st.markdown("**Source:** Finnhub API<br>**Criteria:** Market Cap > $300M, P/E < 15, PEG < 1, EPS Growth > 20%", unsafe_allow_html=True)

    screener_df = load_screener_data()
    if not screener_df.empty:
        for idx, row in screener_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            ticker = row["ticker"]
            link = f"https://finance.yahoo.com/quote/{ticker}"
            col1.markdown(f"[{ticker}]({link})")
            col2.write(f"${row['price']:.2f}")
            col3.write(f"Target: ${row['target']:.2f}" if "target" in row else "N/A")
            if col4.button("Add to Trading Simulation", key=f"add_{ticker}"):
                add_trade(ticker, float(row["price"]), float(row.get("target", row["price"] * 1.25)))
    else:
        st.info("No screener data available for today.")

# Trading Simulation tab
with tabs[1]:
    st.subheader("💼 Simulated Trades")
    trades_df = load_trades()
    if not trades_df.empty:
        trades_df = trades_df[["ticker", "entry_price", "entry_date", "target_price", "stop_loss", "status"]]
        trades_df["yahoo_link"] = trades_df["ticker"].apply(lambda x: f"https://finance.yahoo.com/quote/{x}")
        trades_df["ticker"] = trades_df.apply(lambda row: f"[{row['ticker']}]({row['yahoo_link']})", axis=1)
        trades_df.drop(columns=["yahoo_link"], inplace=True)
        st.markdown(trades_df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("No trades have been simulated yet.")
