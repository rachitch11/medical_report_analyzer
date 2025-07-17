import gspread
import streamlit as st
from google.oauth2 import service_account
import random

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
            return i + 2, row  # row_num for updating
    return None, None

def add_new_user(email, password, name, age, gender, max_usage=5):
    sheet = get_sheet()
    sheet.append_row([email.strip().lower(), password.strip(), 0, max_usage, name.strip(), age, gender, False, ""])

def verify_password(stored_password, entered_password):
    return str(stored_password).strip() == str(entered_password).strip()

def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return True
    row_num, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user["usage"] + 1)  # usage column
        return True
    return False

def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0

def set_otp(email, otp):
    row_num, user = get_user_data(email)
    if row_num:
        sheet = get_sheet()
        sheet.update_cell(row_num, 9, otp)  # otp column

def verify_otp(email, entered_otp):
    _, user = get_user_data(email)
    return user and str(user.get("otp")) == str(entered_otp)

def set_verified(email):
    row_num, user = get_user_data(email)
    if row_num:
        sheet = get_sheet()
        sheet.update_cell(row_num, 8, "TRUE")  # verified column

def is_verified(email):
    _, user = get_user_data(email)
    return user and str(user.get("verified", "")).strip().lower() == "true"

def generate_otp():
    return str(random.randint(100000, 999999))
