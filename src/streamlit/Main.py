import sys
import os
import streamlit as st
import pandas as pd

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

os.getenv("POSTGRES_HOST")

import src.data.analyze  as al

st.set_page_config(
    page_title="Chứng cháo",
    layout="wide"
)

st.write("# Chứng cháo")
limit_row = 50

# Layout settings
st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(1)
        {
            text-align: center
        } 

        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: center
        }

        div[data-testid="column"]:nth-of-type(3)
        {
            text-align: center
        }
    </style>
    """,unsafe_allow_html=True
)
n_months = st.number_input("Insert number of months", value=9)
df, df2, df3 = al.calc_top_10_stock(n_months)
col1, col2, col3 = st.columns(3)

with col1:
    st.dataframe(df, hide_index=True)

with col2:
    st.dataframe(df2, hide_index=True)

with col3:
    st.dataframe(df3, hide_index=True)