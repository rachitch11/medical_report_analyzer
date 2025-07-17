import gspread
import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account

# ✅ Admin email with unlimited usage
ADMIN_EMAIL = "rachit87911094@gmail.com"

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --------------------------------------------
# 🔌 Connect to Google Sheet
# --------------------------------------------
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

# --------------------------------------------
# 🔍 Get user record from sheet
# --------------------------------------------
def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get("email", "").strip().lower() == email.strip().lower():
            return i + 2, row  # +2 accounts for 1-based index + header
    return None, None

# --------------------------------------------
# ✅ Add new user (during signup)
# --------------------------------------------
def save_new_user(email, password, name, age, gender, max_usage=5):
    sheet = get_sheet()
    sheet.append_row([
        email.strip().lower(),
        password.strip(),
        0,  # usage
        max_usage,
        name.strip(),
        str(age),
        gender,
        "TRUE",  # verified
        ""       # otp (clear after use)
    ])

# --------------------------------------------
# 🔍 Check if user exists
# --------------------------------------------
def user_exists(email):
    _, user = get_user_data(email)
    return user is not None

# --------------------------------------------
# 🔐 Send OTP to email
# --------------------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email):
    otp = generate_otp()
    sheet = get_sheet()
    row_num, user = get_user_data(email)
    
    if row_num:
        # Update existing user OTP
        sheet.update_cell(row_num, 9, otp)  # OTP = column 9
    else:
        # New signup flow — temp row before verification not added
        pass  # OTP will be verified and row added during signup

    # 🔒 Use your own email + app password
    sender_email = "your_email@gmail.com"
    sender_password = "your_gmail_app_password"

    subject = "Your OTP for Medical Report Analyzer"
    body = f"Your OTP is: {otp}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("❌ Email sending failed:", e)
        return False

# --------------------------------------------
# ✅ Verify entered OTP with stored one
# --------------------------------------------
def verify_otp(email, entered_otp):
    row_num, user = get_user_data(email)
    if user and str(user.get("otp", "")).strip() == entered_otp.strip():
        # ✅ Mark verified and clear OTP
        sheet = get_sheet()
        sheet.update_cell(row_num, 8, "TRUE")  # verified column
        sheet.update_cell(row_num, 9, "")      # clear OTP
        return True
    return False

# --------------------------------------------
# 🔐 Usage tracking
# --------------------------------------------
def update_usage(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return True
    row_num, user = get_user_data(email)
    if user and user["usage"] < user["max_usage"]:
        sheet = get_sheet()
        sheet.update_cell(row_num, 3, user["usage"] + 1)  # usage = column 3
        return True
    return False

def remaining_uses(email):
    if email.strip().lower() == ADMIN_EMAIL.strip().lower():
        return float("inf")
    _, user = get_user_data(email)
    if user:
        return user["max_usage"] - user["usage"]
    return 0
