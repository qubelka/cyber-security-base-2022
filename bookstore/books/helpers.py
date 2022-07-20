from django.contrib import messages
from .models import User


def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def authenticate(request, username, password):
    user = get_user(username)
    if user and user.check_password(password):
        request.session["username"] = username
        return True
    return False


def check_registration(request, username, password1, password2):
    if password1 != password2:
        messages.error(request, "Passwords do not match.")
        return False
    if get_user(username):
        messages.error(request, "Username already registered.")
        return False
    return True
