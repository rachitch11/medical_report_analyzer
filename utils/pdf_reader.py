import pytesseract
from PIL import Image
import pdfplumber
import io
import re
from datetime import datetime
from dateutil import parser

def extract_text_and_date(file):
    text = ""
    file_type = file.type

    # --- PDF Extraction ---
    if file_type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    # --- Image (JPG/PNG) OCR Extraction ---
    elif "image" in file_type:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)

    # Fallback if OCR or PDF text is empty
    if not text.strip():
        raise ValueError("❌ No readable text found in report")

    # --- Extract Date ---
    report_date = None
    try:
        # Use fuzzy parser to extract closest date-like string
        report_date = parser.parse(text, fuzzy=True)

        # Reject invalid-looking dates (like future or too old)
        if report_date.year < 1950 or report_date > datetime.today():
            report_date = None
    except Exception:
        report_date = None

    return text, report_date
