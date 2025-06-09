import streamlit as st
import pandas as pd

# Dummy dataset
data = [
    {"ticker": "AAPL", "price": 185.2, "pe": 29.8, "peg": 2.1, "eps_growth": 18.5},
    {"ticker": "GOOGL", "price": 128.3, "pe": 26.4, "peg": 1.8, "eps_growth": 20.2},
    {"ticker": "SMCI", "price": 900.5, "pe": 32.7, "peg": 0.9, "eps_growth": 75.0},
    {"ticker": "MSFT", "price": 320.1, "pe": 34.5, "peg": 2.3, "eps_growth": 15.0},
    {"ticker": "TSLA", "price": 230.2, "pe": 70.1, "peg": 2.5, "eps_growth": 28.0},
]
df = pd.DataFrame(data)

# Session state setup
if "default_filters" not in st.session_state:
    st.session_state.default_filters = {"pe_max": 40, "peg_max": 2.5, "eps_min": 10}

st.title("📊 Stock Screener")

# --- FILTER SECTION ---
with st.expander("🔍 Filter Criteria", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        pe_max = st.slider("Max P/E Ratio", 0, 100, st.session_state.default_filters["pe_max"], step=1)
        st.number_input("Manual P/E max", value=pe_max, key="pe_input")
        pe_max = st.session_state.pe_input

    with col2:
        peg_max = st.slider("Max PEG Ratio", 0.0, 5.0, st.session_state.default_filters["peg_max"], step=0.1)
        st.number_input("Manual PEG max", value=peg_max, key="peg_input")
        peg_max = st.session_state.peg_input

    eps_min = st.slider("Min EPS Growth (%)", 0, 100, st.session_state.default_filters["eps_min"], step=1)
    st.number_input("Manual EPS min", value=eps_min, key="eps_input")
    eps_min = st.session_state.eps_input

    st.markdown("---")
    apply_defaults = st.button("Apply Standard Filters")
    if apply_defaults:
        pe_max = st.session_state.default_filters["pe_max"]
        peg_max = st.session_state.default_filters["peg_max"]
        eps_min = st.session_state.default_filters["eps_min"]
        st.experimental_rerun()

    with st.popover("⚙️ Change Standard Filters"):
        st.markdown("### Set New Defaults")
        new_pe = st.number_input("New max P/E", value=st.session_state.default_filters["pe_max"], key="new_pe")
        new_peg = st.number_input("New max PEG", value=st.session_state.default_filters["peg_max"], key="new_peg")
        new_eps = st.number_input("New min EPS growth", value=st.session_state.default_filters["eps_min"], key="new_eps")
        if st.button("Save & Apply"):
            st.session_state.default_filters = {
                "pe_max": new_pe,
                "peg_max": new_peg,
                "eps_min": new_eps
            }
            st.success("✅ Standard filters updated.")
            st.experimental_rerun()

# Apply filtering logic
filtered_df = df[
    (df["pe"] <= pe_max) &
    (df["peg"] <= peg_max) &
    (df["eps_growth"] >= eps_min)
]

st.markdown("### 📈 Filtered Results")
st.dataframe(filtered_df.reset_index(drop=True))
