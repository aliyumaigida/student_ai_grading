

from django.urls import path
from .views import signup_view, login_view, logout_view, home
from .views import (
    GradeView,
    signup_view,
    login_view,
    logout_view,
    home
)

urlpatterns = [
    # 🌐 Web pages
    path('', home, name="home"),
    path('signup/', signup_view, name="signup"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),

    # 🔌 API endpoint
    path('grade/', GradeView.as_view(), name="grade"),
]
