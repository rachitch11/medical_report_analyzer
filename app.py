import streamlit as st
from utils.auth import (
    get_user_data, verify_password,
    add_new_user, update_usage, remaining_uses
)

st.set_page_config(page_title="🧠 Medical Report Analyzer", layout="centered")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "email" not in st.session_state:
    st.session_state.email = None
if "name" not in st.session_state:
    st.session_state.name = ""

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
                st.success(f"✅ Welcome, {email}. You have {remaining_uses(email)} uses remaining.")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    with tab2:
        name = st.text_input("👤 Your name", key="signup_name")
        new_email = st.text_input("📧 New email", key="signup_email")
        new_password = st.text_input("🔐 New password", type="password", key="signup_password")
        confirm_password = st.text_input("🔁 Confirm password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            _, user = get_user_data(new_email)
            if user:
                st.error("❌ User already exists")
            elif not name or not new_email or not new_password or not confirm_password:
                st.warning("⚠️ Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                add_new_user(new_email, new_password, name)
                st.success("✅ Account created. You can log in now.")

else:
    st.success(f"✅ Logged in as {st.session_state.name} ({st.session_state.email}) — Remaining uses: {remaining_uses(st.session_state.email)}")

    uploaded_files = st.file_uploader(
        "📁 Upload your medical reports",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

if uploaded_files:
    from utils.pdf_reader import extract_text_from_pdf
    from utils.ocr_reader import extract_text_from_image
    from utils.gpt_analysis import analyze_text_with_gpt

    if st.button("🔍 Analyze Reports"):
        if update_usage(st.session_state.email):
            st.info("🧪 Analyzing reports...")

            combined_text = ""

            for file in uploaded_files:
                if file.name.endswith(".pdf"):
                    combined_text += extract_text_from_pdf(file) + "\n"
                else:
                    combined_text += extract_text_from_image(file) + "\n"

            if combined_text.strip():
                result = analyze_text_with_gpt(combined_text)
                st.subheader("📋 Analysis Result")
                st.markdown(result)
            else:
                st.warning("❗ No readable text found in uploaded files.")
        else:
            st.error("❌ Usage limit reached.")


    # 🔒 Logout Button
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
