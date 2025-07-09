import streamlit as st
import os
from utils.pdf_reader import extract_text_and_date
from utils.report_parser import extract_parameters, extract_tumor_sizes
from utils.gpt_analysis import analyze_reports
from datetime import datetime
import matplotlib.pyplot as plt

# 🔐 Import auth helper
from utils.auth import (
    get_user_data,
    update_usage,
    remaining_uses,
    add_new_user,
    verify_password
)

st.set_page_config(page_title="Medical Report Analyzer", layout="wide")

st.title("🧠 Medical Report Analyzer (PDF & Image)")
st.markdown("Upload one or more medical reports to get a summary, trends, and abnormalities using GPT-4.")

# 🔐 Login or Signup Section
auth_mode = st.radio("Login or Sign Up", ["Login", "Sign Up"])
email = st.text_input("📧 Enter your email")
password = st.text_input("🔐 Enter your password", type="password")

if email and password:
    row_num, user_data = get_user_data(email)

    if auth_mode == "Login":
        if not user_data:
            st.error("❌ Email not found. Please sign up first.")
            st.stop()
        if not verify_password(user_data["password_hash"], password):
            st.error("❌ Incorrect password.")
            st.stop()
        rem = remaining_uses(email)
        st.success(f"✅ Welcome, {email}. You have **{rem} uses remaining**.")
        if rem <= 0:
            st.error("❌ You've reached your usage limit. Please contact support.")
            st.stop()

    elif auth_mode == "Sign Up":
        if user_data:
            st.warning("⚠️ Email already exists. Please login.")
            st.stop()
        add_new_user(email, password, max_usage=5)
        st.success("✅ Account created! You have 5 uses.")
        rem = 5
