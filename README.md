# 🧾 Medical Report Analyzer

An AI-powered Streamlit app that allows users to upload medical reports in PDF or image format, automatically extracts abnormal parameters using OCR and GPT, and generates impressions and visual trend summaries over time.

## 📌 Overview

This tool helps users:
- Extract key health metrics from lab reports
- Identify abnormal values
- Generate health summaries using OpenAI
- Track changes in parameters like glucose, BP, etc., over time via graphs

## 🚀 Features

- Upload **PDF or Image** of medical reports
- **Tesseract OCR** for text extraction
- **OpenAI GPT-4** for impressions and summary
- Interactive **line charts** for tracking trends
- User **authentication** and **usage control** via Google Sheets API
- Works for multiple users with dark mode support

## 🛠 Tech Stack

- Streamlit
- OpenAI API (GPT-4)
- Tesseract OCR
- Pandas, Matplotlib
- Google Sheets API (Auth & usage limits)
- Python 3.10+

## 📦 Installation

```bash
pip install -r requirements.txt
streamlit run app.py
