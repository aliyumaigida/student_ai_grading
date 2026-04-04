# grading/services/parser.py
import re

def parse_score(text):
    if not text:
        return 0

    match = re.search(r"Score:\s*(\d+)", text)
    if match:
        return int(match.group(1))

    # fallback
    match = re.search(r"\b(\d+)\b", text)
    if match:
        return int(match.group(1))

    return 0


import re

def clean_feedback(response):
    if not response:
        return ""

    # 🔥 Extract ONLY text after "Feedback:"
    match = re.search(r"Feedback:\s*(.*)", response, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""
