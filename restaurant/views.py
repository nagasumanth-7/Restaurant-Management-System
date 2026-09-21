from django.shortcuts import render


def home(request):
    return render(request, "restaurant/home.html")


def menu(request):
    return render(request, "restaurant/menu.html")


def reservation(request):
    return render(request, "restaurant/reservation.html")


def login_page(request):
    return render(request, "restaurant/login.html")


def signup_page(request):
    return render(request, "restaurant/signup.html")
