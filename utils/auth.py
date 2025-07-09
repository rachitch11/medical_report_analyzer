import gspread
from oauth2client.service_account import ServiceAccountCredentials
import bcrypt
import json
import streamlit as st

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
ADMIN_EMAIL = "rachit@example.com"  # Your admin email here

def get_sheet():
    try:
        # Local: from file
        creds = ServiceAccountCredentials.from_json_keyfile_name("gcp_credentials.json", SCOPE)
    except:
        # Streamlit Cloud: from secrets
        gcp_creds = json.loads(st.secrets["GCP_CREDS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_creds, SCOPE)

    client = gspread.authorize(creds)
    sheet = client.open("MedicalReportUsers").worksheet("users")  # Use your sheet name
    return sheet

def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row['email'] == email:
            return i + 2, row
    return None, None

def add_new_user(email, password, max_usage=5):
    sheet = get_sheet()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    sheet.append_row([email, hashed_pw, 0, max_usage])

def verify_password(stored_hash, input_password):
    return bcrypt.checkpw(input_password.encode(), stored_hash.encode())

def update_usage(email):
    if email == ADMIN_EMAIL:
        return True
    row_num, user = get_user_data(email)
    if user:
        if user['usage'] < user['max_usage']:
            sheet = get_sheet()
            sheet.update_cell(row_num, 3, user['usage'] + 1)  # Column 3 = usage
            return True
    return False

def remaining_uses(email):
    if email == ADMIN_EMAIL:
        return float('inf')
    _, user = get_user_data(email)
    if user:
        return user['max_usage'] - user['usage']
    return 0
