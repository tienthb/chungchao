import os
import io
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


def load_data(file):
    df = pd.read_csv(file)
    df["transaction_date"] = df["<DTYYYYMMDD>"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").date())
    df = df.drop("<DTYYYYMMDD>", axis=1)
    df["<Ticker>"] = df["<Ticker>"].apply(lambda x: x.split("_")[1])
    df.columns = ["ticker", "buy_vol", "volume", "oi", "sell_vol", "buy_amt", "sell_amt", "transaction_date"]
    df["daily_vol"] = df["buy_vol"] - df["sell_vol"]
    df = df[["ticker", "transaction_date", "buy_vol", "volume", "oi", "sell_vol", "buy_amt", "sell_amt", "daily_vol"]]
    df = df[df["ticker"].str.len() == 3]
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    controller.load_data(file.name, buffer)
    return df

def calc_up_to_date():
    query = "SELECT COUNT(1) FROM transaction_snapshot"
    cur.execute(query)
    result = cur.fetchone()[0]
    # return result
    if result == 0:
        query = """INSERT INTO transaction_snapshot
            SELECT 
                ticker,
                MAX(transaction_date) AS transaction_date,
                SUM(daily_vol) AS volume
            FROM transaction_volume t
            GROUP BY ticker, NOW()::date"""
        cur.execute(query)
        controller.conn.commit()
    else:
        query = """MERGE INTO transaction_snapshot t
            USING (
                WITH last_updated AS 
                (
                    SELECT MAX(transaction_date) transaction_date
                    FROM transaction_snapshot ts
                )
                SELECT 
                    ticker,
                    MAX(transaction_date) AS transaction_date,
                    SUM(daily_vol) AS volume
                FROM transaction_volume t
                WHERE transaction_date > (SELECT transaction_date FROM last_updated)
                GROUP BY ticker
            ) s
            ON t.ticker = s.ticker
            WHEN MATCHED THEN
                UPDATE 
                SET volume = t.volume + s.volume,
                    transaction_date = s.transaction_date
            WHEN NOT MATCHED THEN
                INSERT (ticker, transaction_date, volume)
                VALUES (s.ticker, s.transaction_date, s.volume)"""

def patching_db():
    query = """
        DROP TABLE IF EXISTS transaction_snapshot;

        ALTER TABLE transaction_volume
        DROP COLUMN avg_price
    """
    cur.execute(query)

# print("Ingestion")