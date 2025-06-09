import streamlit as st
import pandas as pd

# ---------- Dummy Data Setup ----------
def format_market_cap(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.0f}M"
    else:
        return str(value)

def load_screener_data():
    data = {
        "ticker": ["AAPL", "GOOGL", "MSFT", "ABC"],
        "price": [180.14, 125.80, 312.45, 8.92],
        "pe": [28.5, 22.3, 35.1, 17.2],
        "peg": [1.8, 1.3, 2.0, 0.9],
        "eps_growth": [25.0, 30.5, 22.1, 18.2],
        "market_cap": [2.8e12, 1.8e12, 2.3e12, 480_000_000]
    }
    df = pd.DataFrame(data)
    df["market_cap_fmt"] = df["market_cap"].apply(format_market_cap)
    return df

# ---------- Session State Setup ----------
if "hidden_rows" not in st.session_state:
    st.session_state.hidden_rows = set()

if "sort_column" not in st.session_state:
    st.session_state.sort_column = None
    st.session_state.sort_ascending = True

if "filters" not in st.session_state:
    st.session_state.filters = {"pe": 100, "peg": 5, "eps_growth": 0}

# ---------- Filter Application ----------
def apply_filters(df, filters):
    return df[
        (df["pe"] <= filters["pe"]) &
        (df["peg"] <= filters["peg"]) &
        (df["eps_growth"] >= filters["eps_growth"])
    ]

# ---------- UI ----------
st.title("📊 Stock Screener Dashboard")

# --- Filter Controls ---
with st.expander("🎛️ Filter Controls", expanded=True):
    st.markdown("### Apply Filters")

    col1, col2, col3 = st.columns(3)
    pe = col1.slider("Max P/E", 0, 100, st.session_state.filters["pe"])
    peg = col2.slider("Max PEG", 0.0, 5.0, st.session_state.filters["peg"])
    eps = col3.slider("Min EPS Growth (%)", 0, 100, st.session_state.filters["eps_growth"])

    if st.button("Apply Filters"):
        st.session_state.filters = {"pe": pe, "peg": peg, "eps_growth": eps}

# --- Default Filter Editor ---
with st.expander("⚙️ Change Default Filters"):
    dcol1, dcol2, dcol3 = st.columns(3)
    new_pe = dcol1.number_input("Default Max P/E", value=st.session_state.filters["pe"])
    new_peg = dcol2.number_input("Default Max PEG", value=st.session_state.filters["peg"])
    new_eps = dcol3.number_input("Default Min EPS Growth", value=st.session_state.filters["eps_growth"])

    if st.button("Save & Apply Default Filters"):
        st.session_state.filters = {"pe": new_pe, "peg": new_peg, "eps_growth": new_eps}
        st.success("✅ Default filters updated and applied!")

# ---------- Data Section ----------
df = load_screener_data()
filtered = apply_filters(df, st.session_state.filters)

# Sort toggle
def sort_by(column):
    if st.session_state.sort_column == column:
        st.session_state.sort_ascending = not st.session_state.sort_ascending
    else:
        st.session_state.sort_column = column
        st.session_state.sort_ascending = True

if st.session_state.sort_column:
    filtered = filtered.sort_values(
        by=st.session_state.sort_column,
        ascending=st.session_state.sort_ascending
    )

# Column headers
col_labels = {
    "ticker": "Stock",
    "price": "Last Price",
    "pe": "PE",
    "peg": "PEG",
    "eps_growth": "EPS Growth",
    "market_cap_fmt": "Market Cap"
}
cols = st.columns(len(col_labels) + 2)

for i, (col_key, label) in enumerate(col_labels.items()):
    if cols[i].button(label):
        sort_by(col_key)

cols[-2].markdown("**👁️**")
cols[-1].markdown("**➕**")

# Render table
for _, row in filtered.iterrows():
    ticker = row["ticker"]
    if ticker in st.session_state.hidden_rows:
        continue

    rcols = st.columns(len(col_labels) + 2)
    rcols[0].markdown(f"[{row['ticker']}](https://finance.yahoo.com/quote/{row['ticker']})")
    rcols[1].write(f"${row['price']:.2f}")
    rcols[2].write(row["pe"])
    rcols[3].write(row["peg"])
    rcols[4].write(f"{row['eps_growth']}%")
    rcols[5].write(row["market_cap_fmt"])

    if rcols[-2].button("👁️", key=f"hide_{ticker}"):
        st.session_state.hidden_rows.add(ticker)
        st.experimental_rerun()

    if rcols[-1].button("➕", key=f"add_{ticker}"):
        st.success(f"{ticker} added to Trading Simulation (placeholder)")

# Restore hidden
if st.button("Restore All Rows"):
    st.session_state.hidden_rows.clear()
    st.success("✅ All rows restored.")
