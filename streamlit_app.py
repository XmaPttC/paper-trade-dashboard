import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="Dark Table Test")

# Sample data
df = pd.DataFrame({
    "Ticker": ["AAPL", "GOOG", "MSFT"],
    "PE": [24.6, 30.2, 28.1],
    "EPS Growth": [18, 22, 15]
})

# Configure grid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True)

# Apply row-level styling
gb.configure_grid_options(
    getRowStyle="""
    function(params) {
        return {
            'backgroundColor': '#3d5975',
            'color': '#f1f5f9',
            'fontFamily': 'Lato, sans-serif',
            'fontSize': '13px'
        }
    }
    """
)
grid_options = gb.build()

# Render
AgGrid(
    df,
    gridOptions=grid_options,
    height=300,
    width='100%',
    update_mode=GridUpdateMode.NO_UPDATE,
    fit_columns_on_grid_load=True,
    theme="streamlit",  # Must use built-in theme
)
