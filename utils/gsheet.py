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

# ✅ Update usage count in the sheet
def update_usage_count(sheet_url, email, new_count):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_url).sheet1
    records = sheet.get_all_records()
    for idx, row in enumerate(records):
        if row["email"] == email:
            cell_row = idx + 2  # +2 because header is row 1 and gspread is 1-indexed
            usage_col = list(row.keys()).index("usage_count") + 1
            sheet.update_cell(cell_row, usage_col, new_count)
            break
