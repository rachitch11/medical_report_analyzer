import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Define Google Sheets scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate using Streamlit secrets
try:
    creds_dict = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sheet = client.open("MedicalReportAnalyzer").worksheet("Users")

except KeyError:
    st.error("Google Cloud credentials not found in st.secrets.")
    st.stop()
except Exception as e:
    st.error(f"Unable to connect to Google Sheet: {e}")
    st.stop()


# User-related helper functions

def get_user_data(email):
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        if record["email"].lower() == email.lower():
            return i + 2, record  # account for header row
    return None, None


def login(email, password):
    _, user = get_user_data(email)
    if user and user["password"] == password:
        return True, user
    return False, None


def signup(name, email, password, age, gender):
    _, existing_user = get_user_data(email)
    if existing_user:
        return False, "User already exists."
    sheet.append_row([name, email, password, age, gender, 0])
    return True, "Signup successful!"


def increment_usage(email):
    row, user = get_user_data(email)
    if row:
        current_usage = int(user.get("usage_count", 0))
        sheet.update_cell(row, 6, current_usage + 1)


def get_user_info(email):
    _, user = get_user_data(email)
    return user
