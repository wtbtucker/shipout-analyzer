import pandas as pd
import numpy as np
import streamlit as st
from st_files_connection import FilesConnection
import boto3


conn = st.connection("s3", type=FilesConnection)
# Load RICS Inventory detail report for only footwear
inventory_detail = conn.read("rics-file-exports/InventoryDetail.csv", input_format="csv", ttl=600)

inventory_detail["InventoryDate"] = pd.to_datetime(inventory_detail["InventoryDate"], format="%m/%d/%Y", errors="coerce")
st.write(f"Start date: {inventory_detail["InventoryDate"].max()}")
st.write(f"End date: {inventory_detail["InventoryDate"].min()}")

# Each shipout request should have a corresponding transfer out and transfer in
# Use transfer in since the transaction takes place at the requesting store (what we are interested in tracking)
# Will shipouts request from Amazon inventory which do not have a transfer in RICS
transfers = inventory_detail[inventory_detail["InventoryType"]=="Transfer In"]

# Filter to transfers which use naming convention for shipouts
shipouts = transfers[transfers["Comment"].str.startswith("TO# SHP", na=False)]
st.write(f"Total number of shipouts: {shipouts["Qty"].sum()}")

sales = inventory_detail[inventory_detail["InventoryType"]=="Sale"]
st.write(f"Total sales: {-1 * sales["Qty"].sum()}")

shipouts_by_store = (
    shipouts
    .groupby("InventoryStore")
    .agg(
        shipout_count=("Qty", "sum")
    )
)

sales_by_store = (
    sales
    .groupby("InventoryStore")
    .agg(total_sales=("Qty", "sum"))    
)
sales_by_store["total_sales"] = -1*sales_by_store["total_sales"]

# shipouts as a percentage of units sold
combined = pd.merge(sales_by_store, shipouts_by_store, left_index=True, right_index=True)
combined["shipout_percent_of_sales"] = combined["shipout_count"] / combined["total_sales"]

established_combined = combined[~combined.index.isin([31, 32, 9])].copy()
st.write(established_combined.sort_values(by="shipout_percent_of_sales", ascending=False))