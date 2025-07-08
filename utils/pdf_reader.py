import fitz
import re
from dateutil.parser import parse
from PIL import Image
import pytesseract

def extract_text_and_date(file):
    if file.type == "application/pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
    elif "image" in file.type:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    else:
        raise ValueError("Unsupported file type")

    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text)
    report_date = parse(date_match.group(1), dayfirst=True) if date_match else None

    return text, report_date
