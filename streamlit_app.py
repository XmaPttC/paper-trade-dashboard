import streamlit as st
from datetime import datetime

# Set wide layout
st.set_page_config(layout="wide", page_title="Terminal")

# Dummy mock data for 5 tickers
mock_data = [
    {"Ticker": "AAPL", "Price": 195.2, "SmartScore": 84.5, "PEG": 1.2, "PE": 24.1, "EPSGrowth": 18,
     "MarketCap": "3.12T", "30DayVol": "75M", "AnalystRating": 2.2, "TargetUpside": 15,
     "Sector": "Technology", "InsiderDepth": 0.60, "SentimentScore": 0.72, "RedditSentiment": 0.42, "HiLoProximity": "92%"},
    {"Ticker": "MSFT", "Price": 341.7, "SmartScore": 88.9, "PEG": 1.3, "PE": 31.2, "EPSGrowth": 22,
     "MarketCap": "2.89T", "30DayVol": "65M", "AnalystRating": 1.9, "TargetUpside": 18,
     "Sector": "Technology", "InsiderDepth": 0.45, "SentimentScore": 0.81, "RedditSentiment": 0.58, "HiLoProximity": "88%"},
    {"Ticker": "GOOGL", "Price": 138.4, "SmartScore": 81.0, "PEG": 1.5, "PE": 26.5, "EPSGrowth": 20,
     "MarketCap": "1.87T", "30DayVol": "52M", "AnalystRating": 2.4, "TargetUpside": 12,
     "Sector": "Communication", "InsiderDepth": 0.30, "SentimentScore": 0.64, "RedditSentiment": 0.47, "HiLoProximity": "85%"},
    {"Ticker": "AMZN", "Price": 132.8, "SmartScore": 76.4, "PEG": 2.1, "PE": 48.2, "EPSGrowth": 30,
     "MarketCap": "1.72T", "30DayVol": "48M", "AnalystRating": 2.8, "TargetUpside": 22,
     "Sector": "Consumer", "InsiderDepth": 0.20, "SentimentScore": 0.70, "RedditSentiment": 0.62, "HiLoProximity": "89%"},
    {"Ticker": "NVDA", "Price": 795.1, "SmartScore": 92.3, "PEG": 1.0, "PE": 52.4, "EPSGrowth": 45,
     "MarketCap": "2.23T", "30DayVol": "55M", "AnalystRating": 1.5, "TargetUpside": 25,
     "Sector": "Technology", "InsiderDepth": 0.55, "SentimentScore": 0.90, "RedditSentiment": 0.78, "HiLoProximity": "95%"},
]

# Table rows
table_rows = ""
for row in mock_data:
    ticker = row['Ticker']
    link = f"https://finance.yahoo.com/quote/{ticker}"
    table_rows += f"""
    <tr>
        <td><a href="{link}" target="_blank">{ticker}</a></td>
        <td>${row['Price']}</td>
        <td>{row['SmartScore']}</td>
        <td>{row['PEG']}</td>
        <td>{row['PE']}</td>
        <td>{row['EPSGrowth']}%</td>
        <td>{row['MarketCap']}</td>
        <td>{row['30DayVol']}</td>
        <td>{row['AnalystRating']}</td>
        <td>{row['TargetUpside']}%</td>
        <td>{row['Sector']}</td>
        <td>{row['InsiderDepth']}</td>
        <td>{row['SentimentScore']}</td>
        <td>{row['RedditSentiment']}</td>
        <td>{row['HiLoProximity']}</td>
    </tr>
    """

# Info header
st.title("Terminal")
st.markdown(f"""
<div style='display: flex; gap: 20px; margin-bottom: 6px;'>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Total Results:</strong> {len(mock_data)}</div>
  <div style='border:1px solid #ccc; font-size: 10px; padding:4px 8px;'><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
<hr style='border-top: 1px solid #ccc; margin-bottom: 8px;' />
""", unsafe_allow_html=True)

# Render table
st.markdown(f"""
<style>
    .custom-table {{
        font-family: 'Lato', sans-serif;
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
    }}
    .custom-table th {{
        background-color: #1e293b;
        color: #f1f5f9;
        padding: 8px;
        text-align: left;
    }}
    .custom-table td {{
        background-color: #3d5975;
        color: #f1f5f9;
        padding: 6px;
    }}
    .custom-table tr:nth-child(even) td {{
        background-color: #466686;
    }}
    .custom-table tr:hover td {{
        background-color: #64748b;
    }}
    a {{
        color: #93c5fd;
        text-decoration: none;
    }}
    a:hover {{
        text-decoration: underline;
    }}
</style>

<table class="custom-table">
<thead>
<tr>
    <th>Ticker</th><th>Price</th><th>SmartScore</th><th>PEG</th><th>PE</th><th>EPSGrowth</th>
    <th>MarketCap</th><th>30DayVol</th><th>AnalystRating</th><th>TargetUpside</th>
    <th>Sector</th><th>InsiderDepth</th><th>SentimentScore</th>
    <th>RedditSentiment</th><th>HiLoProximity</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
""", unsafe_allow_html=True)
