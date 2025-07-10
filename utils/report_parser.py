import re

def extract_parameters(text):
    """
    Extracts key health parameters from the medical report text.
    Returns a dictionary with values like blood sugar, BP, cholesterol, etc.
    """
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
    """
    Extracts tumor size mentions in the format 'X x Y cm/mm'.
    Returns a list of size strings like '2.3 x 1.5 cm'.
    """
    matches = re.findall(r"(\d+(?:\.\d+)?) ?[xX×*] ?(\d+(?:\.\d+)?) ?(cm|mm)", text)
    return [f"{m[0]} x {m[1]} {m[2]}" for m in matches]
