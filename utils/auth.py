import gspread
import streamlit as st
from google.oauth2 import service_account

ADMIN_EMAIL = "rachit@example.com"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "gcp_credentials.json", scopes=SCOPE
        )
    except:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["GCP_CREDS"], scopes=SCOPE
        )
    client = gspread.authorize(credentials)
    sheet = client.open("MedicalReportUsers").worksheet("users")
    return sheet

def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get("email") == email:
            return i + 2, row  # row number, data
    return None, None

def add_new_user(email, password, name, max_usage=5):
    sheet = get_sheet()
    sheet.append_row([email, password, 0, max_usage, name])

def update_usage(email):
    if email == ADMIN_EMAIL:
        return True
    row_num, user = get_user_data(email)
    if user and user['usage'] < user['max_usage']:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user['usage'] + 1)
        return True
    return False

def remaining_uses(email):
    if email == ADMIN_EMAIL:
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user['max_usage'] - user['usage']
    return 0
