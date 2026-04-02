from django.db import models

# Create your models here.
from django.db import models

class StudentScore(models.Model):
    student_name = models.CharField(max_length=100)
    total_score = models.FloatField()
    total_max = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.total_score}/{self.total_max}"
