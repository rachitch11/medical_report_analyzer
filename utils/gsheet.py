import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["GCP_CREDS"])
    client = gspread.authorize(creds)
    return client

def get_sheet_data(sheet_url):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

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

