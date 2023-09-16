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
        # DELETE
        query = f"""DELETE FROM {tbl_name} t
            USING {tmp_tbl_name} s
            WHERE t.ticker = s.ticker
                AND t.transaction_date = s.transaction_date"""
        self.cursor.execute(query)

        # Get column list
        query = f"""SELECT string_agg(column_name, ',')
            FROM information_schema.COLUMNS
            WHERE table_name = '{tbl_name}'"""
        self.cursor.execute(query)
        columns = self.cursor.fetchone()[0]

        # INSERT
        query = f"""INSERT INTO {tbl_name} ({columns})
            SELECT {columns}
            FROM {tmp_tbl_name}"""
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