import streamlit as st
import random
from utils.auth import (
    get_user_data, verify_password,
    add_new_user, update_usage, remaining_uses,
    send_otp_email
)
from utils.report_parser import parse_medical_report
from utils.gpt_analysis import analyze_reports

st.set_page_config(page_title="🧠 Medical Report Analyzer", layout="centered")

# Initialize session state
for key in ["authenticated", "email", "name", "reports", "signup_otp_sent", "signup_otp"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "authenticated" else False

st.title("🧠 Medical Report Analyzer (PDF & Image)")
st.caption("Upload one or more medical reports to get a summary, trends, and abnormalities using GPT-4.")

if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab1:
        email = st.text_input("📧 Enter your email", key="login_email")
        password = st.text_input("🔐 Enter your password", type="password", key="login_password")

        if st.button("Login"):
            _, user = get_user_data(email)
            if user and verify_password(user.get("password", ""), password):
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.name = user.get("name", "")
                st.success(f"✅ Welcome, {st.session_state.name}. You have {remaining_uses(email)} uses remaining.")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    with tab2:
        name = st.text_input("👤 Your name", key="signup_name")
        new_email = st.text_input("📧 New email", key="signup_email")
        new_password = st.text_input("🔐 New password", type="password", key="signup_password")
        confirm_password = st.text_input("🔁 Confirm password", type="password", key="signup_confirm")
        age = st.number_input("🎂 Your age", min_value=0, max_value=120, key="signup_age")
        gender = st.selectbox("🚻 Gender", ["Male", "Female", "Other", "Prefer not to say"], key="signup_gender")

        if not st.session_state.signup_otp_sent and st.button("📨 Send OTP to Email"):
            otp = str(random.randint(100000, 999999))
            success = send_otp_email(new_email, otp)
            if success:
                st.session_state.signup_otp = otp
                st.session_state.signup_otp_sent = True
                st.success("✅ OTP sent to your email.")
            else:
                st.error("❌ Failed to send OTP. Please try again.")

        if st.session_state.signup_otp_sent:
            entered_otp = st.text_input("🔐 Enter the OTP sent to your email", key="signup_otp")

            if st.button("Sign Up"):
                _, user = get_user_data(new_email)
                if user:
                    st.error("❌ User already exists")
                elif not all([name, new_email, new_password, confirm_password, age, gender]):
                    st.warning("⚠️ Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif entered_otp != st.session_state.signup_otp:
                    st.error("❌ Invalid OTP")
                else:
                    add_new_user(new_email, new_password, name, age, gender, verified="yes", otp=st.session_state.signup_otp)
                    st.success("✅ Account created. You can log in now.")
                    st.session_state.signup_otp_sent = False
                    st.session_state.signup_otp = None

else:
    st.success(f"✅ Logged in as {st.session_state.name} ({st.session_state.email}) — Remaining uses: {remaining_uses(st.session_state.email)}")

    uploaded_files = st.file_uploader(
        "📁 Upload your medical reports (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        report_data = []
        for file in uploaded_files:
            try:
                report = parse_medical_report(file)
                report_data.append(report)
            except Exception as e:
                st.error(f"❌ Error in {file.name}: {e}")

        st.session_state.reports = report_data

        if st.button("🧠 Analyze Reports") and report_data:
            if update_usage(st.session_state.email):
                with st.spinner("Analyzing with GPT..."):
                    result = analyze_reports(report_data)

                st.subheader("📋 Summary")
                st.write(result["summary"])

                st.subheader("📊 Detailed Report")
                st.dataframe(result["abnormal_table"], use_container_width=True)
            else:
                st.error("❌ Usage limit reached.")

    if st.button("Logout"):
        st.session_state.clear()
        st.success("✅ Logged out successfully.")
        st.rerun()
