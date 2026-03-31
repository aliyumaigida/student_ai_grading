# grading/api/urls.py
from django.urls import path
from .views import GradeView

urlpatterns = [
    path("grade/", GradeView.as_view()),
]
