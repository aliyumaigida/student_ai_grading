import os
from dotenv import load_dotenv
from groq import Groq
import re

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise Exception("❌ GROQ_API_KEY not found in .env file")

# -------------------------
# Initialize Client
# -------------------------
groq_client = Groq(api_key=GROQ_API_KEY)

# -------------------------
# Model
# -------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"

# -------------------------
# Helpers
# -------------------------
def parse_score(text: str) -> int:
    """Extract numeric score from AI output"""
    match = re.search(r"Score:\s*(\d+)\s*/", text)
    return int(match.group(1)) if match else 0

def clean_feedback(text: str) -> str:
    """Clean feedback text"""
    # Remove redundant Score lines if present
    text = re.sub(r"Score:.*\n?", "", text)
    return text.strip()

# -------------------------
# Split student answers helper
# -------------------------
def split_student_answers(text, exam_questions):
    """
    Splits student text based on sub-question patterns like 1a, 1b, 2a, 2b.
    Returns a list of answers in the same order as exam_questions.
    """
    pattern = r"(\d+[a-zA-Z]?\.)"
    parts = re.split(pattern, text)
    parts = [p.strip() for p in parts if p.strip()]

    answers = []
    i = 0
    while i < len(parts):
        if re.match(pattern, parts[i]):
            answer_text = parts[i+1] if i+1 < len(parts) else ""
            answers.append(answer_text.strip())
            i += 2
        else:
            i += 1

    # Ensure number of answers matches number of exam questions
    if len(answers) < len(exam_questions):
        answers += [""] * (len(exam_questions) - len(answers))
    elif len(answers) > len(exam_questions):
        answers = answers[:len(exam_questions)]

    return answers

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise Exception("❌ GROQ_API_KEY not found in .env file")

# -------------------------
# Initialize Client
# -------------------------
groq_client = Groq(api_key=GROQ_API_KEY)

# ... rest of grader.py ...


def build_prompt(question_text: str, student_answer: str, max_marks: int, marking_scheme: str = None) -> str:
    scheme_text = f"Marking Scheme:\n{marking_scheme}\n" if marking_scheme else ""

    return f"""
You are an expert academic grading system.

Question:
{question_text}

Student Answer:
{student_answer}

{scheme_text}
Maximum Score: {max_marks}

Instructions:

1. If a marking scheme is provided:
   - Follow it carefully
   - If marks are included, use them strictly
   - If marks are not included, intelligently distribute the total score

2. If no marking scheme is provided:
   - Evaluate using:
     - Accuracy of content
     - Clarity of explanation
     - Grammar and language quality
     - Logical structure

3. General Rules:
   - Be fair and consistent
   - Do NOT exceed {max_marks}
   - Reward correctness, clarity, and depth
   - Penalize missing key points

Return format STRICTLY:

Score: X/{max_marks}

Feedback:
<clear, teacher-like feedback>
"""

# -------------------------
# AI Grading Function
# -------------------------
def grade_with_groq(prompt: str) -> str:
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Groq API Error: {e}")

# -------------------------
# Grade Exam (supports sub-questions)
# -------------------------
def grade_exam(exam: list, student_submission: list) -> dict:
    """
    exam: list of dicts with keys: question, max_marks, marking_scheme
    student_submission: list of strings (answers)
    """
    results = []
    total_score = 0
    total_max = 0

    # Pad missing student answers with empty string
    if len(student_submission) < len(exam):
        student_submission += [""] * (len(exam) - len(student_submission))

    for idx, (q, ans) in enumerate(zip(exam, student_submission), start=1):
        question_text = q.get("question")
        max_marks = q.get("max_marks", 1)
        marking_scheme = q.get("marking_scheme")

        prompt = build_prompt(question_text, ans, max_marks, marking_scheme)
        print(f"\n🔍 Grading Question {idx}: {question_text}")

        try:
            ai_response = grade_with_groq(prompt)
        except Exception as e:
            ai_response = f"❌ Error grading: {e}"

        score = parse_score(ai_response)
        total_score += score
        total_max += max_marks

        results.append({
            "question_number": idx,
            "question": question_text,
            "student_answer": ans,
            "score": score,
            "max_marks": max_marks,
            "feedback": clean_feedback(ai_response)
        })

    return {
        "total_score": total_score,
        "total_max": total_max,
        "results": results
    }

# -------------------------
# Example / Test
# -------------------------
if __name__ == "__main__":
    exam = [
        {"question": "1a. Define Database and DBMS",
         "max_marks": 7,
         "marking_scheme": "A Database is a structured collection of data that can be easily accessed, managed, and updated (1 marks).\n"
                           "A Database Management System (DBMS) is software that allows users to define, create, maintain, and control access to the database (6 marks)"},
        {"question": "1b. Explain DBMS Operations",
         "max_marks": 4,
         "marking_scheme": "Insert: Add new records (1)\nUpdate: Modify existing records (1)\nDelete: Remove records (1)\nSort: Arrange records (1)"}
    ]

    student_submission = [
        "A Database is a structured collection of data that can be easily accessed and stored. "
        "A Database Management System (DBMS) is software that allows users to define, create, maintain, and control how information will be managed.",
        "Insert: Add new records\nUpdate: Modify existing data\nDelete: Remove records\nSort: Arrange records"
    ]

    graded = grade_exam(exam, student_submission)

    print("\n🎯 FINAL RESULT")
    print(f"Total Score: {graded['total_score']}/{graded['total_max']}")
    for r in graded["results"]:
        print("\n==============================")
        print(f"Question {r['question_number']}: {r['question']}")
        print(f"Score: {r['score']}/{r['max_marks']}")
        print("Feedback:")
        print(r["feedback"])
