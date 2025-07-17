import streamlit as st
from utils.auth import (
    get_user_data, verify_password,
    add_new_user, update_usage, remaining_uses,
    generate_and_send_otp, verify_otp, is_verified
)
from utils.report_parser import parse_medical_report
from utils.gpt_analysis import analyze_reports

st.set_page_config(page_title="🧠 Medical Report Analyzer", layout="centered")

for key in ["authenticated", "email", "name", "reports"]:
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
                if is_verified(email):
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.session_state.name = user.get("name", "")
                    st.success(f"✅ Welcome, {st.session_state.name}. You have {remaining_uses(email)} uses remaining.")
                    st.rerun()
                else:
                    st.error("❌ Email not verified. Please complete signup and verify OTP.")
            else:
                st.error("❌ Invalid credentials")

    with tab2:
        name = st.text_input("👤 Your name", key="signup_name")
        new_email = st.text_input("📧 New email", key="signup_email")
        new_password = st.text_input("🔐 New password", type="password", key="signup_password")
        confirm_password = st.text_input("🔁 Confirm password", type="password", key="signup_confirm")
        age = st.text_input("🎂 Age", key="signup_age")
        gender = st.selectbox("⚧ Gender", ["Male", "Female", "Other"], key="signup_gender")

        if st.button("Generate OTP"):
            _, user = get_user_data(new_email)
            if user:
                st.error("❌ User already exists")
            elif not name or not new_email or not new_password or not confirm_password or not age:
                st.warning("⚠️ Please fill all fields.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                otp = generate_and_send_otp(new_email)
                add_new_user(new_email, new_password, name, age, gender, otp)
                st.session_state.otp_email = new_email
                st.success("✅ OTP sent to your email.")

        if "otp_email" in st.session_state:
            entered_otp = st.text_input("🔑 Enter OTP sent to your email")
            if st.button("Verify OTP"):
                if verify_otp(st.session_state.otp_email, entered_otp):
                    st.success("✅ Email verified. You can now log in.")
                    del st.session_state.otp_email
                else:
                    st.error("❌ Invalid OTP")

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
