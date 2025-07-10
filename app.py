import streamlit as st
from utils.auth import get_user_data, verify_password, add_new_user, update_usage, remaining_uses

st.set_page_config(page_title="🧠 Medical Report Analyzer", layout="centered")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "email" not in st.session_state:
    st.session_state.email = None

st.title("🧠 Medical Report Analyzer (PDF & Image)")
st.caption("Upload one or more medical reports to get a summary, trends, and abnormalities using GPT-4.")

# 👇 Login and Sign Up
if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab1:
        email = st.text_input("📧 Enter your email", key="login_email")
        password = st.text_input("🔐 Enter your password", type="password", key="login_password")

        if st.button("Login"):
            _, user = get_user_data(email)
            if user and verify_password(user["password"], password):
                st.session_state.authenticated = True
                st.session_state.email = email
                st.success(f"✅ Welcome, {email}. You have {remaining_uses(email)} uses remaining.")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    with tab2:
        new_email = st.text_input("📧 New email", key="signup_email")
        new_password = st.text_input("🔐 New password", type="password", key="signup_password")
        if st.button("Sign Up"):
            _, user = get_user_data(new_email)
            if user:
                st.error("❌ User already exists")
            else:
                add_new_user(new_email, new_password)
                st.success("✅ Account created. You can log in now.")

# 👇 Authenticated UI
else:
    st.success(f"✅ Logged in as {st.session_state.email} — Remaining uses: {remaining_uses(st.session_state.email)}")

    uploaded_files = st.file_uploader(
        "📁 Upload your medical reports",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if update_usage(st.session_state.email):
            st.write("🧪 Analyzing reports...")
            # 🔍 Replace this with your actual analysis logic
            # result = analyze_reports(uploaded_files)
            # st.write(result)

            st.success("✅ Analysis complete.")

            # Logout button after analysis
            st.markdown("---")
            if st.button("🔓 Logout"):
                del st.session_state["authenticated"]
                del st.session_state["email"]
                st.success("🔒 Logged out successfully.")
                st.experimental_rerun()
        else:
            st.error("❌ Usage limit reached.")

    # Also allow logout without uploading
    st.markdown("---")
    if st.button("🔓 Logout"):
        del st.session_state["authenticated"]
        del st.session_state["email"]
        st.success("🔒 Logged out successfully.")
        st.experimental_rerun()
