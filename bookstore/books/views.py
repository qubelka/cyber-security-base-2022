from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from .models import User, Book
from .helpers import check_registration, authenticate, get_user, user_is_authenticated


def index(request):
    user = get_user(request.session.get("username"))
    books = Book.objects.all()
    return render(request, "books/index.html", {"user": user, "books": books})


def book(request, slug):
    return render(
        request, "books/book.html", {"book": get_object_or_404(Book, slug=slug)}
    )


def register(request):
    if user_is_authenticated(request):
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if check_registration(request, username, password1, password2):
            try:
                user = User.objects.create_user(username, password1)
                if user:
                    authenticate(request, username, password1)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return render(request, "books/register.html")
            return redirect("index")
    return render(request, "books/register.html")


@require_POST
def login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    if not authenticate(request, username, password):
        messages.error(request, "Wrong username or password.")
    return redirect("index")


def logout(request):
    if user_is_authenticated(request):
        del request.session["username"]
    return redirect("index")

# A01:2021 – Broken Access Control fix:
# Decorator checks whether the user is staff member.
# Decorator code in helpers.py

# @staff_only 
def statistics(request):
    stats = Book.objects.all()
    return render(request, "books/statistics.html", {"stats": stats})
