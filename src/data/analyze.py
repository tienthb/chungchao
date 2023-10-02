import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.db.pg_controller import PGController

controller = PGController()
cur = controller.cursor


# def stock_summary():
#     query = """
#         SELECT 
#             t.transaction_date,
#             t.ticker,
#             t.buy_vol,
#             t.buy_amt,
#             t.sell_vol,
#             t.sell_amt,
#             t.daily_vol,
#             t.avg_price
#         FROM transaction_volume t
#         WHERE transaction_date >= (NOW() - INTERVAL '270 day')::date
#     """
#     cur.execute(query)
#     data = cur.fetchall()

#     columns = [desc[0] for desc in cur.description]

#     df = pd.DataFrame(data, columns=columns)
#     return df

# def rank_by_vol():
#     query = """
#         WITH base AS 
#         (
#             SELECT 
#                 ticker,
#                 SUM(buy_vol + sell_vol) AS volume
#             FROM transaction_volume
#             WHERE transaction_date >= (NOW() - INTERVAL '270 day')::date
#             GROUP BY ticker
#         )
#         SELECT 
#             *,
#             ROW_NUMBER() OVER (ORDER BY volume DESC) AS rn
#         FROM base
#     """
#     cur.execute(query)
#     data = cur.fetchall()

#     columns = [desc[0] for desc in cur.description]

#     df = pd.DataFrame(data, columns=columns)
#     df["volume"] = df["volume"].astype("int64")
#     return df

def has_data():
    query = "SELECT COUNT(1) FROM transaction_snapshot"
    cur.execute(query)
    result = cur.fetchone()[0]
    if result > 0:
        return True
    return False

def get_stocks():
    query = "SELECT string_agg(DISTINCT ticker, ',') FROM transaction_volume"
    cur.execute(query)
    return cur.fetchone()[0]

def calc_top_10_stock(n_months):
    days = n_months * 30

    query = f"""WITH date_param AS 
        (
            SELECT NOW()::date t_date, (NOW() - INTERVAL '{days} days')::DATE f_date
        )
        ,top_vol AS 
        (
            SELECT 
                tv.ticker,
                SUM(tv.buy_vol + tv.sell_vol) AS total_vol
            FROM transaction_volume tv
                INNER JOIN date_param p ON tv.transaction_date BETWEEN f_date AND t_date
            GROUP BY tv.ticker
        )
        SELECT *
        FROM top_vol
        ORDER BY total_vol DESC
        LIMIT 10
    """   
    cur.execute(query)
    column_names = [desc[0] for desc in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=column_names)
    df = df.astype({"total_vol": np.int64})

    query = f"""WITH date_param AS 
        (
            SELECT NOW()::date t_date, (NOW() - INTERVAL '{days} days')::DATE f_date
        )
        ,top_vol AS 
        (
            SELECT 
                tv.ticker,
                SUM(tv.buy_vol) AS total_buy_vol,
                CASE WHEN SUM(tv.buy_vol) = 0 THEN 0 ELSE SUM(tv.buy_amt) / SUM(tv.buy_vol) END AS price,
                CASE WHEN SUM(tv.buy_vol - tv.sell_vol) = 0 THEN 0 ELSE SUM(tv.buy_amt - tv.sell_amt) / SUM(tv.buy_vol - tv.sell_vol) END AS price2
            FROM transaction_volume tv
                INNER JOIN date_param p ON tv.transaction_date BETWEEN f_date AND t_date
            GROUP BY tv.ticker
        )
        SELECT *
        FROM top_vol
        ORDER BY total_buy_vol DESC
        LIMIT 10
    """   
    cur.execute(query)
    column_names = [desc[0] for desc in cur.description]
    df2 = pd.DataFrame(cur.fetchall(), columns=column_names)
    df2 = df2.astype({"total_buy_vol": np.int64, "price": np.int16, "price2": np.int16})

    query = f"""WITH date_param AS 
        (
            SELECT NOW()::date t_date, (NOW() - INTERVAL '{days} days')::DATE f_date
        )
        ,top_vol AS 
        (
            SELECT 
                tv.ticker,
                SUM(tv.sell_vol) AS total_sell_vol
            FROM transaction_volume tv
                INNER JOIN date_param p ON tv.transaction_date BETWEEN f_date AND t_date
            GROUP BY tv.ticker
        )
        SELECT *
        FROM top_vol
        ORDER BY total_sell_vol DESC
        LIMIT 10
    """   
    cur.execute(query)
    column_names = [desc[0] for desc in cur.description]
    df3 = pd.DataFrame(cur.fetchall(), columns=column_names)
    df3 = df3.astype({"total_sell_vol": np.int64})
    return df, df2, df3