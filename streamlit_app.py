import streamlit as st
import boto3
import pandas as pd

# Force region to avoid NoRegionError
boto3.setup_default_session(region_name="us-east-1")

# Constants
BUCKET_NAME = "stock-screener-output-beta"
KEY = "finnhub-results/2025-06-08.csv"

# Set up S3 client
s3 = boto3.client("s3")

# Title
st.title("🔍 S3 CSV Viewer")

# Try to load and display the CSV
try:
    st.write(f"Fetching from: `s3://{BUCKET_NAME}/{KEY}`")

    response = s3.get_object(Bucket=BUCKET_NAME, Key=KEY)
    df = pd.read_csv(response["Body"])

    st.success(f"✅ Loaded {len(df)} rows from CSV!")
    st.dataframe(df)

except Exception as e:
    st.error(f"❌ Failed to load CSV:\n\n{e}")
