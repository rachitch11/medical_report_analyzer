import streamlit as st
import random
import smtplib
import pandas as pd
from email.message import EmailMessage
import datetime
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ SETUP ------------------

# Connect to Google Sheet
@st.cache_resource
def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["EMAIL"]["SHEET_URL"])
    worksheet = sheet.worksheet("users")
    return worksheet

worksheet = get_gsheet()

# ------------------ EMAIL OTP ------------------

def generate_and_send_otp(email):
    otp = str(random.randint(100000, 999999))
    st.session_state.generated_otp = otp
    st.session_state.otp_email = email
    send_otp_email(email, otp)
    return otp

def send_otp_email(email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP for Medical Report Analyzer"
    msg["From"] = st.secrets["EMAIL"]["sender_email"]
    msg["To"] = email
    msg.set_content(f"Your OTP is: {otp}")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(
        st.secrets["EMAIL"]["sender_email"],
        st.secrets["EMAIL"]["sender_password"]
    )
    server.send_message(msg)
    server.quit()

# ------------------ SIGNUP ------------------

def signup_user(name, email, password, age, gender):
    user_id = str(uuid.uuid4())[:8]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usage_count = 0
    max_usage = 10  # default

    worksheet.append_row([
        user_id, name, email, password, age, gender, usage_count, max_usage, timestamp
    ])

def email_exists(email):
    users = worksheet.get_all_records()
    return any(user["email"] == email for user in users)

# ------------------ LOGIN ------------------

def login_user(email, password):
    users = worksheet.get_all_records()
    for user in users:
        if user["email"] == email and user["password"] == password:
            return user
    return None

def increment_usage(email):
    cell = worksheet.find(email)
    row = cell.row
    usage = int(worksheet.cell(row, 7).value) + 1
    worksheet.update_cell(row, 7, usage)

def get_user_info(email):
    users = worksheet.get_all_records()
    for user in users:
        if user["email"] == email:
            return user
    return None
