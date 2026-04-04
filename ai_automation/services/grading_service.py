# grading/services/grading_serve.py
import logging
from django.conf import settings
from .loader import load_marking_scheme
from .extractor import extract_text
from .splitter import split_student_answers
from .grading_engine import grade_exam
import re

logger = logging.getLogger(__name__)

def process_grading(marking_file, student_file):
    # Load marking scheme
    exam_raw = load_marking_scheme(marking_file)

    # Normalize exam questions: always a dict
    exam = []
    for q in exam_raw:
        if isinstance(q, str):
            exam.append({
                "question": q,
                "max_marks": 1,       # default max mark if not provided
                "marking_scheme": ""  # default empty marking scheme
            })
        else:
            exam.append(q)

    # Extract text from student file
    text = extract_text(student_file)

    if settings.DEBUG:
        logger.info("EXTRACTED TEXT (first 500 chars):\n%s", text[:500])

    if not text or not text.strip():
        raise Exception("❌ No text extracted from student file")

    # Try splitting answers intelligently
    answers = split_student_answers(text, len(exam))

    # Fallback if splitting fails
    if all(not a.strip() for a in answers):
        if settings.DEBUG:
            logger.warning("⚠️ Splitting failed — using marking scheme for fallback")

        import re
        q_pattern = re.compile(r"Question\s+\d+[a-z]*", re.I)
        splits = q_pattern.split(text)
        splits = [s.strip() for s in splits if s.strip()]
        if len(splits) == len(exam):
            answers = splits
        else:
            answers = [text.strip() for _ in exam]

    if settings.DEBUG:
        logger.info("SPLIT ANSWERS: %s", answers)

    # Grade exam
    return grade_exam(exam, answers)
