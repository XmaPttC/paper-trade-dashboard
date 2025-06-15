import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="AG Grid Styling Test")

# Custom CSS for styling AG Grid
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');
html, body, .stApp, .block-container {
    font-family: 'Lato', sans-serif;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
}
.ag-theme-streamlit {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    font-family: 'Lato', sans-serif;
    font-size: 13px !important;
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

# Sample data
df = pd.DataFrame({
    "Ticker": ["AAPL", "TSLA", "MSFT", "GOOG", "NVDA"],
    "Price": [175.2, 202.5, 321.8, 140.7, 116.9],
    "PE Ratio": [28.5, 65.3, 33.2, 24.8, 50.0],
    "PEG Ratio": [1.2, 2.1, 1.8, 1.5, 2.3]
})

# AG Grid configuration
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True)
gb.configure_grid_options(domLayout='normal')
grid_options = gb.build()

# Display the table
AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    theme="streamlit",  # This activates the 'ag-theme-streamlit' styling
    update_mode=GridUpdateMode.NO_UPDATE
)
