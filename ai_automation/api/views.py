from rest_framework import status

import tempfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UploadSerializer
from services.grading_service import process_grading
from django.shortcuts import render, redirect
from .models import StudentScore
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

@login_required
def home(request):
    return render(request, "index.html")

# def home(request):
#     return render(request, "index.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "User already exists"})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("/")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")


import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentScore
from services.grading_service import process_grading  # <-- use your grading_service module

class GradeView(APIView):
    def post(self, request):
        marking_file = request.FILES.get("marking_file")
        student_file = request.FILES.get("student_file")
        student_name = request.data.get("student_name", "Unknown Student")

        if not marking_file or not student_file:
            return Response(
                {"error": "Both marking file and student file are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Save files temporarily
            m_ext = os.path.splitext(marking_file.name)[1]
            s_ext = os.path.splitext(student_file.name)[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=m_ext) as mf:
                for chunk in marking_file.chunks():
                    mf.write(chunk)
                marking_path = mf.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=s_ext) as sf:
                for chunk in student_file.chunks():
                    sf.write(chunk)
                student_path = sf.name

            # Process grading
            raw_result = process_grading(marking_path, student_path)

            # Ensure each question is a dict and keys exist
            results = []
            for q in raw_result["results"]:
                results.append({
                    "question_number": q.get("question_number"),
                    "question": q.get("question"),
                    "student_answer": q.get("student_answer"),
                    "score": q.get("score"),
                    "max_marks": q.get("max_marks"),
                    "feedback": q.get("feedback")
                })

            # Save total score
            StudentScore.objects.create(
                student_name=student_name,
                total_score=raw_result["total_score"],
                total_max=raw_result["total_max"]
            )

            return Response({
                "total_score": raw_result["total_score"],
                "total_max": raw_result["total_max"],
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Cleanup temp files
            try:
                if os.path.exists(marking_path):
                    os.remove(marking_path)
                if os.path.exists(student_path):
                    os.remove(student_path)
            except Exception as cleanup_error:
                print("⚠️ File cleanup error:", cleanup_error)
