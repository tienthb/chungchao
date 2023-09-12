import sys
import os
import streamlit as st
import pandas as pd

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

os.getenv("POSTGRES_HOST")

from src.db.pg_controller import PGController


controller = PGController()
cur = controller.cursor

st.set_page_config(
    page_title="Chứng cháo",
    layout="wide"
)

st.write("# Chứng cháo")

limit_row = 50

query = "SELECT COUNT(1) FROM transaction_snapshot"
cur.execute(query)
result = cur.fetchone()[0]

if result > 0:

    query = """SELECT 
        ticker,
        volume,
        ROW_NUMBER() OVER(ORDER BY volume DESC) AS buy_rank,
        ROW_NUMBER() OVER(ORDER BY ABS(volume) DESC) AS sell_rank
    FROM transaction_snapshot ts"""
    cur.execute(query)
    data = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(data, columns=columns)

    query = """WITH base AS 
        (
            SELECT ticker, buy_vol + sell_vol AS volume
            FROM transaction_volume
            WHERE transaction_date >= (NOW() - INTERVAL '270 day')::date
        )
        SELECT 
            *,
            ROW_NUMBER() OVER (ORDER BY volume DESC) AS rn
        FROM base
    """
    cur.execute(query)
    data = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    df2 = pd.DataFrame(data, columns=columns)
    # df

    col1, col2, col3 = st.columns(3)

    st.markdown(
        """
        <style>
            div[data-testid="column"]:nth-of-type(1)
            {
                text-align: center;
            } 

            div[data-testid="column"]:nth-of-type(2)
            {
                text-align: center;
            }

            div[data-testid="column"]:nth-of-type(3)
            {
                text-align: center;
            } 
        </style>
        """,unsafe_allow_html=True
    )

    with col1:
        st.subheader("Most Buy")
        st.header(f"""{df[df["buy_rank"] == 1]["volume"].values[0]:,}""")
        f"""**{df[df["buy_rank"] == 1]["ticker"].values[0]}**"""
        df.loc[df["buy_rank"] <= limit_row, ["ticker", "volume"]]

    with col2:
        st.subheader("Most Sell")
        st.header(f"""{df[df["sell_rank"] == 1]["volume"].values[0]:,}""")
        f"""**{df[df["sell_rank"] == 1]["ticker"].values[0]}**"""
        df.loc[df["sell_rank"] <= limit_row, ["ticker", "volume"]]

    with col3:
        st.subheader("Most Buy & Sell")
        st.header(f"""{df2[df2["rn"] == 1]["volume"].values[0]:,}""")
        f"""**{df2[df2["rn"] == 1]["ticker"].values[0]}**"""
        df2.loc[df2["rn"] <= limit_row, ["ticker", "volume"]]

else:
    "# No data available"
    "Go to Data tab to load data"