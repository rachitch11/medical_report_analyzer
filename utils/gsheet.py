import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# ✅ Create GSpread client using Streamlit secrets
def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["GCP_CREDS"])
    client = gspread.authorize(creds)
    return client

# ✅ Get full sheet as DataFrame
def get_sheet_data(sheet_url):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# ✅ Append new row or clear+replace
def append_row_to_sheet(sheet_url, row, clear=False):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_url).sheet1
    if clear:
        sheet.clear()
        sheet.append_row(["name", "email", "password", "age", "gender", "usage_count", "max_usage"])
        for r in row:
            sheet.append_row(r)
    else:
        sheet.append_row(row)

# ✅ Final fixed: Update usage count by row number
def update_usage_count(sheet_url, row_number, new_count):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_url).sheet1
    usage_col = 6 + 1  # "usage_count" is the 6th field (0-indexed), so column 7
    sheet.update_cell(row_number, usage_col, new_count)
