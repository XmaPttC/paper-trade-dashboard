import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Set page
st.set_page_config(layout="wide", page_title="AG Grid Test")

# CSS styling injected to override AG Grid defaults
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        font-family: 'Lato', sans-serif;
    }

    .ag-root-wrapper {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }

    .ag-header {
        background-color: #334155 !important;
        color: #f1f5f9 !important;
    }

    .ag-row {
        background-color: #3d5975 !important;
        color: #f1f5f9 !important;
    }

    .ag-row:nth-child(even) {
        background-color: #466686 !important;
    }

    .ag-row:hover {
        background-color: #64748b !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sample DataFrame
df = pd.DataFrame({
    "Ticker": ["AAPL", "TSLA", "GOOG", "MSFT"],
    "Price": [187.6, 251.3, 2835.2, 312.0],
    "PE": [28, 70, 30, 33],
    "PEG": [1.5, 2.1, 1.8, 1.9]
})

# Configure Grid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True)
grid_options = gb.build()

# Display table
AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    update_mode=GridUpdateMode.NO_UPDATE,
    fit_columns_on_grid_load=True,
    theme="streamlit"
)
