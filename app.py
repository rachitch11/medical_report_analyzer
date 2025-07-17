import streamlit as st
from utils.auth import (
    send_otp_email, verify_otp, set_verified,
    get_user_data, save_new_user, update_usage,
    remaining_uses, user_exists
)
from utils.report_parser import parse_medical_report
from utils.gpt_analysis import analyze_reports

st.set_page_config(page_title="🧠 Medical Report Analyzer", layout="centered")

# Initialize session state
for key in ["authenticated", "email", "name", "reports", "signup_info", "otp_email"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "authenticated" else False

st.title("🧠 Medical Report Analyzer (PDF & Image)")
st.caption("Upload medical reports to get a summary, trends, and abnormalities using GPT-4.")

# -------------------- 🔐 LOGIN/SIGNUP --------------------
if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("📧 Enter your email to login")

        if st.button("Send OTP", key="login_otp_btn"):
            if not email:
                st.warning("⚠️ Please enter your email.")
            elif not user_exists(email):
                st.error("❌ User not found. Please sign up first.")
            elif send_otp_email(email):
                st.success("✅ OTP sent to your email.")
                st.session_state.otp_email = email
            else:
                st.error("❌ Failed to send OTP. Try again.")

        if st.session_state.otp_email:
            login_otp = st.text_input("🔐 Enter OTP to Login", max_chars=6)
            if st.button("Verify & Login"):
                if verify_otp(st.session_state.otp_email, login_otp):
                    user = get_user_data(st.session_state.otp_email)
                    if user and str(user.get("verified", "")).lower() in ["yes", "true"]:
                        st.session_state.authenticated = True
                        st.session_state.email = st.session_state.otp_email
                        st.session_state.name = user.get("name", "")
                        st.success(f"✅ Welcome, {st.session_state.name}. You have {remaining_uses(email)} uses remaining.")
                        st.rerun()
                    else:
                        st.error("❌ Account not verified.")
                else:
                    st.error("❌ Invalid OTP.")

    # ---------------- SIGNUP ----------------
    with tab2:
        name = st.text_input("👤 Full Name")
        signup_email = st.text_input("📧 Email")
        age = st.number_input("🎂 Age", min_value=1, step=1)
        gender = st.selectbox("⚧️ Gender", ["Male", "Female", "Other"])
        password = st.text_input("🔐 Password", type="password")
        confirm_password = st.text_input("🔁 Confirm Password", type="password")

        if st.button("Send OTP", key="signup_otp_btn"):
            if user_exists(signup_email):
                st.error("❌ User already exists. Please login.")
            elif not all([name, signup_email, age, gender, password, confirm_password]):
                st.warning("⚠️ Please fill all fields.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                st.session_state.signup_info = {
                    "name": name,
                    "email": signup_email,
                    "age": age,
                    "gender": gender,
                    "password": password
                }
                if send_otp_email(signup_email):
                    st.success("✅ OTP sent. Please verify below.")
                else:
                    st.error("❌ Failed to send OTP.")

        if st.session_state.signup_info:
            signup_otp = st.text_input("🔐 Enter OTP to Sign Up", max_chars=6)
            if st.button("Verify & Create Account"):
                info = st.session_state.signup_info
                if verify_otp(info["email"], signup_otp):
                    save_new_user(
                        info["email"], info["password"], info["name"],
                        info["age"], info["gender"]
                    )
                    set_verified(info["email"])
                    st.success("✅ Signup complete. You are now logged in.")
                    st.session_state.authenticated = True
                    st.session_state.email = info["email"]
                    st.session_state.name = info["name"]
                    st.rerun()
                else:
                    st.error("❌ Invalid OTP. Try again.")

# -------------------- MAIN APP --------------------
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
