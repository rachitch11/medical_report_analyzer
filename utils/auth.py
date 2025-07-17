import gspread
import random
import streamlit as st
from google.oauth2 import service_account

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
            return i + 2, row  # 1-based + header
    return None, None

def add_new_user(email, password, name, age, gender, otp, max_usage=5):
    sheet = get_sheet()
    sheet.append_row([
        email.strip().lower(), password.strip(), 0, max_usage,
        name.strip(), age.strip(), gender.strip(), "no", otp
    ])

def update_otp(email, otp):
    row, _ = get_user_data(email)
    if row:
        sheet = get_sheet()
        sheet.update_cell(row, 9, otp)

def mark_verified(email):
    row, _ = get_user_data(email)
    if row:
        sheet = get_sheet()
        sheet.update_cell(row, 8, "yes")

def verify_password(stored_password, entered_password):
    return str(stored_password).strip() == str(entered_password).strip()

def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL:
        return True
    row_num, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user["usage"] + 1)
        return True
    return False

def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL:
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0
