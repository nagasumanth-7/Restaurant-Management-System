from django.urls import path
from . import views

app_name = "restaurant"

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path("reserve/", views.reservation, name="reservation"),
    path("bookings/", views.booking_history, name="booking_history"),
    path("bookings/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("verification-sent/", views.verification_sent, name="verification_sent"),
    path("verify-email/<str:uidb64>/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
]
