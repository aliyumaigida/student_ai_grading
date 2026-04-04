import os
from docx import Document
import pdfplumber
import pytesseract
from PIL import Image
import tempfile

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    # 📄 DOCX
    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # 📄 TXT
    elif ext == ".txt":
        with open(file_path, encoding="utf-8") as f:
            return f.read()

    # 📄 PDF (TEXT + OCR FALLBACK)
    elif ext == ".pdf":
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()

                    # ✅ Use OCR only if text is missing or very short
                    if page_text and len(page_text.strip()) > 10:
                        text += page_text + "\n"
                    else:
                        # OCR fallback for scanned pages
                        image = page.to_image(resolution=300).original
                        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                            image.save(tmp.name, format="PNG")
                            ocr_text = pytesseract.image_to_string(Image.open(tmp.name))
                        text += ocr_text + "\n"

        except Exception as e:
            print("❌ PDF extraction error:", e)
            return ""

        # ✅ Remove duplicate lines while preserving order
        lines = text.splitlines()
        seen = set()
        unique_lines = []
        for line in lines:
            clean_line = line.strip()
            if clean_line and clean_line not in seen:
                unique_lines.append(clean_line)
                seen.add(clean_line)
        return "\n".join(unique_lines)

    return ""
