from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from .models import User, Book
from .helpers import check_registration, authenticate, get_user


def index(request):
    user = None
    if request.session.get("username"):
        user = get_user(request.session.get("username"))
    books = Book.objects.all()
    return render(request, "books/index.html", {"user": user, "books": books})


def book(request, slug):
    return render(
        request, "books/book.html", {"book": get_object_or_404(Book, slug=slug)}
    )


def register(request):
    if request.session.get("username"):
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
    username = request.session.get("username")
    if username:
        del request.session["username"]
    return redirect("index")


def statistics(request):
    stats = Book.objects.all()
    return render(request, "books/statistics.html", {"stats": stats})
