
from django.db import models

class StudentScore(models.Model):
    student_name = models.CharField(max_length=100)
    matric_no = models.CharField(max_length=20, unique=True)  # unique matric number
    total_score = models.FloatField()
    total_max = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} ({self.matric_no}) - {self.total_score}/{self.total_max}"
