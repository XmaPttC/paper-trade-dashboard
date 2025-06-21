import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Alt-Data Screener")

# Setup tabs
tab1, tab2 = st.tabs(["📈 Screener", "🧠 Alt-Data Control Panel"])

# Placeholder dataframe for tickers
df = pd.DataFrame({
    "Ticker": ["AAPL", "MSFT", "TSLA"],
    "Price": [190.1, 342.8, 265.3],
    "Sector": ["Tech", "Tech", "Auto"],
    "PEG": [1.5, 2.1, 1.2],
    "EPSGr": [15, 10, 30],
})

# Store Alt-Data settings in session_state
if "altdata_settings" not in st.session_state:
    st.session_state.altdata_settings = {
        "Reddit": {"enabled": True, "weight": 20, "threshold": 0.3},
        "WebTraffic": {"enabled": False, "weight": 15, "threshold": 10.0},
        "GEX": {"enabled": True, "weight": 25, "threshold": 1.5},
    }

# ---------------- Tab 2: Alt-Data Control Panel ----------------
with tab2:
    st.title("🧠 Alt-Data Control Panel")
    st.markdown("Configure which alt-data signals to include in scoring and how they're weighted.")

    col1, col2, col3 = st.columns(3)

    # Reddit Mentions Card
    with col1.expander("📣 Reddit Mentions"):
        enabled = st.checkbox("Enable Reddit Score", value=st.session_state.altdata_settings["Reddit"]["enabled"], key="reddit_toggle")
        weight = st.slider("Weight", 0, 100, int(st.session_state.altdata_settings["Reddit"]["weight"]), key="reddit_weight")
        threshold = st.number_input(
            "Sentiment Threshold",
            min_value=float(0.0),
            max_value=float(1.0),
            value=float(st.session_state.altdata_settings["Reddit"]["threshold"]),
            step=float(0.01),
            key="reddit_thresh"
        )

    # Web Traffic Card
    with col2.expander("🌐 Web Traffic"):
        enabled = st.checkbox("Enable Web Traffic Score", value=st.session_state.altdata_settings["WebTraffic"]["enabled"], key="web_toggle")
        weight = st.slider("Weight", 0, 100, int(st.session_state.altdata_settings["WebTraffic"]["weight"]), key="web_weight")
        threshold = st.number_input(
            "Change Threshold (%)",
            min_value=float(0.0),
            max_value=float(100.0),
            value=float(st.session_state.altdata_settings["WebTraffic"]["threshold"]),
            step=float(1.0),
            key="web_thresh"
        )

    # GEX Card
    with col3.expander("📊 GEX Signal"):
        enabled = st.checkbox("Enable GEX Score", value=st.session_state.altdata_settings["GEX"]["enabled"], key="gex_toggle")
        weight = st.slider("Weight", 0, 100, int(st.session_state.altdata_settings["GEX"]["weight"]), key="gex_weight")
        threshold = st.number_input(
            "Gamma Threshold",
            min_value=float(0.0),
            max_value=float(5.0),
            value=float(st.session_state.altdata_settings["GEX"]["threshold"]),
            step=float(0.1),
            key="gex_thresh"
        )

    # Apply Button
    if st.button("✅ Apply Alt-Data Scoring"):
        st.session_state.altdata_settings["Reddit"]["enabled"] = st.session_state.reddit_toggle
        st.session_state.altdata_settings["Reddit"]["weight"] = st.session_state.reddit_weight
        st.session_state.altdata_settings["Reddit"]["threshold"] = st.session_state.reddit_thresh

        st.session_state.altdata_settings["WebTraffic"]["enabled"] = st.session_state.web_toggle
        st.session_state.altdata_settings["WebTraffic"]["weight"] = st.session_state.web_weight
        st.session_state.altdata_settings["WebTraffic"]["threshold"] = st.session_state.web_thresh

        st.session_state.altdata_settings["GEX"]["enabled"] = st.session_state.gex_toggle
        st.session_state.altdata_settings["GEX"]["weight"] = st.session_state.gex_weight
        st.session_state.altdata_settings["GEX"]["threshold"] = st.session_state.gex_thresh

        st.success("Alt-Data settings applied!")

# ---------------- Tab 1: Screener ----------------
with tab1:
    st.title("📈 Harbourne Screener")
    st.dataframe(df)


# --- Alt-Data Signal Cards ---

import streamlit as st

# Ensure session state initialization
if "altdata_settings" not in st.session_state:
    st.session_state.altdata_settings = {}

# Helper function to create a signal card
def render_signal_card(col, title, key_prefix, default_enabled, default_weight, threshold_range, default_thresh):
    with col.expander(title):
        st.session_state.altdata_settings.setdefault(key_prefix, {
            "enabled": default_enabled,
            "weight": default_weight,
            "threshold": default_thresh
        })

        enabled = st.checkbox("Enable", value=st.session_state.altdata_settings[key_prefix]["enabled"], key=f"{key_prefix}_toggle")
        weight = st.slider("Weight", 0, 100, int(st.session_state.altdata_settings[key_prefix]["weight"]), key=f"{key_prefix}_weight")
        threshold = st.number_input(
            "Threshold",
            min_value=float(threshold_range[0]),
            max_value=float(threshold_range[1]),
            value=float(st.session_state.altdata_settings[key_prefix]["threshold"]),
            step=float(0.01),
            key=f"{key_prefix}_thresh"
        )

        st.session_state.altdata_settings[key_prefix]["enabled"] = enabled
        st.session_state.altdata_settings[key_prefix]["weight"] = weight
        st.session_state.altdata_settings[key_prefix]["threshold"] = threshold

# Layout in 3 columns
col1, col2, col3 = st.columns(3)

# High-Quality Signals
render_signal_card(col1, "📈 Options Flow", "optionsflow", True, 25, (0.0, 5.0), 1.0)
render_signal_card(col2, "🔒 Dark Pool Prints", "darkpool", True, 20, (0.0, 1000.0), 100.0)
render_signal_card(col3, "📊 Gamma Exposure", "gex", True, 25, (0.0, 5.0), 1.5)

# Medium-Quality Signals
render_signal_card(col1, "🧑‍💼 Insider Buying", "insider", True, 15, (0.0, 100.0), 10.0)
render_signal_card(col2, "📱 App Usage Growth", "appusage", True, 10, (0.0, 500.0), 50.0)

# Sentiment Signals
render_signal_card(col3, "📣 Reddit Mentions", "reddit", True, 5, (0.0, 1.0), 0.3)
render_signal_card(col1, "🌐 Google Trends", "googletrends", True, 5, (0.0, 100.0), 10.0)
