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

def patching_db():
    query = """
        SELECT TRUE
    """
    cur.execute(query)

# print("Ingestion")