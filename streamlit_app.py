import streamlit as st
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import os

st.set_page_config(page_title="Paper Trading Dashboard", layout="wide")
st.title("📈 Paper Trading Simulator")

st.markdown("""
### 📋 Strategy Overview

- **Screener**: [Yahoo Finance “Undervalued Growth Stocks”](https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks)
- **Upside Filter**: Target price must be at least **25% above** the current market price
""")

# Load AWS credentials from Streamlit secrets
aws_access_key = st.secrets["aws_access_key_id"]
aws_secret_key = st.secrets["aws_secret_access_key"]
aws_region = st.secrets["aws_region"]

# Connect to DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

table = dynamodb.Table("paper_trades")

# Query all items
response = table.scan()
items = response.get("Items", [])

# Show summary
st.subheader(f"🗂️ {len(items)} Total Trades")
status_filter = st.selectbox("Filter by trade status", options=["All", "open", "closed"])

# Apply filter
if status_filter != "All":
    items = [item for item in items if item["status"] == status_filter]

# Convert Decimal to float for display
for item in items:
    for key in ["entry_price", "target_price", "stop_loss"]:
        if isinstance(item.get(key), Decimal):
            item[key] = float(item[key])

# Display table
import pandas as pd

if items:
    # Convert to DataFrame
    df = pd.DataFrame(items)

    # Add Yahoo Finance link to ticker
    df["ticker"] = df["ticker"].apply(
        lambda t: f"[{t}](https://finance.yahoo.com/quote/{t})"
    )

    # Select and reorder columns
    column_order = ["ticker", "entry_price", "entry_date", "target_price", "stop_loss", "status"]
    df = df[[col for col in column_order if col in df.columns]]

    # Display with links enabled
    st.markdown("### 📋 Trade Data")
    st.write(df.to_markdown(index=False), unsafe_allow_html=True)
else:
    st.info("No trades found.")
