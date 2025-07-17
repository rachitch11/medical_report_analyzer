import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# Define the required scope for Google Sheets and Drive
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(dict(creds_dict), scopes=SCOPE)

# Initialize the client
client = gspread.authorize(creds)

# Google Sheet name
SHEET_NAME = "MedicalReportAnalyzerUsers"

# Open sheet
sheet = client.open(SHEET_NAME)
worksheet = sheet.worksheet("users")  # Assumes your sheet has a tab named "users"

# ----------------- Authentication Functions -----------------

def signup(name, email, password, age=None, gender=None):
    """Registers a new user."""
    if is_user_exist(email):
        return False, "User already exists."
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([name, email, password, age, gender, 0, "active", now])
    return True, "Signup successful."

def login(email, password):
    """Validates user credentials."""
    users = worksheet.get_all_records()
    for user in users:
        if user["email"] == email and user["password"] == password:
            return True, user
    return False, {}

def is_user_exist(email):
    """Checks if a user with the given email already exists."""
    users = worksheet.get_all_records()
    for user in users:
        if user["email"] == email:
            return True
    return False

def get_user_data(email):
    """Fetches user data based on email."""
    users = worksheet.get_all_records()
    for user in users:
        if user["email"] == email:
            return user
    return None

def increment_usage(email):
    """Increments the usage count for a user."""
    users = worksheet.get_all_records()
    for i, user in enumerate(users):
        if user["email"] == email:
            new_count = int(user["usage_count"]) + 1
            worksheet.update_cell(i + 2, 6, new_count)  # Row offset +2 for headers, col 6 = usage_count
            return new_count
    return 0
