import gspread
import bcrypt
import streamlit as st
from google.oauth2 import service_account

ADMIN_EMAIL = "rachit@example.com"

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    try:
        # ✅ Local run - from file
        credentials = service_account.Credentials.from_service_account_file(
            "gcp_credentials.json", scopes=SCOPE
        )
        st.write("✅ Loaded ")
    except:
        # ✅ Streamlit Cloud - from secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["GCP_CREDS"],
            scopes=SCOPE
        )
        st.write("✅ Loaded")

    client = gspread.authorize(credentials)
    sheet = client.open("MedicalReportUsers").worksheet("users")
    return sheet

def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get('email') == email:
            return i + 2, row  # +2 for 1-based row number and header
    return None, None

def add_new_user(email, password, max_usage=5):
    sheet = get_sheet()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    sheet.append_row([email, hashed_pw, 0, max_usage])

def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())

def update_usage(email):
    if email == ADMIN_EMAIL:
        return True
    row_num, user = get_user_data(email)
    if user and user.get('usage', 0) < user.get('max_usage', 0):
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user['usage'] + 1)  # usage is 3rd column
        return True
    return False

def remaining_uses(email):
    if email == ADMIN_EMAIL:
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user.get('max_usage', 0) - user.get('usage', 0)
    return 0
