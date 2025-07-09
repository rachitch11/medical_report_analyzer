import streamlit as st
import os
from utils.pdf_reader import extract_text_and_date
from utils.report_parser import extract_parameters, extract_tumor_sizes
from utils.gpt_analysis import analyze_reports
from datetime import datetime
import matplotlib.pyplot as plt

# 🔐 Import auth helper
from utils.auth import get_user_data, update_usage, remaining_uses

st.set_page_config(page_title="Medical Report Analyzer", layout="wide")

st.title("🧠 Medical Report Analyzer (PDF & Image)")
st.markdown("Upload one or more medical reports to get a summary, trends, and abnormalities using GPT-4.")

# 🔐 Login Section
email = st.text_input("🔐 Enter your email to continue:")

if email:
    row_num, user_data = get_user_data(email)

    if user_data:
        rem = remaining_uses(email)
        st.success(f"✅ Welcome, {email}. You have **{rem} uses remaining**.")

        if rem <= 0:
            st.error("❌ You've reached your usage limit. Please contact support for more access.")
            st.stop()

        # 🟢 Upload section
        uploaded_files = st.file_uploader(
            "📁 Upload Reports (PDF, PNG, JPG)", 
            type=["pdf", "png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )

        report_data = []

        if uploaded_files:
            with st.spinner("🔍 Extracting data from uploaded reports..."):
                for file in uploaded_files:
                    try:
                        text, report_date = extract_text_and_date(file)
                        parameters = extract_parameters(text)
                        tumor_sizes = extract_tumor_sizes(text)

                        report_data.append({
                            "filename": file.name,
                            "text": text,
                            "date": report_date,
                            "parameters": parameters,
                            "tumor_sizes": tumor_sizes
                        })
                    except Exception as e:
                        st.warning(f"⚠️ Failed to process {file.name}: {e}")

            # ✅ Sort by date
            report_data.sort(
                key=lambda x: x["date"] if isinstance(x["date"], datetime) else datetime.min
            )

            for r in report_data:
                st.caption(f"📄 {r['filename']} → 🗓️ Date: {r['date'] if r['date'] else '❓ Not detected'}")

            # ✅ Analyze Button
            if st.button("🔎 Analyze"):
                with st.spinner("🧠 Analyzing with GPT..."):
                    try:
                        if update_usage(email):  # ✅ Count this usage
                            result = analyze_reports(report_data)

                            st.subheader("📊 Abnormal Findings & Impressions")
                            st.dataframe(result["abnormal_table"])

                            st.subheader("📝 Final Summary")
                            st.text_area("Summary", result["summary"], height=400)
                        else:
                            st.error("❌ Usage limit reached or failed to update usage.")
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")

    else:
        st.error("❌ Email not authorized. Please contact support.")
