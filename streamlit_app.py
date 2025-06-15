import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="AG Grid Test")

# Use sample data
data = pd.DataFrame({
    "Ticker": ["AAPL", "GOOG", "MSFT"],
    "PE": [24.6, 30.2, 28.1],
    "EPS Growth": [18, 22, 15]
})

# Grid options
gb = GridOptionsBuilder.from_dataframe(data)
gb.configure_default_column(editable=False, sortable=True, filter=True)
grid_options = gb.build()

# Use AG Grid with material-dark theme
st.markdown("<div class='ag-theme-material-dark' style='height: 300px;'>", unsafe_allow_html=True)
AgGrid(
    data,
    gridOptions=grid_options,
    height=300,
    width='100%',
    update_mode=GridUpdateMode.NO_UPDATE,
    fit_columns_on_grid_load=True,
    theme="material-dark"  # This must match the class above
)
st.markdown("</div>", unsafe_allow_html=True)
