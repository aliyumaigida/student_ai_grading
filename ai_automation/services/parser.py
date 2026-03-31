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


def clean_feedback(text):
    if not text:
        return ""

    text = re.sub(r"Score:.*\n?", "", text)
    return text.strip()
