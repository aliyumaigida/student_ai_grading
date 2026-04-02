
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



# class GradeView(APIView):

#     def post(self, request):
#         marking_file = request.FILES.get("marking_file")
#         student_file = request.FILES.get("student_file")

#         if not marking_file or not student_file:
#             return Response({"error": "Both files are required"}, status=400)

#         # 🔥 Get original extensions
#         m_ext = os.path.splitext(marking_file.name)[1]
#         s_ext = os.path.splitext(student_file.name)[1]

#         # 🔥 Save marking file WITH extension
#         with tempfile.NamedTemporaryFile(delete=False, suffix=m_ext) as mf:
#             for chunk in marking_file.chunks():
#                 mf.write(chunk)
#             marking_path = mf.name

#         # 🔥 Save student file WITH extension
#         with tempfile.NamedTemporaryFile(delete=False, suffix=s_ext) as sf:
#             for chunk in student_file.chunks():
#                 sf.write(chunk)
#             student_path = sf.name

#         # ✅ Now loader will detect format correctly
#         result = process_grading(marking_path, student_path)

#         return Response(result)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# import os, tempfile

class GradeView(APIView):
    def post(self, request):
        marking_file = request.FILES.get("marking_file")
        student_file = request.FILES.get("student_file")
        student_name = request.data.get("student_name", "Unknown Student")

        if not marking_file or not student_file:
            return Response({"error": "Both files are required"}, status=400)

        # Save marking file temporarily
        m_ext = os.path.splitext(marking_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=m_ext) as mf:
            for chunk in marking_file.chunks():
                mf.write(chunk)
            marking_path = mf.name

        # Save student file temporarily
        s_ext = os.path.splitext(student_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=s_ext) as sf:
            for chunk in student_file.chunks():
                sf.write(chunk)
            student_path = sf.name

        # Grade the exam
        result = process_grading(marking_path, student_path)

        # Save total score in DB
        StudentScore.objects.create(
            student_name=student_name,
            total_score=result["total_score"],
            total_max=result["total_max"]
        )

        return Response(result)