import os
import io
import sys
import pandas as pd
from datetime import datetime, date
import requests
import zipfile
from pathlib import Path
import streamlit as st

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.db.pg_controller import PGController

controller = PGController()
cur = controller.cursor


def load_data(load_type: str):
    st.write("Downloading data")
    result = fetch_zip_file(load_type)
    st.write("Zip downloaded")
    if not result: 
        files = Path(os.getcwd()).rglob("CafeF.NN_*")
        for file in files:
            st.write(f"Loading {file.name}")
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
    clean_up()

def patching_db():
    query = """
        SELECT TRUE
    """
    cur.execute(query)

def fetch_zip_file(load_type):
    today = date.today()
    today_str1 = today.strftime("%Y%m%d")
    today_str2 = today.strftime("%d%m%Y")
    if load_type == "Incr":
        url = f"https://cafef1.mediacdn.vn/data/ami_data/{today_str1}/CafeF.CCNN.{today_str2}.zip"
    else:
        url = f"https://cafef1.mediacdn.vn/data/ami_data/{today_str1}/CafeF.CCNN.Upto{today_str2}.zip"
    # Try to get the ZIP file
    try:
        response = requests.get(url)
    except OSError:
        st.write("No connection to the server!")
        return None

    # check if the request is succesful
    if response.status_code == 200:
        # Save dataset to file
        st.write(f"Found data for {today.strftime('%d-%m-%Y')}")
        open('./data.zip', 'wb').write(response.content)
        with zipfile.ZipFile("./data.zip", "r") as z:
            z.extractall()
        os.remove("./data.zip")
    else:
        st.write("ZIP file request not successful!.")
        return None

def clean_up():
    st.write("Starting clean up")
    csv_files = Path(os.getcwd()).rglob("*.csv")
    for file in csv_files:
        os.remove(file)
    st.write("Done")
    