from django.urls import path
from . import views

app_name = "restaurant"

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path("reserve/", views.reservation, name="reservation"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
]
