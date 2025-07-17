import streamlit as st
import gspread
from google.oauth2 import service_account

# Load Google Sheets credentials
try:
    creds_dict = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("MedicalReportAnalyzer").worksheet("Users")
except KeyError:
    st.error("Google Cloud credentials not found in st.secrets.")
    st.stop()
except Exception as e:
    st.error(f"Unable to connect to Google Sheet: {e}")
    st.stop()

def get_all_users():
    try:
        records = sheet.get_all_records()
        return records
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def get_user(email):
    users = get_all_users()
    for user in users:
        if user["email"] == email:
            return user
    return None

def signup(name, email, password, confirm_password, age, gender):
    if password != confirm_password:
        st.error("Passwords do not match.")
        return False

    if get_user(email):
        st.error("User already exists. Please login.")
        return False

    try:
        sheet.append_row([name, email, password, age, gender, 0])  # usage = 0
        return True
    except Exception as e:
        st.error(f"Error during signup: {e}")
        return False

def login(email, password):
    user = get_user(email)
    if not user:
        st.error("User not found.")
        return None
    if user["password"] != password:
        st.error("Incorrect password.")
        return None
    return user

def increment_usage(email):
    users = sheet.get_all_records()
    for i, user in enumerate(users):
        if user["email"] == email:
            new_usage = user["usage"] + 1
            sheet.update_cell(i + 2, 6, new_usage)  # 6th column = usage
            break
