# grading/services/loader.py
import os, csv, json, re
import pandas as pd
from docx import Document

def load_marking_scheme(file):
    """
    Load marking scheme from csv, json, excel, or docx.
    Accepts:
        - file path (str)
        - UploadedFile / file-like object
    """
    # Determine extension
    if hasattr(file, "read"):  # UploadedFile or file-like
        name = getattr(file, "name", "")
        ext = os.path.splitext(name)[1].lower()
    elif isinstance(file, str) and os.path.exists(file):
        ext = os.path.splitext(file)[1].lower()
    else:
        raise ValueError("Invalid file: must be path or file-like object")

    if ext == ".csv":
        import csv
        if hasattr(file, "read"):
            file.seek(0)
            return list(csv.DictReader(file.read().decode("utf-8").splitlines()))
        else:
            with open(file, encoding="utf-8") as f:
                return list(csv.DictReader(f))

    elif ext == ".json":
        import json
        if hasattr(file, "read"):
            file.seek(0)
            return json.load(file)
        else:
            with open(file, encoding="utf-8") as f:
                return json.load(f)

    elif ext in [".xls", ".xlsx"]:
        import pandas as pd
        if hasattr(file, "read"):
            return pd.read_excel(file).to_dict("records")
        else:
            return pd.read_excel(file).to_dict("records")

    elif ext == ".docx":
        return load_marking_scheme_docx(file)

    else:
        raise Exception("Unsupported format")



def load_marking_scheme_docx(file):
    """
    file can be a path string or a file-like object (UploadedFile from Django)
    """
    # Determine if it's a path or a file-like object
    if hasattr(file, "read"):
        doc = Document(file)  # UploadedFile or BytesIO
    elif os.path.exists(file):
        doc = Document(file)
    else:
        raise ValueError("Invalid file: must be path or file-like object")

    exam = []
    current = None
    lines = []

    q_pattern = re.compile(r"^Question\s+\d+", re.I)
    marks_pattern = re.compile(r"\((\d+)")

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        if q_pattern.match(text):
            if current:
                marks = sum(map(int, marks_pattern.findall("\n".join(lines))))
                exam.append({
                    "question": current,
                    "max_marks": marks or 100,
                    "marking_scheme": "\n".join(lines)
                })
            current = text
            lines = []
        else:
            lines.append(text)

    # Add the last question
    if current:
        marks = sum(map(int, marks_pattern.findall("\n".join(lines))))
        exam.append({
            "question": current,
            "max_marks": marks or 100,
            "marking_scheme": "\n".join(lines)
        })

    return exam

def extract_text(file):
    """
    Extract text from a file.
    Accepts:
        - file path (str)
        - UploadedFile or file-like object
    Supports: pdf, docx, txt
    """
    import os
    import re
    from docx import Document
    import pdfplumber

    ext = None
    if hasattr(file, "read"):
        # UploadedFile or BytesIO
        name = getattr(file, "name", "")
        ext = name.split(".")[-1].lower()
    elif isinstance(file, str) and os.path.exists(file):
        ext = file.split(".")[-1].lower()
    else:
        raise ValueError("Invalid file")

    if ext == "pdf":
        text = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text.append(content)
        return "\n".join(text)

    elif ext == "docx":
        doc = Document(file)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

    elif ext == "txt":
        if hasattr(file, "read"):
            return file.read().decode("utf-8", errors="ignore")
        else:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    else:
        raise Exception("Unsupported file format")
