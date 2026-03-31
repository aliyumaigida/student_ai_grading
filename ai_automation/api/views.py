
import tempfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UploadSerializer
from services.grading_service import process_grading

# grading/views.py
from django.shortcuts import render

def home(request):
    return render(request, "index.html")



class GradeView(APIView):

    def post(self, request):
        marking_file = request.FILES.get("marking_file")
        student_file = request.FILES.get("student_file")

        if not marking_file or not student_file:
            return Response({"error": "Both files are required"}, status=400)

        # 🔥 Get original extensions
        m_ext = os.path.splitext(marking_file.name)[1]
        s_ext = os.path.splitext(student_file.name)[1]

        # 🔥 Save marking file WITH extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=m_ext) as mf:
            for chunk in marking_file.chunks():
                mf.write(chunk)
            marking_path = mf.name

        # 🔥 Save student file WITH extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=s_ext) as sf:
            for chunk in student_file.chunks():
                sf.write(chunk)
            student_path = sf.name

        # ✅ Now loader will detect format correctly
        result = process_grading(marking_path, student_path)

        return Response(result)
