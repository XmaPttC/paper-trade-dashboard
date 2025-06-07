import streamlit as st
import boto3
import os
import pandas as pd
import csv
from io import StringIO
from datetime import datetime
from decimal import Decimal

# Read credentials from Streamlit secrets
AWS_REGION = st.secrets["AWS_DEFAULT_REGION"]
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

s3 = session.client("s3")
dynamodb = session.resource("dynamodb")
table = dynamodb.Table("paper_trades")

# ---------- CONSTANTS ----------
BUCKET = "stock-screener-output-beta"
TODAY_KEY = "yahoo-results/2025-06-06.csv"  # or any known file

# ---------- HELPERS ----------
def load_screener_data():
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=TODAY_KEY)
        csv_data = obj["Body"].read().decode("utf-8")
        reader = csv.DictReader(StringIO(csv_data))
        return list(reader)
    except Exception as e:
        st.error(f"⚠️ Failed to load screener data: {e}")
        return []

def add_trade(ticker, price, target):
    try:
        if table.get_item(Key={"ticker": ticker}).get("Item"):
            return False
        entry_price = float(price)
        target_price = float(target)
        stop_loss = round(entry_price * 0.8, 2)
        table.put_item(Item={
            "ticker": ticker,
            "entry_price": Decimal(str(entry_price)),
            "target_price": Decimal(str(target_price)),
            "stop_loss": Decimal(str(stop_loss)),
            "entry_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "status": "open"
        })
        return True
    except Exception as e:
        st.error(f"❌ Failed to add trade: {e}")
        return False

def load_trades():
    try:
        return table.scan().get("Items", [])
    except Exception as e:
        st.error(f"⚠️ Failed to load trades: {e}")
        return []

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Stock Screener & Simulator", layout="wide")
st.title("📈 Stock Screener + Paper Trading Dashboard")

tab1, tab2 = st.tabs(["📊 Screener", "📘 Trading Simulation"])

# ---------- TAB 1: Screener ----------
with tab1:
    st.subheader("📊 Undervalued Growth Stocks")
    screener_data = load_screener_data()

    if screener_data:
        for row in screener_data:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            with col1:
                st.markdown(f"[{row['ticker']}](https://finance.yahoo.com/quote/{row['ticker']})")
            with col2:
                st.markdown(f"Price: **{row['price']}**")
            with col3:
                st.markdown(f"Target: **{row['target']}**")
            with col4:
                try:
                    price, target = float(row["price"]), float(row["target"])
                    upside = round((target - price) / price * 100, 1)
                    st.markdown(f"Upside: **{upside}%**")
                except:
                    st.markdown("Upside: —")
            with col5:
                if st.button("Add to Trading Simulation", key=row["ticker"]):
                    added = add_trade(row["ticker"], row["price"], row["target"])
                    if added:
                        st.success(f"✅ {row['ticker']} added.")
                    else:
                        st.warning(f"⚠️ {row['ticker']} already exists.")

    else:
        st.info("No screener data available for today.")

# ---------- TAB 2: Simulated Trades ----------
with tab2:
    st.subheader("📘 Simulated Trades")
    items = load_trades()

    if items:
        df = pd.DataFrame(items)
        for col in ["entry_price", "target_price", "stop_loss", "exit_price"]:
            if col in df.columns:
                df[col] = df[col].astype(float)

        if "exit_price" in df.columns and "status" in df.columns:
            df["exit_date"] = df.get("exit_date", "")
            df["pnl"] = df.apply(
                lambda row: row["exit_price"] - row["entry_price"]
                if row["status"].startswith("closed") and pd.notnull(row["exit_price"])
                else None,
                axis=1,
            )

        df["ticker"] = df["ticker"].apply(
            lambda t: f"[{t}](https://finance.yahoo.com/quote/{t})"
        )

        columns = ["ticker", "entry_price", "entry_date", "target_price", "stop_loss", "status", "exit_date", "pnl"]
        df = df[[col for col in columns if col in df.columns]]

        st.markdown("### 🧾 Trade Log")
        st.write(df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("No trades found.")
