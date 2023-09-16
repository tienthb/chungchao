import sys
import os
import streamlit as st

# directory reach
directory = os.path.dirname(os.path.abspath("__file__"))
 
# setting path
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.data.data_processor import patching_db

if st.button("Patching DB"):
    patching_db()
    "Done"