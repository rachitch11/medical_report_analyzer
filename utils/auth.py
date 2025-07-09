import gspread
import bcrypt
import streamlit as st
from google.oauth2 import service_account

ADMIN_EMAIL = "rachit@example.com"  # Replace with your admin email
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Get Google Sheet client
def get_sheet():
    try:
        # Local use: JSON file present
        credentials = service_account.Credentials.from_service_account_file(
            "gcp_credentials.json", scopes=SCOPE
        )
    except Exception:
        # Streamlit Cloud: use secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["GCP_CREDS"], scopes=SCOPE
        )

    client = gspread.authorize(credentials)
    sheet = client.open("MedicalReportUsers").worksheet("users")
    return sheet

# Fetch row and user data
def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row["email"] == email:
            return i + 2, row  # +2 because of header and 1-indexing
    return None, None

# Add new user with hashed password
def add_new_user(email, password, max_usage=5):
    sheet = get_sheet()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    sheet.append_row([email, hashed_pw, 0, max_usage])  # email, hash, usage=0, max_usage

# Check password match
def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())

# Update usage count (unless admin)
def update_usage(email):
    if email == ADMIN_EMAIL:
        return True  # unlimited usage
    row_num, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user["usage"] + 1)  # 3 = usage column
        return True
    return False

# Remaining usage logic
def remaining_uses(email):
    if email == ADMIN_EMAIL:
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0
