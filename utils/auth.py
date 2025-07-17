import gspread
from google.oauth2.service_account import Credentials

# --- Setup ---
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS = Credentials.from_service_account_file("secrets.json", scopes=SCOPE)
client = gspread.authorize(CREDS)
sheet = client.open("MedicalReportUsers").sheet1  # Make sure this sheet name is correct

def get_sheet():
    return sheet

# --- Get User Data by Email ---
def get_user_data(email):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row["email"].strip().lower() == email.strip().lower():
            return i + 2, row  # +2 to match Google Sheets row index
    return None, None

# --- Add New User ---
def add_new_user(email, password, name, age, gender, max_usage=5):
    sheet = get_sheet()
    sheet.append_row([
        email.strip().lower(),
        password.strip(),
        0,  # usage
        max_usage,
        name.strip(),
        age,
        gender,
        "no",  # verified
        ""     # otp
    ])

# --- Password Check ---
def verify_password(stored_pw, entered_pw):
    return stored_pw.strip() == entered_pw.strip()

# --- Update Usage Count ---
def update_usage(row_num):
    sheet = get_sheet()
    usage = int(sheet.cell(row_num, 3).value)
    sheet.update_cell(row_num, 3, usage + 1)

# --- Remaining Uses ---
def remaining_uses(user):
    max_usage = user["max_usage"]
    usage = user["usage"]
    return "Unlimited" if max_usage == "unlimited" else int(max_usage) - int(usage)
