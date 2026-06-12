import pandas as pd
import streamlit as st
from st_files_connection import FilesConnection
from datetime import datetime, timedelta

def get_start_date(date_option: str) -> datetime:
    today = datetime.today()

    if date_option == "month_to_date":
        return datetime(today.year, today.month, 1)

    if date_option == "year_to_date":
        return datetime(today.year, 1, 1)

    if date_option == "quarter_to_date":
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        return datetime(today.year, quarter_start_month, 1)

    if date_option == "last_30_days":
        return today - timedelta(days=30)

    if date_option == "last_90_days":
        return today - timedelta(days=90)

    raise ValueError(f"Unknown date option: {date_option}")

def filter_transactions(start_date: datetime, df: pd.DataFrame) -> pd.DataFrame:
    # start_date has format MM/DD/YYYY
    start_dt = pd.to_datetime(start_date)

    retail_stores = [
        1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16,
        17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        30, 31, 32, 33
    ]

    df = df.copy()
    df["InventoryDate"] = pd.to_datetime(df["InventoryDate"], format="%m/%d/%Y")

    first_txn = (
        df[df["InventoryStore"].isin(retail_stores)]
        .groupby("InventoryStore")["InventoryDate"]
        .min()
    )

    stores_to_include = first_txn[first_txn <= start_dt].index

    return df[(df["InventoryStore"].isin(stores_to_include))&(df["InventoryDate"]>=start_dt)]

def compute_shipouts_by_store(df: pd.DataFrame) -> pd.DataFrame:
    transfers = df[df["InventoryType"]=="Transfer In"]
    shipouts = transfers[transfers["Comment"].str.startswith("TO# SHP", na=False)]
    shipouts_by_store = (
        shipouts
            .groupby("InventoryStore")
            .agg(
                shipout_units_requested=("Qty", "sum")
            )
    )

    sales = df[df["InventoryType"]=="Sale"]
    sales_by_store = (
        sales
        .groupby("InventoryStore")
        .agg(total_units_sold=("Qty", "sum"))
    )
    sales_by_store["total_units_sold"] = -1*sales_by_store["total_units_sold"]
    
    combined = pd.merge(sales_by_store, shipouts_by_store, left_index=True, right_index=True)
    combined["shipout_percent_of_sales"] = combined["shipout_units_requested"] / combined["total_units_sold"]    
    return combined

conn = st.connection("s3", type=FilesConnection)
# Load RICS Inventory detail report for only footwear
inventory_detail = conn.read("rics-file-exports/InventoryDetail.csv", input_format="csv", ttl=600)

date_option = st.selectbox(
    "Date range",
    [
        "month_to_date",
        "quarter_to_date",
        "year_to_date",
        "last_30_days",
        "last_90_days",
    ],
)

start_date = get_start_date(date_option=date_option)
filtered_df = filter_transactions(start_date, inventory_detail)
shipouts_by_store = compute_shipouts_by_store(filtered_df)

st.write(f"Start date: {start_date}")
total_shipouts = shipouts_by_store["shipout_units_requested"].sum()
st.write(f"Total number of shipouts: {total_shipouts}")
total_units_sold = shipouts_by_store["total_units_sold"].sum()
st.write(f"Total sales: {total_units_sold}")
shipout_percentage = (total_shipouts / total_units_sold) * 100
st.write(f"Average shipout percentage: {shipout_percentage:.2f}%")
st.write(shipouts_by_store.sort_values(by="shipout_percent_of_sales", ascending=False))