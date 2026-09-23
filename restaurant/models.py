from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} Profile"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    SEATING_CHOICES = [
        ("No preference", "No preference"),
        ("Indoor", "Indoor"),
        ("Outdoor", "Outdoor"),
        ("Window", "Window"),
        ("Private Booth", "Private Booth"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    date = models.DateField()
    time = models.CharField(max_length=20)
    guests = models.PositiveIntegerField(default=2)
    seating_preference = models.CharField(max_length=50, choices=SEATING_CHOICES, default="No preference")
    special_requests = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CONFIRMED")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"Booking #{self.id} - {self.name} on {self.date} at {self.time}"

    @property
    def is_past(self):
        return self.date < timezone.localdate()

    @property
    def can_cancel(self):
        return self.status == "CONFIRMED" and not self.is_past

