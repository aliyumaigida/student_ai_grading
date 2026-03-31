# grading/services/prompt_builder.py

def build_prompt(question, answer, max_marks, scheme=None):

    scheme_text = f"Marking Scheme:\n{scheme}\n" if scheme else ""

    return f"""
You are a strict academic grader.

Question:
{question}

Student Answer:
{answer}

{scheme_text}

Maximum Score: {max_marks}

IMPORTANT:
Return ONLY in this format:

Score: X/{max_marks}

Feedback:
<clear explanation>

Do NOT add anything else.
"""
