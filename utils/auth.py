import gspread
from google.oauth2.service_account import Credentials
import random

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("gcp_credentials.json", scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open("MedicalReportUsers").worksheet("users")

ADMIN_EMAIL = "rachit87911094@gmail.com"

def get_user_data(email):
    data = sheet.get_all_records()
    for idx, row in enumerate(data):
        if row["email"].strip().lower() == email.strip().lower():
            return idx + 2, row
    return None, None

def user_exists(email):
    _, user = get_user_data(email)
    return user is not None

def save_new_user(email, password, name, age, gender, max_usage=5):
    sheet.append_row([
        email.lower(), password, 0, max_usage, name, age, gender, "no", ""
    ])

def send_otp_email(email):
    otp = str(random.randint(100000, 999999))
    row_num, user = get_user_data(email)
    if row_num:
        sheet.update_cell(row_num, 9, otp)
    else:
        # pre-store during signup flow if user doesn't yet exist
        sheet.append_row([email, "", 0, 5, "", "", "", "no", otp])
    # simulate sending OTP
    print(f"Simulated OTP sent to {email}: {otp}")
    return True

def verify_otp(email, entered_otp):
    row_num, user = get_user_data(email)
    return user and str(user.get("otp", "")).strip() == str(entered_otp).strip()

def set_verified(email):
    row_num, _ = get_user_data(email)
    sheet.update_cell(row_num, 8, "yes")  # column 8 = verified
    sheet.update_cell(row_num, 9, "")     # clear OTP

def update_usage(email):
    if email.lower() == ADMIN_EMAIL.lower():
        return True
    row_num, user = get_user_data(email)
    if user and int(user["usage"]) < int(user["max_usage"]):
        sheet.update_cell(row_num, 3, int(user["usage"]) + 1)
        return True
    return False

def remaining_uses(user):
    if user["email"].strip().lower() == ADMIN_EMAIL:
        return "∞"
    return int(user["max_usage"]) - int(user["usage"])
