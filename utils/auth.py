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

# ⬇️ Load Google Sheet
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

# ⬇️ Get row index and user record by email
def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get("email", "").strip().lower() == email.strip().lower():
            return i + 2, row  # +2 for 1-based index + header
    return None, None

# ⬇️ Compare passwords
def verify_password(stored_password, entered_password):
    return str(stored_password).strip() == str(entered_password).strip()

# ⬇️ Increment usage count if within limit
def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return True
    row, user = get_user_data(email)
    if user and int(user.get("usage", 0)) < int(user.get("max_usage", 0)):
        get_sheet().update_cell(row, 3, int(user["usage"]) + 1)
        return True
    return False

# ⬇️ Remaining uses for user
def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return int(user.get("max_usage", 0)) - int(user.get("usage", 0))
    return 0

# ⬇️ Send OTP email
def send_otp_email(recipient, otp):
    msg = MIMEText(f"Your OTP for Medical Report Analyzer signup is: {otp}")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = st.secrets["EMAIL_ADDRESS"]
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(st.secrets["EMAIL_ADDRESS"], st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg)

# ⬇️ Generate OTP and send email
def generate_and_send_otp(email):
    otp = random.randint(1000, 9999)
    send_otp_email(email, otp)
    return otp

# ⬇️ Add new user with OTP verification info
def add_new_user(email, password, name, age, gender, otp):
    sheet = get_sheet()
    sheet.append_row([
        email.strip().lower(),
        password.strip(),
        0,  # usage
        5,  # max_usage
        name.strip(),
        str(age).strip(),
        gender.strip().lower(),
        str(otp),
        "no"  # verified
    ])

# ⬇️ Verify entered OTP
def verify_otp(email, entered_otp):
    row, user = get_user_data(email)
    if user and str(user.get("otp")).strip() == str(entered_otp).strip():
        get_sheet().update_cell(row, 9, "yes")  # 9th column is 'verified'
        return True
    return False

# ⬇️ Check if user has verified OTP
def is_verified(email):
    _, user = get_user_data(email)
    return user and user.get("verified", "").strip().lower() == "yes"
