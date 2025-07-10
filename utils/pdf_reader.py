import pytesseract
from PIL import Image
import pdfplumber
import io
import re
from datetime import datetime
from dateutil import parser

def extract_text_and_date(file):
    text = ""
    file_type = file.type.lower()

    # --- PDF Extraction ---
    if "pdf" in file_type:
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"❌ Failed to read PDF: {str(e)}")

    # --- Image (JPG/PNG) OCR Extraction ---
    elif "image" in file_type:
        try:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            raise ValueError(f"❌ Failed to read image: {str(e)}")

    # --- Fallback if no text found ---
    if not text.strip():
        raise ValueError("❌ No readable text found in report")

    # --- Extract Date ---
    report_date = None
    try:
        report_date = parser.parse(text, fuzzy=True)

        # Reject unlikely dates
        if report_date.year < 1950 or report_date > datetime.today():
            report_date = None
    except Exception:
        # Try regex-based fallback
        date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
        if date_match:
            try:
                report_date = parser.parse(date_match.group(), dayfirst=True)
            except:
                report_date = None

    return text, report_date
