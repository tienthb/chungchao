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


def _calc_price(buy_amt, sell_amt, daily_vol):
    if daily_vol == 0:
        return 0
    return int((buy_amt - sell_amt) / daily_vol)

def load_data(file):
    df = pd.read_csv(file)
    df["transaction_date"] = df["<DTYYYYMMDD>"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").date())
    df = df.drop("<DTYYYYMMDD>", axis=1)
    df["<Ticker>"] = df["<Ticker>"].apply(lambda x: x.split("_")[1])
    df.columns = ["ticker", "buy_vol", "volume", "oi", "sell_vol", "buy_amt", "sell_amt", "transaction_date"]
    df["daily_vol"] = df["buy_vol"] - df["sell_vol"]
    df["avg_price"] = df.apply(lambda x: _calc_price(x["buy_amt"], x["sell_amt"], x["daily_vol"]), axis=1)
    df = df[["ticker", "transaction_date", "buy_vol", "volume", "oi", "sell_vol", "buy_amt", "sell_amt", "daily_vol", "avg_price"]]
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
        ALTER TABLE transaction_volume
        RENAME buy_amt TO high;

        ALTER TABLE transaction_volume
        RENAME volume TO buy_amt;

        ALTER TABLE transaction_volume
        RENAME sell_vol TO low;

        ALTER TABLE transaction_volume
        RENAME sell_amt TO sell_vol;

        ALTER TABLE transaction_volume
        RENAME oi TO sell_amt;    

        ALTER TABLE transaction_volume
        RENAME high TO volume;

        ALTER TABLE transaction_volume
        RENAME low TO oi;

        UPDATE transaction_volume
        SET daily_vol = buy_vol - sell_vol;

        ALTER TABLE transaction_volume
        ADD COLUMN avg_price INT;

        UPDATE transaction_volume
        SET avg_price = CASE WHEN daily_vol = 0 THEN 0 ELSE (buy_amt - sell_amt) / daily_vol END
    """
    cur.execute(query)

# print("Ingestion")