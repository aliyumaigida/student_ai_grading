# grading/services/splitter.py
import re

def split_student_answers(text, num_questions):

    pattern = r"(\d+[a-zA-Z]?\.?)"

    parts = re.split(pattern, text)
    parts = [p.strip() for p in parts if p.strip()]

    answers = []
    i = 0

    while i < len(parts):
        if re.match(pattern, parts[i]):
            answer = parts[i + 1] if i + 1 < len(parts) else ""
            answers.append(answer.strip())
            i += 2
        else:
            if answers:
                answers[-1] += "\n" + parts[i]
            i += 1

    if len(answers) < num_questions:
        answers += [""] * (num_questions - len(answers))

    return answers[:num_questions]
