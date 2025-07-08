import re

def extract_parameters(text):
    patterns = {
        "Blood Sugar": r"blood sugar.*?(\d+)",
        "BP Systolic": r"(?:BP|blood pressure).*?(\d{2,3})\/(\d{2,3})",
        "Cholesterol": r"cholesterol.*?(\d+)",
        "Pulse": r"pulse.*?(\d+)",
    }

    result = {}
    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result[param] = int(match.group(1))
            if param == "BP Systolic" and match.group(2):
                result["BP Diastolic"] = int(match.group(2))
    return result

def extract_tumor_sizes(text):
    matches = re.findall(r"(\d+(\.\d+)?) ?[xX×*] ?(\d+(\.\d+)?) ?(cm|mm)", text)
    return [f"{m[0]} x {m[2]} {m[4]}" for m in matches]
