import gspread
import streamlit as st
from google.oauth2 import service_account

# ✅ Admin email with unlimited usage
ADMIN_EMAIL = "rachit87911094@gmail.com"

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
        if row.get("email", "").strip().lower() == email.strip().lower():
            return i + 2, row  # +2 for header and 1-based index
    return None, None

def add_new_user(email, password, name, max_usage=5):
    sheet = get_sheet()
    sheet.append_row([email.strip().lower(), password.strip(), 0, max_usage, name.strip()])

def verify_password(stored_password, entered_password):
    return stored_password.strip() == entered_password.strip()

def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return True
    row_num, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user["usage"] + 1)  # usage is 3rd column
        return True
    return False

def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0
