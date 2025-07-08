import streamlit as st
import os
from utils.pdf_reader import extract_text_and_date
from utils.report_parser import extract_parameters, extract_tumor_sizes
from utils.gpt_analysis import analyze_reports
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Medical Report Analyzer", layout="wide")

st.title("🧠 Medical Report Analyzer (PDF & Image)")
st.markdown("Upload one or more medical reports to get a summary, trends, and abnormalities using GPT-4.")

uploaded_files = st.file_uploader("📁 Upload Reports (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

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

    # ✅ Sort by date safely
    report_data.sort(
        key=lambda x: x["date"] if isinstance(x["date"], datetime) else datetime.min
    )

    # ✅ Log filenames and dates (optional)
    for r in report_data:
        st.caption(f"📄 {r['filename']} → 🗓️ Date: {r['date'] if r['date'] else '❓ Not detected'}")

    # ✅ Analyze Button
    if st.button("🔎 Analyze"):
        with st.spinner("🧠 Analyzing with GPT..."):
            try:
                result = analyze_reports(report_data)

                st.subheader("📊 Abnormal Findings & Impressions")
                st.dataframe(result["abnormal_table"])

                st.subheader("📝 Final Summary")
                st.text_area("Summary", result["summary"], height=400)

            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
