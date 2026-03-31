
import logging
from django.conf import settings

from .loader import load_marking_scheme
from .extractor import extract_text
from .splitter import split_student_answers
from .grading_engine import grade_exam


logger = logging.getLogger(__name__)


def process_grading(marking_file, student_file):

    exam = load_marking_scheme(marking_file)

    text = extract_text(student_file)

    # 🔍 Debug only in development
    if settings.DEBUG:
        logger.info("EXTRACTED TEXT (first 500 chars):\n%s", text[:500])

    if not text or not text.strip():
        raise Exception("❌ No text extracted from student file")

    answers = split_student_answers(text, len(exam))

    # 🔍 Debug only in development
    if settings.DEBUG:
        logger.info("SPLIT ANSWERS: %s", answers)

    # 🔥 Fallback if splitting fails
    if all(not a.strip() for a in answers):
        if settings.DEBUG:
            logger.warning("⚠️ Splitting failed — using fallback")
        answers = [text] * len(exam)

    return grade_exam(exam, answers)

