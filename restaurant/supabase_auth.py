import json
import urllib.request
import urllib.error
from django.conf import settings


def _get_headers():
    return {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }


def supabase_sign_up(email, password, name, phone_number, redirect_to=None):
    """
    Register a user using Supabase Auth.
    Supabase sends an email confirmation link if 'Confirm email' is enabled.
    """
    url = f"{settings.SUPABASE_URL}/auth/v1/signup"
    payload = {
        "email": email.strip().lower(),
        "password": password,
        "data": {
            "name": name.strip(),
            "phone_number": phone_number.strip(),
        },
    }
    if redirect_to:
        payload["options"] = {"emailRedirectTo": redirect_to}

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=_get_headers(), method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_data = json.loads(error_body)
            msg = err_data.get("msg") or err_data.get("message") or err_data.get("error_description") or "Sign up failed."
        except Exception:
            msg = f"HTTP Error {e.code}: {e.reason}"
        return False, None, msg
    except Exception as e:
        return False, None, str(e)


def supabase_sign_in(email, password):
    """
    Authenticate user using Supabase Auth API with email and password.
    Returns:
      (True, data, None) on successful login
      (False, 'email_not_confirmed', msg) if email confirmation is required
      (False, 'invalid_credentials', msg) if wrong credentials
      (False, 'error', msg) for other errors
    """
    url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
    payload = {
        "email": email.strip().lower(),
        "password": password,
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=_get_headers(), method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_data = json.loads(error_body)
            desc = (err_data.get("error_description") or err_data.get("msg") or err_data.get("message") or "").lower()
            code = err_data.get("error_code") or err_data.get("error") or ""

            if "email not confirmed" in desc or code == "email_not_confirmed":
                return False, "email_not_confirmed", "Email not confirmed. Please check your inbox for the confirmation link sent by Supabase."
            if "invalid login credentials" in desc or "invalid" in desc:
                return False, "invalid_credentials", "Invalid email or password. Please try again."

            return False, "error", err_data.get("error_description") or err_data.get("msg") or "Authentication failed."
        except Exception:
            return False, "error", f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, "error", str(e)


def supabase_resend_confirmation(email, redirect_to=None):
    """
    Trigger a new confirmation email from Supabase Auth.
    """
    url = f"{settings.SUPABASE_URL}/auth/v1/resend"
    payload = {
        "type": "signup",
        "email": email.strip().lower(),
    }
    if redirect_to:
        payload["options"] = {"emailRedirectTo": redirect_to}

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=_get_headers(), method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_data = json.loads(error_body)
            msg = err_data.get("msg") or err_data.get("message") or err_data.get("error_description") or "Resend failed."
        except Exception:
            msg = f"HTTP Error {e.code}"
        return False, msg
    except Exception as e:
        return False, str(e)
