from django.contrib import admin
from .models import UserProfile, Reservation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "is_email_verified", "created_at")
    search_fields = ("user__email", "user__first_name", "phone_number")
    list_filter = ("is_email_verified", "created_at")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone_number", "date", "time", "guests", "seating_preference", "status", "created_at")
    list_filter = ("status", "date", "seating_preference")
    search_fields = ("name", "email", "phone_number", "id")
    date_hierarchy = "date"

