import streamlit as st
import sys
import os

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.db.pg_controller import PGController
from src.data.data_processor import load_data, calc_up_to_date, patching_db

controller = PGController()

uploaded_file = st.file_uploader("Choose a file", type={"csv"})

if uploaded_file is not None:  
    if st.button("Load"):
        df = load_data(uploaded_file)
        calc_up_to_date()
        "Data loaded"
        df
  