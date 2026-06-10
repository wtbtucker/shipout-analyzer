import pandas as pd
import numpy as np
import streamlit as st
from st_files_connection import FilesConnection

conn = st.connection("s3", type=FilesConnection)
upc_file = conn.read("rics-file-exports/upc_export.csv", input_format="csv", ttl=600)
print("UPC export length", len(upc_file))