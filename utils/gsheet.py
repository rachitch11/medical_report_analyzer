import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Get gspread client using Streamlit secrets
def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["GCP_CREDS"])
    client = gspread.authorize(creds)
    return client

# Get all data from sheet and return as DataFrame
def get_sheet_data(sheet_key):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_key).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Append a single row or clear and overwrite the sheet
def append_row_to_sheet(sheet_key, row, clear=False):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_key).sheet1

    if clear:
        # Expecting row to be a list of lists (entire DataFrame)
        sheet.clear()
        # Add header row
        sheet.append_row(["name", "email", "password", "age", "gender", "usage_count", "max_usage"])
        # Append all rows
        for r in row:
            sheet.append_row(r)
    else:
        # Append a single row (list)
        sheet.append_row(row)
