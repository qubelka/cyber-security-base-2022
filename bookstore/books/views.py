from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.middleware import csrf
from django.views.decorators.http import require_POST

# 4. A07:2021 – Identification and Authentication Failures fix: use Django built-in UserCreationForm and User model
# from django.contrib.auth.forms import UserCreationForm

# A02:2021 – Cryptographic Failures fix: use Django built-in User model
# from django.contrib.auth.models import User
from .models import User
from .models import Book, Comment

# A01:2021 – Broken Access Control fix:
# Decorator checks whether the user is staff member.
# from .helpers import staff_only
from .helpers import (
    check_registration,
    authenticate,
    get_book,
    get_user,
    user_is_authenticated,
    login_required,
)


def index(request):
    user = get_user(request.session.get("username"))
    books = Book.objects.all()
    return render(request, "books/index.html", {"user": user, "books": books})

"""
A03:2021 – Injection fix: use Django templates

@login_required
def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    comments = book.comments.all()
    return render(request, "books/book.html", {"book" : book, "comments": comments})
"""

@login_required
def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    comments = book.comments.all()
    comments_as_string = ""
    for comment in comments:
        comments_as_string += str(comment) + "<br/>"

    book_page_without_template = f"""
    <button><a href="/">Home</a></button><br/>
    {book.title}<br/>
    {book.author}<br/>
    {book.published}<br/>
    <br/>
    Leave a comment:<br/>
    <form action="/comment" method="POST">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf.get_token(request)}">
        <input type="text" name="comment"><br/>
        <input type="hidden" name="book_slug" value="{book.slug}">
        <input type="submit" value="add comment">
    </form>

    {comments_as_string}
    """
    return HttpResponse(book_page_without_template)


"""
# 4. A07:2021 – Identification and Authentication Failures fix: 
# use Django built-in UserCreationForm and User model

def register(request):
    if user_is_authenticated(request):
        return redirect("index")
    if request.method == "POST":
        registration_form = UserCreationForm(request.POST)
        if registration_form.is_valid():
            cleaned_data = registration_form.cleaned_data
            if not get_user(cleaned_data["username"]):
                user = registration_form.save(commit=False)
                user.set_password(registration_form.cleaned_data["password1"])
                user.save()
                authenticate(request, cleaned_data["username"], cleaned_data["password1"])
                return redirect("index")
            else:
                messages.error(request, "Username already registered.")
    else:
        registration_form = UserCreationForm()
    return render(request, "books/register_with_forms.html", {"registration_form": registration_form})
"""


def register(request):
    if user_is_authenticated(request):
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if check_registration(request, username, password1, password2):
            try:
                # A02:2021 – Cryptographic Failures fix: use Django built-in User model:
                # user = User.objects.create_user(username=username, password=password1)
                user = User.objects.create_user(username, password1)
                if user:
                    authenticate(request, username, password1)
                    return redirect("index")
            except ValidationError as e:
                messages.error(request, e.messages[0])
    return render(request, "books/register.html")


@require_POST
def login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    if not authenticate(request, username, password):
        messages.error(request, "Wrong username or password.")
    return redirect("index")


@login_required
def logout(request):
    del request.session["username"]
    messages.success(request, "Successfully logged out.")
    return redirect("index")


# A01:2021 – Broken Access Control fix:
# Decorator checks whether the user is staff member.
# Decorator code in helpers.py

# @staff_only
def statistics(request):
    stats = Book.objects.all()
    return render(request, "books/statistics.html", {"stats": stats})


@require_POST
@login_required
def comment(request):
    comment = request.POST.get("comment")
    slug = request.POST.get("book_slug")
    book = get_book(slug)
    if book:
        try:
            result = Comment(comment=comment, book=book)
            result.save()
        except ValidationError as e:
            messages.error(request, e.messages[0])
    else:
        return redirect("index")
    return redirect(reverse("book", args=[slug]))
