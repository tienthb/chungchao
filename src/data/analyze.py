import os
import sys
import pandas as pd
from datetime import datetime

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.db.pg_controller import PGController

controller = PGController()
cur = controller.cursor


def stock_summary():
    query = """
        SELECT 
            t.transaction_date,
            t.ticker,
            t.buy_vol,
            t.buy_amt,
            t.sell_vol,
            t.sell_amt,
            t.daily_vol,
            t.avg_price
        FROM transaction_volume t
        WHERE transaction_date >= (NOW() - INTERVAL '270 day')::date
    """
    cur.execute(query)
    data = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(data, columns=columns)
    return df

def rank_by_vol():
    query = """
        WITH base AS 
        (
            SELECT 
                ticker,
                SUM(buy_vol + sell_vol) AS volume
            FROM transaction_volume
            WHERE transaction_date >= (NOW() - INTERVAL '270 day')::date
            GROUP BY ticker
        )
        SELECT 
            *,
            ROW_NUMBER() OVER (ORDER BY volume DESC) AS rn
        FROM base
    """
    cur.execute(query)
    data = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    df = pd.DataFrame(data, columns=columns)
    df["volume"] = df["volume"].astype("int64")
    return df

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