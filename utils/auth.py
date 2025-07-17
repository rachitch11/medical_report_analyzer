import streamlit as st
import pandas as pd
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.gsheet import get_sheet_data, append_row_to_sheet

# Load secrets
SHEET_URL = st.secrets["EMAIL"]["SHEET_URL"]
SENDER_EMAIL = st.secrets["EMAIL"]["sender_email"]
SENDER_PASSWORD = st.secrets["EMAIL"]["sender_password"]

def get_user_sheet():
    return get_sheet_data(SHEET_URL)

def user_exists(email):
    df = get_user_sheet()
    return df[df['email'] == email].shape[0] > 0

def send_otp_email(receiver_email, otp):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = 'Your OTP for Signup Verification'

    body = f'Your OTP for signup verification is: {otp}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print("Error sending OTP:", e)
        return False

def signup(name, email, password, age, gender):
    if user_exists(email):
        st.error("User already exists. Please login.")
        return False

    otp = str(random.randint(100000, 999999))
    sent = send_otp_email(email, otp)
    if not sent:
        st.error("Failed to send OTP. Please try again.")
        return False

    st.session_state.otp_expected = otp
    st.session_state.new_user = {
        'name': name,
        'email': email,
        'password': password,
        'age': age,
        'gender': gender,
        'usage_count': 0,
        'max_usage': 5
    }

    return True  # OTP sent successfully

def verify_otp(otp_entered):
    if "otp_expected" not in st.session_state or "new_user" not in st.session_state:
        st.error("No OTP session found. Please start signup again.")
        return False

    if otp_entered != st.session_state.otp_expected:
        st.error("Incorrect OTP. Please try again.")
        return False

    # Append new user to sheet only after successful OTP
    new_user = st.session_state.new_user
    append_row_to_sheet(SHEET_URL, [
        new_user['name'],
        new_user['email'],
        new_user['password'],
        new_user['age'],
        new_user['gender'],
        new_user['usage_count'],
        new_user['max_usage']
    ])

    # Clean up session
    del st.session_state.otp_expected
    del st.session_state.new_user

    st.success("Signup successful! Please login.")
    return True

def login(email, password):
    df = get_user_sheet()
    user_row = df[(df['email'] == email) & (df['password'] == password)]
    if not user_row.empty:
        return user_row.iloc[0].to_dict()
    else:
        return None

def increment_usage(email):
    df = get_user_sheet()
    index = df.index[df['email'] == email].tolist()
    if index:
        idx = index[0]
        max_usage = df.at[idx, 'max_usage']
        if max_usage != "unlimited":
            df.at[idx, 'usage_count'] = int(df.at[idx, 'usage_count']) + 1
        append_row_to_sheet(SHEET_URL, df.values.tolist(), clear=True)

def get_user_info(email):
    df = get_user_sheet()
    row = df[df['email'] == email]
    if not row.empty:
        return row.iloc[0].to_dict()
    return None
