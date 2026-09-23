import re
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Reservation


class SignUpForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Your full name",
            "autocomplete": "name",
            "class": "form-control",
        }),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "class": "form-control",
        }),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "+91 98765 43210",
            "autocomplete": "tel",
            "class": "form-control",
        }),
    )
    password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create a secure password (min 6 chars)",
            "autocomplete": "new-password",
            "class": "form-control",
        }),
    )
    confirm_password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Re-enter your password",
            "autocomplete": "new-password",
            "class": "form-control",
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        active_user_exists = User.objects.filter(email__iexact=email, is_active=True).exists()
        if active_user_exists:
            raise forms.ValidationError("An account with this email address already exists. Please log in.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7:
            raise forms.ValidationError("Please enter a valid phone number with at least 7 digits.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "class": "form-control",
        }),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
            "class": "form-control",
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class ReservationForm(forms.ModelForm):
    TIME_CHOICES = [
        ("", "Select reservation time"),
        ("12:00 PM", "12:00 PM (Lunch)"),
        ("12:30 PM", "12:30 PM (Lunch)"),
        ("01:00 PM", "01:00 PM (Lunch)"),
        ("01:30 PM", "01:30 PM (Lunch)"),
        ("02:00 PM", "02:00 PM (Lunch)"),
        ("02:30 PM", "02:30 PM (Lunch)"),
        ("06:30 PM", "06:30 PM (Dinner)"),
        ("07:00 PM", "07:00 PM (Dinner)"),
        ("07:30 PM", "07:30 PM (Dinner)"),
        ("08:00 PM", "08:00 PM (Dinner)"),
        ("08:30 PM", "08:30 PM (Dinner)"),
        ("09:00 PM", "09:00 PM (Dinner)"),
        ("09:30 PM", "09:30 PM (Dinner)"),
    ]

    time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Reservation
        fields = [
            "name",
            "email",
            "phone_number",
            "date",
            "time",
            "guests",
            "seating_preference",
            "special_requests",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Full Name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+91 98765 43210", "class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "guests": forms.NumberInput(attrs={"min": 1, "max": 20, "class": "form-control"}),
            "seating_preference": forms.Select(attrs={"class": "form-control"}),
            "special_requests": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Celebration notes, dietary needs, or table placement preferences...",
                "class": "form-control",
            }),
        }

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date and date < timezone.localdate():
            raise forms.ValidationError("Reservation date cannot be in the past.")
        return date

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

