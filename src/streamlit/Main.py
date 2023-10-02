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

if al.has_data():
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
    # st.write("The current number is", n_months)
    df, df2, df3 = al.calc_top_10_stock(n_months)
    col1, col2, col3 = st.columns(3)

    # df
    # df2
    # df = al.calc_top_10_stock(n_months)
    # query
    # stock = al.stock_summary()
    # stock_rank = al.rank_by_vol()
    
    with col1:
        st.dataframe(df, hide_index=True)
    #     n_months = st.number_input("Insert number of months", value=9)
    #     st.subheader("Most Buy & Sell")
    #     st.header(f"""{stock_rank[stock_rank["rn"] == 1]["volume"].values[0]:,}""")
    #     f"""**{stock_rank[stock_rank["rn"] == 1]["ticker"].values[0]}**"""
    #     st.dataframe(
    #         stock_rank.loc[stock_rank["rn"] <= limit_row, ["ticker", "volume"]], 
    #         hide_index=True
    #     )

    with col2:
        st.dataframe(df2, hide_index=True)
    #     tickers = al.get_stocks()
    #     tickers = tickers.split(",")
    #     option = st.selectbox(
    #         "Select stock",
    #         tickers
    #     )
    #     st.dataframe(
    #         stock[stock["ticker"] == option].sort_values("transaction_date", ascending=False), 
    #         hide_index=True
    #     )

    with col3:
        st.dataframe(df3, hide_index=True)
    #     st.subheader("Most Buy & Sell")
    #     st.header(f"""{df2[df2["rn"] == 1]["volume"].values[0]:,}""")
    #     f"""**{df2[df2["rn"] == 1]["ticker"].values[0]}**"""
    #     df2.loc[df2["rn"] <= limit_row, ["ticker", "volume"]]

else:
    "# No data available"
    "Go to Data tab to load data"