import gspread
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from google.oauth2 import service_account

# ✅ Admin email with unlimited usage
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
    sheet = client.open("MedicalReportUsers").worksheet("users")
    return sheet

def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get("email", "").strip().lower() == email.strip().lower():
            return i + 2, row  # +2 for header and 1-based index
    return None, None

def add_new_user(email, password, name, age="", gender="", max_usage=5, verified="", otp=""):
    sheet = get_sheet()
    sheet.append_row([
        email.strip().lower(),
        password.strip(),
        0,
        max_usage,
        name.strip(),
        age,
        gender,
        verified,
        otp
    ])

def verify_password(stored_password, entered_password):
    try:
        return str(stored_password).strip() == str(entered_password).strip()
    except Exception:
        return False

def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return True
    row_num, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user["usage"] + 1)  # usage is 3rd column
        return True
    return False

def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0

def send_otp_email(recipient_email, otp_code):
    try:
        smtp_config = st.secrets["email_config"]
        sender_email = smtp_config["from_email"]
        smtp_username = smtp_config["smtp_username"]
        smtp_password = smtp_config["smtp_password"]
        smtp_server = smtp_config["smtp_server"]
        smtp_port = smtp_config["smtp_port"]

        msg = MIMEText(f"Your OTP for Medical Report Analyzer signup is: {otp_code}")
        msg['Subject'] = "🔐 Your OTP for Signup Verification"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email sending error:", e)
        return False
