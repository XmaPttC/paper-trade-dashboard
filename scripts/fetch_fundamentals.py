import requests
import csv
import boto3
import os
from datetime import datetime

EODHD_API_KEY = os.environ["EODHD_API_KEY"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
BUCKET_NAME = "stock-screener-output-beta"
EXCHANGES = ["US", "NASDAQ"]

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
s3 = session.client("s3")

def get_exchange_tickers(exchange_code):
    url = f"https://eodhistoricaldata.com/api/exchange-symbol-list/{exchange_code}?api_token={EODHD_API_KEY}&fmt=json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return [d for d in data if d.get("Type") == "Common Stock"]

def fetch_fundamentals(ticker):
    url = f"https://eodhistoricaldata.com/api/fundamentals/{ticker}?api_token={EODHD_API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        highlights = data.get("Highlights", {})
        market_cap = highlights.get("MarketCapitalization")
        pe = highlights.get("PERatio")
        peg = highlights.get("PEGRatio")
        eps_growth = highlights.get("EPSGrowth")
        return {
            "ticker": ticker,
            "market_cap": float(market_cap) if market_cap else None,
            "pe": float(pe) if pe else None,
            "peg": float(peg) if peg else None,
            "eps_growth": float(eps_growth) if eps_growth else None
        }
    except Exception:
        return None

def main():
    all_tickers = []
    for exch in EXCHANGES:
        all_tickers += get_exchange_tickers(exch)

    filtered = []
    for t in all_tickers:
        ticker = t["Code"] + ".US"
        fundamentals = fetch_fundamentals(ticker)
        if not fundamentals:
            continue
        if fundamentals["market_cap"] and fundamentals["market_cap"] >= 300_000_000:
            filtered.append(fundamentals)

    if not filtered:
        print("❌ No records collected.")
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"eodhd-fundamentals/{today}.csv"

    with open("/tmp/fundamentals.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=filtered[0].keys())
        writer.writeheader()
        writer.writerows(filtered)

    s3.upload_file("/tmp/fundamentals.csv", BUCKET_NAME, filename)
    print(f"✅ Uploaded {len(filtered)} records to s3://{BUCKET_NAME}/{filename}")

if __name__ == "__main__":
    main()
