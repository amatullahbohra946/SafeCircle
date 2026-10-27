from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("community/", views.community_page, name="community"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("mood/", views.mood_page, name="mood"),
    
    path("journal/", views.journal_page, name="journal"),

]