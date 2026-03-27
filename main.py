import os
import csv
import json
import re
import pandas as pd
from extractor import extract_text
from grader import grade_exam
from docx import Document

# -------------------------
# Helper to load DOCX marking scheme
# -------------------------
def load_marking_scheme_docx(file_path: str) -> list:
    """
    Robust DOCX loader for marking schemes.
    Returns list of dicts: [{question, max_marks, marking_scheme}, ...]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Marking scheme file not found: {file_path}")

    doc = Document(file_path)
    exam = []

    current_question = None
    current_scheme_lines = []

    # Match "Question 1a", "Question 2b.", "Question 3" — dot optional
    question_pattern = re.compile(r"^Question\s+\d+[a-z]?\b\.?", re.IGNORECASE)
    # Match marks in format "(1 mark)" or "(2 marks)"
    marks_pattern = re.compile(r"\((\d+)\s*marks?\)", re.IGNORECASE)

    for para in doc.paragraphs:
        text = para.text.strip().replace("\xa0", " ")
        if not text:
            continue

        # Detect question start
        if question_pattern.match(text):
            # Save previous question
            if current_question:
                total_marks = sum(
                    int(m) for line in current_scheme_lines for m in marks_pattern.findall(line)
                )
                exam.append({
                    "question": current_question,
                    "max_marks": total_marks if total_marks > 0 else 100,
                    "marking_scheme": "\n".join(current_scheme_lines).strip()
                })

            # Start new question
            current_question = text
            current_scheme_lines = []

        else:
            current_scheme_lines.append(text)

    # Add last question
    if current_question:
        total_marks = sum(
            int(m) for line in current_scheme_lines for m in marks_pattern.findall(line)
        )
        exam.append({
            "question": current_question,
            "max_marks": total_marks if total_marks > 0 else 100,
            "marking_scheme": "\n".join(current_scheme_lines).strip()
        })

    return exam


# -------------------------
# Main loader
# -------------------------
def load_marking_scheme(file_path):
    """
    Supports CSV, JSON, Excel (XLS/XLSX), or DOCX marking schemes.
    Returns list of dicts: [{question, max_marks, marking_scheme}, ...]
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        exam = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                exam.append({
                    "question": row.get("question"),
                    "max_marks": int(row.get("max_marks", 100)),
                    "marking_scheme": row.get("marking_scheme")
                })
        return exam

    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            exam = json.load(f)
        for q in exam:
            q["max_marks"] = int(q.get("max_marks", 100))
        return exam

    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        exam = df.to_dict(orient="records")
        for q in exam:
            q["max_marks"] = int(q.get("max_marks", 100))
        return exam

    elif ext == ".docx":
        return load_marking_scheme_docx(file_path)

    else:
        raise Exception("Unsupported marking scheme format. Use CSV, JSON, Excel (XLS/XLSX), or DOCX.")


# -------------------------
# Helper to split student answers
# -------------------------

def split_student_answers(text: str, num_questions: int) -> list:
    """
    Splits student submission text into answers per question.
    Handles patterns like 1a., 1b, 2a., 2b, etc.
    Preserves multi-line answers including bullets.
    """
    # Regex: matches sub-questions like "1a", "1b.", "2a", "2b."
    pattern = r"(\d+[a-zA-Z]?\.)"  # dot mandatory for splitting
    # To also allow no-dot version like "1b", add optional dot: r"(\d+[a-zA-Z]?\.?)"
    pattern = r"(\d+[a-zA-Z]?\.?)"

    # Split text by the pattern, keep delimiters
    parts = re.split(pattern, text)
    parts = [p.strip() for p in parts if p.strip()]

    answers = []
    i = 0
    while i < len(parts):
        if re.match(pattern, parts[i]):
            # Current part is question label
            answer_text = parts[i + 1] if i + 1 < len(parts) else ""
            answers.append(answer_text.strip())
            i += 2
        else:
            # Extra text without label, append to last answer
            if answers:
                answers[-1] += "\n" + parts[i]
            i += 1

    # Ensure answers match the number of questions
    if len(answers) < num_questions:
        answers += [""] * (num_questions - len(answers))
    elif len(answers) > num_questions:
        answers = answers[:num_questions]

    return answers

# -------------------------
# Main grading function
# -------------------------
def run_grading():
    # 1️⃣ Load teacher marking scheme
    marking_file = input("Enter path to marking scheme file (CSV/JSON/Excel/DOCX): ").strip().strip('"')
    if not os.path.exists(marking_file):
        print("❌ Error: Marking scheme file not found.")
        return
    exam = load_marking_scheme(marking_file)
    print(f"✅ Loaded {len(exam)} questions from marking scheme.\n")

    # 2️⃣ Load student submission
    file_path = input("Enter path to student file: ").strip().strip('"')
    if not os.path.exists(file_path):
        print("❌ Error: Student file not found.")
        return

    print("\n📄 Extracting text from student file...")
    text = extract_text(file_path)
    if not text or text == "Unsupported file format":
        print("❌ Error: Could not extract text or unsupported format.")
        return

    print("\n📝 Preview of extracted text (first 200 chars):")
    print(text[:200] + "...\n")

    # 3️⃣ Split student answers per question
    student_answers = split_student_answers(text, len(exam))

    # 4️⃣ Grade exam
    print("🤖 Sending to AI for grading...")
    graded = grade_exam(exam, student_answers)

    # 5️⃣ Display results
    print(f"\n===== TOTAL SCORE: {graded['total_score']}/{graded['total_max']} =====\n")
    for idx, r in enumerate(graded["results"], start=1):
        print(f"--- Question {idx} ---")
        print(f"Question: {r['question']}")
        print(f"Student Answer: {r['student_answer']}")
        print(f"Score: {r['score']}/{r['max_marks']}")
        print(f"Feedback:\n{r['feedback']}\n")

    # Optional: export to CSV
    save_csv = input("Do you want to save results to CSV? (y/n): ").strip().lower()
    if save_csv == "y":
        out_file = input("Enter output CSV file path: ").strip()
        with open(out_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["question_number", "question", "student_answer", "score", "max_marks", "feedback"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write per-question results
            for r in graded["results"]: 
                writer.writerow(r)

            # Write total score row
            writer.writerow({
                "question_number": "TOTAL",
                "question": "",
                "student_answer": "",
                "score": graded["total_score"],
                "max_marks": graded["total_max"],
                "feedback": ""
            })


        print(f"✅ Results saved to {out_file}")


if __name__ == "__main__":
    run_grading()
