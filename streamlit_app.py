import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Terminal")

# --- Sample Data ---
data = {
    "Ticker": ["AAPL", "MSFT", "GOOGL"],
    "Price": [192.3, 338.1, 142.8],
    "TerminalScore": [78.2, 80.4, 76.1],
    "PEG": [1.25, 1.19, 1.45],
    "PE": [28.5, 32.3, 27.9],
    "EPSGr": [15.2, 13.6, 14.3],
    "MktCap": [2.7e12, 2.8e12, 1.85e12],
    "30DayVol": [125e6, 180e6, 145e6],
    "AnalystSc": [2.1, 2.0, 2.4],
    "TrgtUpside": [18.5, 15.2, 22.4],
    "Sector": ["Technology", "Technology", "Technology"],
    "InsiderSc": [0.72, 0.68, 0.63],
    "SentSc": [0.61, 0.59, 0.55],
    "RedditSc": [0.74, 0.70, 0.62],
    "52wH": [91, 88, 85]
}
df = pd.DataFrame(data)

# --- CSS Styling ---
st.markdown("""
<style>
.custom-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.custom-table th, .custom-table td {
    border: 1px solid #334155;
    padding: 6px 10px;
    text-align: left;
}
.custom-table th {
    background-color: #334155;
    color: white;
    cursor: pointer;
}
.custom-table tr:nth-child(even) { background-color: #3d5975; }
.custom-table tr:nth-child(odd) { background-color: #466686; }
.custom-table tr:hover { background-color: #64748b; }
a.ticker-link {
    color: #93c5fd;
    text-decoration: none;
}
a.ticker-link:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2 = st.tabs(["ð Terminal", "ð§  Alt-Data Control Panel"])

with tab1:
    st.title("Terminal")

    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = None

    # Table rendering with clickable links that update state
    def render_table():
        st.markdown("<table class='custom-table'><thead><tr>" +
                    "".join([f"<th>{col}</th>" for col in df.columns]) +
                    "</tr></thead><tbody>", unsafe_allow_html=True)

        for _, row in df.iterrows():
            ticker = row["Ticker"]
            cells = ""
            for col in df.columns:
                val = row[col]
                if col == "Ticker":
                    val = f"<a href='?selected={ticker}' class='ticker-link'>{ticker}</a>"
                elif col == "TrgtUpside":
                    val = f"{val:.1f}%"
                elif col == "MktCap":
                    if val >= 1e12:
                        val = f"{val/1e12:.2f}T"
                    elif val >= 1e9:
                        val = f"{val/1e9:.2f}B"
                    else:
                        val = f"{val/1e6:.2f}M"
                elif col == "30DayVol":
                    val = f"{val/1e6:.1f}M"
                cells += f"<td>{val}</td>"
            st.markdown(f"<tr>{cells}</tr>", unsafe_allow_html=True)
        st.markdown("</tbody></table>", unsafe_allow_html=True)

    # Capture ticker from query params
    query_params = st.experimental_get_query_params()
    if "selected" in query_params:
        st.session_state.selected_ticker = query_params["selected"][0]

    # Display table
    render_table()

    # Right-side inspector
    if st.session_state.selected_ticker:
        selected_row = df[df["Ticker"] == st.session_state.selected_ticker]
        if not selected_row.empty:
            row = selected_row.iloc[0]
            st.markdown("---")
            with st.container():
                st.markdown(f"### ð§ª Signal Inspector: {row['Ticker']}")
                st.write(f"**Terminal Score**: {row['TerminalScore']}")
                st.write(f"**PEG**: {row['PEG']}")
                st.write(f"**EPS Growth**: {row['EPSGr']}%")
                st.write(f"**Analyst Score**: {row['AnalystSc']}")
                st.write(f"**Target Upside**: {row['TrgtUpside']}%")
                st.write(f"**Reddit Sentiment**: {row['RedditSc']}")
                st.write(f"**Sector**: {row['Sector']}")

with tab2:
    st.title("ð§  Alt-Data Control Panel")
    st.info("This tab will be extended with alt-data sliders and controls.")
