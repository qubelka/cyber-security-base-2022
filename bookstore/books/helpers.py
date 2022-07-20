from functools import wraps
from django.contrib import messages
from django.http import Http404
# A02:2021 – Cryptographic Failures fix: use Django built-in User model
# from django.contrib.auth.models import User
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


def user_is_authenticated(request):
    return request.session.get("username")

'''
A01:2021 – Broken Access Control fix:
Decorator checks whether the user is staff member.

def staff_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        username = user_is_authenticated(request)
        if username and get_user(username).is_staff:
            return function(request, *args, **kwargs)
        else:
            raise Http404("Page statistics does not exist.")

    return wrap
'''