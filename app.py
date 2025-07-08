import streamlit as st
import pandas as pd
import altair as alt
from utils.pdf_reader import extract_text_and_date
from utils.report_parser import extract_parameters, extract_tumor_sizes
from utils.gpt_analysis import analyze_reports

st.set_page_config(page_title="Medical Report Analyzer", layout="centered")
st.title("🧠 Medical Report Analyzer + MRI Tracker")

uploaded_files = st.file_uploader(
    "📤 Upload one or more medical reports (PDF, JPG, PNG)",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

report_data = []

if uploaded_files:
    for file in uploaded_files:
        text, report_date = extract_text_and_date(file)
        parameters = extract_parameters(text)
        tumor_sizes = extract_tumor_sizes(text)

        report_data.append({
            "filename": file.name,
            "date": report_date,
            "text": text,
            "parameters": parameters,
            "tumor_sizes": tumor_sizes
        })

    report_data.sort(key=lambda x: x["date"])

    # 🔘 Analyze Button
    if st.button("🔍 Analyze Reports"):
        result = analyze_reports(report_data)

        st.markdown("### 📋 Final Summary")
        st.text_area("GPT-4 Summary:", result["summary"], height=400)

        st.markdown("### 🧪 Abnormal Reports Table")
        st.dataframe(result["abnormal_table"])

        st.markdown("### 📈 Parameter Trend Graphs")
        trend_data = []
        for report in report_data:
            for param, val in report["parameters"].items():
                trend_data.append({
                    "Date": report["date"],
                    "Parameter": param,
                    "Value": val
                })

        trend_df = pd.DataFrame(trend_data)
        for param in trend_df["Parameter"].unique():
            chart = alt.Chart(trend_df[trend_df["Parameter"] == param]).mark_line(point=True).encode(
                x="Date:T",
                y="Value:Q"
            ).properties(title=f"{param} Over Time")
            st.altair_chart(chart, use_container_width=True)
