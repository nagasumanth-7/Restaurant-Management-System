from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile, Reservation


class AuthenticationAndReservationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("restaurant:signup")
        self.login_url = reverse("restaurant:login")
        self.logout_url = reverse("restaurant:logout")
        self.reserve_url = reverse("restaurant:reservation")
        self.bookings_url = reverse("restaurant:booking_history")

    def test_signup_creates_inactive_user_and_sends_verification(self):
        data = {
            "name": "Sarah Connor",
            "email": "sarah@example.com",
            "phone_number": "+91 9876543210",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("restaurant:verification_sent"))

        # Verify user exists and is inactive
        user = User.objects.get(email="sarah@example.com")
        self.assertFalse(user.is_active)
        self.assertEqual(user.first_name, "Sarah Connor")
        self.assertEqual(user.profile.phone_number, "+91 9876543210")
        self.assertFalse(user.profile.is_email_verified)

    def test_email_verification_activates_user(self):
        # Create unverified user
        user = User.objects.create_user(
            username="john@example.com",
            email="john@example.com",
            password="SecretPassword1",
            first_name="John Doe",
            is_active=False,
        )
        UserProfile.objects.create(user=user, phone_number="1234567890", is_email_verified=False)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = reverse("restaurant:verify_email", kwargs={"uidb64": uidb64, "token": token})

        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email verified successfully!")

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.is_email_verified)

    def test_login_with_unverified_email_fails(self):
        User.objects.create_user(
            username="unverified@example.com",
            email="unverified@example.com",
            password="SecretPassword1",
            is_active=False,
        )
        response = self.client.post(self.login_url, {
            "email": "unverified@example.com",
            "password": "SecretPassword1",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email Verification Required")

    def test_login_with_verified_email_succeeds(self):
        user = User.objects.create_user(
            username="verified@example.com",
            email="verified@example.com",
            password="SecretPassword1",
            first_name="Alice",
            is_active=True,
        )
        UserProfile.objects.create(user=user, phone_number="9999999999", is_email_verified=True)

        response = self.client.post(self.login_url, {
            "email": "VERIFIED@example.com",  # Test case-insensitivity
            "password": "SecretPassword1",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.reserve_url)

    def test_prebook_table_requires_login(self):
        booking_data = {
            "name": "Guest User",
            "email": "guest@example.com",
            "phone_number": "1234567890",
            "date": (timezone.localdate() + timedelta(days=2)).isoformat(),
            "time": "07:30 PM",
            "guests": 4,
            "seating_preference": "Indoor",
            "special_requests": "Window seat please",
        }
        response = self.client.post(self.reserve_url, booking_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_prebook_table_and_view_history(self):
        user = User.objects.create_user(
            username="diner@example.com",
            email="diner@example.com",
            password="Password123",
            first_name="David",
            is_active=True,
        )
        UserProfile.objects.create(user=user, phone_number="9876543210", is_email_verified=True)
        self.client.force_login(user)

        tomorrow = timezone.localdate() + timedelta(days=1)
        booking_data = {
            "name": "David Miller",
            "email": "diner@example.com",
            "phone_number": "9876543210",
            "date": tomorrow.isoformat(),
            "time": "07:30 PM",
            "guests": 3,
            "seating_preference": "Outdoor",
            "special_requests": "Anniversary dinner",
        }
        response = self.client.post(self.reserve_url, booking_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.bookings_url)

        # Check booking is created in database
        booking = Reservation.objects.filter(user=user).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.guests, 3)
        self.assertEqual(booking.seating_preference, "Outdoor")
        self.assertEqual(booking.status, "CONFIRMED")

        # View booking history page
        history_response = self.client.get(self.bookings_url)
        self.assertEqual(history_response.status_code, 200)
        self.assertContains(history_response, "David Miller")
        self.assertContains(history_response, "07:30 PM")
        self.assertContains(history_response, "Outdoor")
        self.assertContains(history_response, "Anniversary dinner")

    def test_cancel_upcoming_reservation(self):
        user = User.objects.create_user(
            username="canceler@example.com",
            email="canceler@example.com",
            password="Password123",
            is_active=True,
        )
        UserProfile.objects.create(user=user, phone_number="1234567890", is_email_verified=True)
        self.client.force_login(user)

        future_date = timezone.localdate() + timedelta(days=3)
        booking = Reservation.objects.create(
            user=user,
            name="Canceler",
            email="canceler@example.com",
            phone_number="1234567890",
            date=future_date,
            time="08:00 PM",
            guests=2,
            status="CONFIRMED",
        )

        cancel_url = reverse("restaurant:cancel_booking", kwargs={"booking_id": booking.id})
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.status, "CANCELLED")

