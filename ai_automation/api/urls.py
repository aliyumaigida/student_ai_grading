from django.urls import path
from .views import (
    home,
    signup_view,
    login_view,
    logout_view,
    GradeView,
    StudentHistoryView,
    student_history_page
)

from django.contrib.auth import views as auth_views

urlpatterns = [
    # 🔐 Auth
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

    # 🏠 Home (grading page)
    path('', home, name='home'),

    # 📝 Grading API
    path('grade/', GradeView.as_view(), name='grade'),

    # 📜 History
    path('student-history/', StudentHistoryView.as_view(), name='student-history-api'),
    path('history-page/', student_history_page, name='history-page'),

]
