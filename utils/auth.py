import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Define the required scopes for Google Sheets and Drive
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Load credentials from Streamlit secrets
if "gcp_service_account" not in st.secrets:
    st.error("Google Cloud credentials not found in st.secrets.")
    st.stop()

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(dict(creds_dict), scopes=SCOPE)

# Initialize the client
client = gspread.authorize(creds)

# Google Sheet name and tab
SHEET_NAME = "MedicalReportAnalyzerUsers"

try:
    sheet = client.open(SHEET_NAME)
    worksheet = sheet.worksheet("users")  # Assumes a tab named "users"
except Exception as e:
    st.error(f"Unable to connect to Google Sheet: {e}")
    st.stop()

# ----------------- Authentication Functions -----------------

def signup(name, email, password, age=None, gender=None):
    """Registers a new user."""
    if is_user_exist(email):
        return False, "User already exists."
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        worksheet.append_row([name, email, password, age, gender, 0, "active", now])
        return True, "Signup successful."
    except Exception as e:
        return False, f"Signup failed: {e}"

def login(email, password):
    """Validates user credentials."""
    try:
        users = worksheet.get_all_records()
        for user in users:
            if user["email"].strip().lower() == email.strip().lower() and user["password"] == password:
                return True, user
        return False, {}
    except Exception as e:
        return False, {}

def is_user_exist(email):
    """Checks if a user with the given email already exists."""
    try:
        users = worksheet.get_all_records()
        for user in users:
            if user["email"].strip().lower() == email.strip().lower():
                return True
        return False
    except Exception:
        return False

def get_user_data(email):
    """Fetches user data based on email."""
    try:
        users = worksheet.get_all_records()
        for user in users:
            if user["email"].strip().lower() == email.strip().lower():
                return user
        return None
    except Exception:
        return None

def increment_usage(email):
    """Increments the usage count for a user."""
    try:
        users = worksheet.get_all_records()
        for i, user in enumerate(users):
            if user["email"].strip().lower() == email.strip().lower():
                new_count = int(user.get("usage_count", 0)) + 1
                worksheet.update_cell(i + 2, 6, new_count)  # Row +2 for headers; col 6 = usage_count
                return new_count
    except Exception:
        pass
    return 0
