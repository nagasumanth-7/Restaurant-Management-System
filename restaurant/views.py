from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from .models import UserProfile, Reservation
from .forms import SignUpForm, LoginForm, ReservationForm

User = get_user_model()


def home(request):
    return render(request, "restaurant/home.html")


def menu(request):
    return render(request, "restaurant/menu.html")


def signup_page(request):
    if request.user.is_authenticated:
        return redirect("restaurant:reservation")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"].strip()
            email = form.cleaned_data["email"].strip().lower()
            phone_number = form.cleaned_data["phone_number"].strip()
            password = form.cleaned_data["password"]

            # Remove any unverified stale user with the same email
            stale_users = User.objects.filter(email__iexact=email, is_active=False)
            stale_users.delete()

            # Create inactive user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                is_active=False,
            )

            UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                is_email_verified=False,
            )

            # Generate verification token
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_url = request.build_absolute_uri(
                reverse("restaurant:verify_email", kwargs={"uidb64": uidb64, "token": token})
            )

            # Send verification email
            subject = "Verify your email - Food Waves"
            message = (
                f"Hello {name},\n\n"
                f"Thank you for registering at Food Waves!\n\n"
                f"Please verify your email address by clicking the link below:\n"
                f"{verify_url}\n\n"
                f"If you did not create this account, please disregard this email.\n\n"
                f"Warm regards,\n"
                f"The Food Waves Team"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "Food Waves <noreply@foodwaves.com>"),
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log error if mail sending encounters an issue
                print(f"[FoodWaves Mail Error] Failed to send email to {email}: {e}")

            request.session["verification_email"] = email
            if settings.DEBUG:
                request.session["dev_verify_link"] = verify_url

            messages.info(
                request,
                f"We sent a verification link to {email}. Please check your inbox to activate your account.",
            )
            return redirect("restaurant:verification_sent")
    else:
        form = SignUpForm()

    return render(request, "restaurant/signup.html", {"form": form})


def verification_sent(request):
    email = request.session.get("verification_email", "")
    dev_verify_link = request.session.get("dev_verify_link") if settings.DEBUG else None
    return render(
        request,
        "restaurant/verification_sent.html",
        {"email": email, "dev_verify_link": dev_verify_link},
    )


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.save()

        # Clear dev link session if set
        request.session.pop("dev_verify_link", None)
        request.session.pop("verification_email", None)

        messages.success(request, "Your email has been verified! You can now log in.")
        return render(request, "restaurant/verify_email.html", {"success": True, "user": user})
    else:
        return render(request, "restaurant/verify_email.html", {"success": False})


def resend_verification(request):
    email = request.POST.get("email") or request.GET.get("email") or request.session.get("verification_email")
    if email:
        email = email.strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=False).first()
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_url = request.build_absolute_uri(
                reverse("restaurant:verify_email", kwargs={"uidb64": uidb64, "token": token})
            )
            try:
                send_mail(
                    subject="Verify your email - Food Waves",
                    message=(
                        f"Hello {user.first_name or 'Food Waves Guest'},\n\n"
                        f"Here is your requested email verification link:\n"
                        f"{verify_url}\n\n"
                        f"Warm regards,\nFood Waves Team"
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "Food Waves <noreply@foodwaves.com>"),
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"[FoodWaves Mail Error] Failed to resend email: {e}")

            request.session["verification_email"] = email
            if settings.DEBUG:
                request.session["dev_verify_link"] = verify_url

            messages.success(request, f"A new verification link has been sent to {email}.")
        else:
            messages.info(request, "If an inactive account exists with that email, a verification link has been sent.")
    else:
        messages.error(request, "Please provide an email address to resend the verification link.")

    return redirect("restaurant:verification_sent")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("restaurant:reservation")

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    unverified_email = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            password = form.cleaned_data["password"]
            remember_me = form.cleaned_data.get("remember_me", True)

            # Check if user exists and is inactive (unverified email)
            inactive_user = User.objects.filter(email__iexact=email, is_active=False).first()
            if inactive_user and inactive_user.check_password(password):
                unverified_email = email
                messages.warning(
                    request,
                    "Your email address is not verified yet. Please check your inbox or resend the verification link below.",
                )
                return render(
                    request,
                    "restaurant/login.html",
                    {
                        "form": form,
                        "next": next_url,
                        "unverified_email": unverified_email,
                    },
                )

            # Authenticate via custom EmailBackend
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                return redirect("restaurant:reservation")
            else:
                messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = LoginForm()

    return render(
        request,
        "restaurant/login.html",
        {"form": form, "next": next_url, "unverified_email": unverified_email},
    )


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("restaurant:home")


def reservation(request):
    initial_data = {}
    if request.user.is_authenticated:
        initial_data["name"] = request.user.get_full_name() or request.user.first_name
        initial_data["email"] = request.user.email
        if hasattr(request.user, "profile"):
            initial_data["phone_number"] = request.user.profile.phone_number

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to pre-book a table.")
            return redirect(f"{reverse('restaurant:login')}?next={reverse('restaurant:reservation')}")

        form = ReservationForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            messages.success(
                request,
                f"Table pre-booked successfully! Reservation reference #{booking.id} for {booking.date} at {booking.time}.",
            )
            return redirect("restaurant:booking_history")
    else:
        form = ReservationForm(initial=initial_data)

    min_date = timezone.localdate().isoformat()
    return render(
        request,
        "restaurant/reservation.html",
        {
            "form": form,
            "min_date": min_date,
            "is_authenticated": request.user.is_authenticated,
        },
    )


@login_required(login_url="restaurant:login")
def booking_history(request):
    today = timezone.localdate()
    user_reservations = Reservation.objects.filter(user=request.user)

    upcoming_bookings = user_reservations.filter(date__gte=today).order_by("date", "time")
    past_bookings = user_reservations.filter(date__lt=today).order_by("-date", "-time")

    return render(
        request,
        "restaurant/booking_history.html",
        {
            "upcoming_bookings": upcoming_bookings,
            "past_bookings": past_bookings,
            "total_count": user_reservations.count(),
        },
    )


@login_required(login_url="restaurant:login")
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Reservation, id=booking_id, user=request.user)

    if request.method == "POST":
        if booking.can_cancel:
            booking.status = "CANCELLED"
            booking.save()
            messages.success(request, f"Reservation #{booking.id} has been cancelled.")
        else:
            messages.error(request, "This reservation cannot be cancelled.")

    return redirect("restaurant:booking_history")
