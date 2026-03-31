# grading/services/extractor.py

from docx import Document

def extract_text(file_path):

    if file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    elif file_path.endswith(".txt"):
        return open(file_path, encoding="utf-8").read()

    elif file_path.endswith(".pdf"):
        return "PDF NOT SUPPORTED YET"

    return ""
