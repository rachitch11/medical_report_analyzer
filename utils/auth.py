import gspread
import bcrypt
import streamlit as st
from google.oauth2 import service_account

# Constants
ADMIN_EMAIL = "rachit@example.com"  # admin has unlimited usage

def get_sheet():
    """Returns the worksheet object from Google Sheets"""
    # Use Streamlit secrets (works both locally and on Streamlit Cloud)
    credentials = service_account.Credentials.from_service_account_info(st.secrets["GCP_CREDS"])
    client = gspread.authorize(credentials)
    sheet = client.open("MedicalReportUsers").worksheet("users")  # Make sure this name matches exactly
    return sheet

def get_user_data(email):
    """Fetch user row number and data by email"""
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row["email"] == email:
            return i + 2, row  # +2 to account for header and 1-based index
    return None, None

def add_new_user(email, password, max_usage=5):
    """Add a new user with hashed password and default usage"""
    sheet = get_sheet()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    sheet.append_row([email, hashed_pw, 0, max_usage])  # [email, password, usage, max_usage]

def verify_password(stored_hash, entered_password):
    """Check entered password against stored hash"""
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())

def update_usage(email):
    """Increment usage count if user has remaining quota (except admin)"""
    if email == ADMIN_EMAIL:
        return True
    row_num, user = get_user_data(email)
    if user and user['usage'] < user['max_usage']:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user['usage'] + 1)  # column 3 = usage
        return True
    return False

def remaining_uses(email):
    """Return remaining usage quota"""
    if email == ADMIN_EMAIL:
        return float('inf')
    _, user = get_user_data(email)
    if user:
        return user['max_usage'] - user['usage']
    return 0
