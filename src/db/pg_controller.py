import psycopg2
import os
from pathlib import Path
import pandas as pd

class PGController:
    def __init__(self) -> None:
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.database = os.getenv("POSTGRES_DB", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "password")
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def load_data(self, filename: str, data):
        tbl_name = "transaction_volume"
        tmp_tbl_name = "tmp_transaction"
        # Create temp tabke
        query = f"""CREATE TEMP TABLE {tmp_tbl_name} AS
            SELECT *
            FROM {tbl_name}
            WHERE 1 = 0"""
        self.cursor.execute(query)
        self.cursor.copy_from(data, tmp_tbl_name, sep=",")
        # merge into target
        query = f"""MERGE INTO {tbl_name} t
            USING {tmp_tbl_name} s
            ON s.ticker = t.ticker
                AND s.transaction_date = t.transaction_date
            WHEN MATCHED THEN
                UPDATE SET buy_vol = s.buy_vol,
                    buy_amt = s.buy_amt,
                    sell_vol = s.sell_vol,
                    sell_amt = s.sell_amt,
                    volume = s.volume,
                    oi = s.oi,
                    daily_vol = s.daily_vol
            WHEN NOT MATCHED THEN
                INSERT (ticker, transaction_date, buy_vol, buy_amt, sell_vol, sell_amt, volume, oi, daily_vol)
                VALUES (s.ticker, s.transaction_date, s.buy_vol, s.buy_amt, s.sell_vol, s.sell_amt, s.volume, s.oi, s.daily_vol)"""
        self.cursor.execute(query)
        # Drop tmp table
        query = f"DROP TABLE IF EXISTS {tmp_tbl_name}"
        self.cursor.execute(query)


# Init tables if not exists
controller = PGController()
curr = controller.cursor
files = Path(os.getcwd()).rglob("*.sql")
for path in files:
    filename = os.path.relpath(path, os.getcwd())
    with open(filename, "r") as f:
        curr.execute(f.read())
        f.close()
controller.conn.close()