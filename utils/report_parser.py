import re
from .pdf_reader import extract_text_and_date

def extract_parameters(text):
    patterns = {
        "Blood Sugar": r"blood sugar.*?(\d+)",
        "BP Systolic": r"(?:BP|blood pressure).*?(\d{2,3})\/(\d{2,3})",
        "Cholesterol": r"cholesterol.*?(\d+)",
        "Pulse": r"pulse.*?(\d+)"
    }

    result = {}
    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if param == "BP Systolic":
                result["BP Systolic"] = int(match.group(1))
                result["BP Diastolic"] = int(match.group(2))
            else:
                result[param] = int(match.group(1))
    return result

def extract_tumor_sizes(text):
    matches = re.findall(r"(\d+(?:\.\d+)?) ?[xX×*] ?(\d+(?:\.\d+)?) ?(cm|mm)", text)
    return [f"{m[0]} x {m[1]} {m[2]}" for m in matches]

def parse_medical_report(file):
    text, date = extract_text_and_date(file)
    parameters = extract_parameters(text)
    tumor_sizes = extract_tumor_sizes(text)
    
    return {
        "text": text,
        "date": date,
        "filename": file.name,
        "parameters": parameters,
        "tumor_sizes": tumor_sizes
    }
