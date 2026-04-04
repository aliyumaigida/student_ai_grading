# # grading/services/grading_engine.py

# from .ai_client import send_prompt
# from .prompt_builder import build_prompt
# from .parser import parse_score, clean_feedback


# def grade_exam(exam, answers):
#     results = []
#     total_score = 0
#     total_max = 0

#     if len(answers) < len(exam):
#         answers += [""] * (len(exam) - len(answers))

#     for i, (q, ans) in enumerate(zip(exam, answers), start=1):

#         print("\n==============================")
#         print(f"QUESTION {i}")
#         print("QUESTION TEXT:", q.get("question"))
#         print("STUDENT ANSWER:", ans)
#         print("==============================\n")

#         prompt = build_prompt(
#             q["question"],
#             ans,
#             q.get("max_marks", 1),
#             q.get("marking_scheme")
#         )

#         try:
#             response = send_prompt(prompt)

#             print("AI RESPONSE:", response)

#         except Exception as e:
#             print("❌ ERROR:", e)
#             response = f"Score: 0/{q.get('max_marks',1)}\n\nFeedback:\n{e}"

#         score = parse_score(response)

#         total_score += score
#         total_max += q.get("max_marks", 1)

#         results.append({
#             "question_number": i,
#             "question": q["question"],
#             "student_answer": ans,
#             "score": score,
#             "max_marks": q.get("max_marks", 1),
#             "feedback": clean_feedback(response)
#         })

#     return {
#         "total_score": total_score,
#         "total_max": total_max,
#         "results": results
#     }

# grading/services/grading_engine.py

from .ai_client import send_prompt
from .prompt_builder import build_prompt
from .parser import parse_score, clean_feedback


def grade_exam(exam, answers):
    results = []
    total_score = 0
    total_max = 0

    if len(answers) < len(exam):
        answers += [""] * (len(exam) - len(answers))

    for i, (q, ans) in enumerate(zip(exam, answers), start=1):

        prompt = build_prompt(
            q["question"],
            ans,
            q.get("max_marks", 1),
            q.get("marking_scheme")
        )

        try:
            response = send_prompt(prompt)

        except Exception as e:
            response = f"Score: 0/{q.get('max_marks',1)}\n\nFeedback:\n{e}"

        score = parse_score(response)

        total_score += score
        total_max += q.get("max_marks", 1)

        results.append({
            "question_number": i,
            "question": q["question"],
            "student_answer": ans,
            "score": score,
            "max_marks": q.get("max_marks", 1),
            "feedback": clean_feedback(response)
        })

    return {
        "total_score": total_score,
        "total_max": total_max,
        "results": results
    }
