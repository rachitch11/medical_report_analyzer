import gspread
import streamlit as st
from google.oauth2 import service_account
import random
import smtplib
from email.mime.text import MIMEText

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
    return client.open("MedicalReportUsers").worksheet("users")

def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get("email", "").strip().lower() == email.strip().lower():
            return i + 2, row
    return None, None

def verify_password(stored_password, entered_password):
    return str(stored_password).strip() == str(entered_password).strip()

def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return True
    row, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        get_sheet().update_cell(row, 3, user["usage"] + 1)
        return True
    return False

def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0

def send_otp_email(recipient, otp):
    msg = MIMEText(f"Your OTP for Medical Report Analyzer signup is: {otp}")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = st.secrets["EMAIL_ADDRESS"]
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(st.secrets["EMAIL_ADDRESS"], st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg)

def generate_and_send_otp(email):
    otp = random.randint(1000, 9999)
    send_otp_email(email, otp)
    return otp

def add_new_user(email, password, name, age, gender, otp):
    sheet = get_sheet()
    sheet.append_row([
        email.strip().lower(),
        password.strip(),
        0, 5,
        name.strip(),
        age.strip(),
        gender.strip(),
        str(otp),
        "no"
    ])

def verify_otp(email, entered_otp):
    row, user = get_user_data(email)
    if user and str(user.get("otp")) == str(entered_otp):
        get_sheet().update_cell(row, 9, "yes")  # 9th column is 'verified'
        return True
    return False

def is_verified(email):
    _, user = get_user_data(email)
    return user and user.get("verified", "").lower() == "yes"
