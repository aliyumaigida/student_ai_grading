# grading/api/serializers.py
from rest_framework import serializers

class UploadSerializer(serializers.Serializer):
    marking_file = serializers.FileField()
    student_file = serializers.FileField()
