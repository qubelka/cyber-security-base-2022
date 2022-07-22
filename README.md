# Cyber security base 2022 course project 

## Running the application

```sh
$ cd bookstore
$ python3 manage.py runserver 
```

App has two users:

| Role         | username | password  |
| :---         |  :----:  |    ---:   |
| Regular user | user     | password  |
| Staff member | admin    | password  |

## Project has the following vulnerabilities  from OWASP Top10:2021 list:

### 1. [A01:2021 – Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)

> *"Bypassing access control checks by modifying the URL (parameter tampering or force browsing), internal application state, or the HTML page, or by using an attack tool modifying API requests."*

**Problem**: `index.html` has a link to statistics-page which should be visible only to the staff, but the statistics view function does not check whether the user accessing the page is staff member or not. Anyone, even the users that are not registered can access the page by going to the url `localhost:8000/statistics`.

**Fix**: add decorator that checks whether the user is staff member before running the view function

Uncomment the decorator code in **helpers.py**:

**books/helpers.py**
```python
def staff_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        username = user_is_authenticated(request)
        if username and get_user(username).is_staff:
            return function(request, *args, **kwargs)
        else:
            raise Http404("Page statistics does not exist.")

    return wrap
```

Uncomment the rows that import and apply the decorator:

**books/views.py**
```python
...
from .helpers import staff_only
...
@staff_only 
def statistics(request):
    stats = Book.objects.all()
    return render(request, "books/statistics.html", {"stats": stats})
```

### 2. [A02:2021 – Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)

> *"Are deprecated hash functions such as MD5 or SHA1 in use, or are non-cryptographic hash
functions used when cryptographic hash functions are needed?"*

**Problem**: User passwords are hashed using deprecated hash function MD5

**Fix**: Use built-in Django `User` model. By default, Django uses the PBKDF2 algorithm with a SHA256 hash for password hashing. 

Import the `User` model from `django.contrib.auth.models` instead of `.models` in **views.py** and **helpers.py**:

**books/views.py**
```python
from django.contrib.auth.models import User
# from .models import User
```

**books/helpers.py**
```python
from django.contrib.auth.models import User
# from .models import User
```

In **books/views.py** change **register()** view to use Django `User` model:

```python
def register(request):
    if user_is_authenticated(request):
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if check_registration(request, username, password1, password2):
            try:
                user = User.objects.create_user(username=username, password=password1)
                # user = User.objects.create_user(username, password1)
                if user:
                    authenticate(request, username, password1)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return render(request, "books/register.html")
            return redirect("index")
    return render(request, "books/register.html")
```

### 3. [A03:2021 – Injection](https://owasp.org/Top10/A03_2021-Injection/)

> *"User-supplied data is not validated, filtered, or sanitized by the application."*

**Problem**: `book`-view renders plain HTML and contains a form for leaving comments. This page is vulnerable to Cross Site Scripting (XSS) attacks. 

For example by leaving a comment 
```html 
<script>window.location="https://craftinginterpreters.com";</script>
```
page visitors will be always redirected to the site `craftinginterpreters.com`. 

**Fix**: Use Django templates. Django templates protect against the majority of XSS attacks. 

Comment out the existing **book()**-view and uncomment the 
view with the *A03:2021 – Injection fix* text:

**views.py**
```python
"""
A03:2021 – Injection fix: use Django templates
"""
@login_required
def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    comments = book.comments.all()
    return render(request, "books/book.html", {"book" : book, "comments": comments})

'''
##################
OLD IMPLEMENTATION
##################
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
'''
```

Fixed view uses the book.html-template:

**books/templates/books/book.html**

```html
{% extends "books/base.html" %}

{% block content %}
    {{ book.title }}<br/>
    {{ book.author }}<br/>
    {{ book.published }}<br/>
    <br/>
    Leave a comment:<br/>
    <form action="{% url 'comment' book.slug %}" method="POST">
        {% csrf_token %}
        <input type="text" name="comment"><br/>
        <input type="submit" value="add comment">
    </form>
    <br/>
    {% for comment in comments %}
        {{ comment }}<br/>
    {% endfor %}
{% endblock %}
```

### 4. [A07:2021 – Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

> *"There may be authentication weaknesses if the application: Permits default, weak, or well-known passwords, such as "Password1" or "admin/admin"."*

**Problem**: `User`-model does not have any password validation checks. Users are allowed to use weak passwords, such as "Password1". 

**Fix**: Use Django built-in `UserCreationForm` which by default enforces strong passwords. 

Import the `User` model from `django.contrib.auth.models` instead of `.models` in **views.py** and **helpers.py**. In **views.py** import `UserCreationForm` from `django.contrib.auth.models`: 

**books/views.py**
```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from .models import User
```

**books/helpers.py**
```python
from django.contrib.auth.models import User
# from .models import User
```

Comment out the existing **register()** view in **views.py** and uncomment the one
with the text *4. A07:2021 – Identification and Authentication Failures fix*:

**books/views.py**

```python
"""
# 4. A07:2021 – Identification and Authentication Failures fix: 
# use Django built-in UserCreationForm and User model
"""
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
                return redirect("index")
            else:
                messages.error(request, "Username already registered.")
    else:
        registration_form = UserCreationForm()
    return render(request, "books/register_with_forms.html", {"registration_form": registration_form})

"""
##################
OLD IMPLEMENTATION
##################
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
                    return redirect("index")
            except ValidationError as e:
                messages.error(request, e.messages[0])
    return render(request, "books/register.html")
"""
```

Fixed view uses the register_with_forms.html-template:

**books/templates/books/register_with_forms.html**
```html
% extends "books/base.html" %}

{% block title %}
    Register
{% endblock %}

{% block content %}
<form action="{% url 'register' %}" method="POST">
    {% csrf_token %}
    {{ registration_form.as_p }}
    <input type="submit" value="Register">
</form>
{% endblock %}
```

### 5. [A05:2021 – Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)

> *"Error handling reveals stack traces or other overly informative error messages to users."*

**Problem**: `DEBUG`-mode is enabled in **settings.py** file, so some errors reveal stack trace and other detailed information for debugging. If this project is meant to be used in production, `DEBUG`-mode needs to be disabled.

**Fix**: Set `DEBUG` to `False` and provide the list of allowed hosts.

Comment out existing debug settings and uncomment the fixed setting with the text *A05:2021 - Security Misconfiguration fix*:

**bookstore/settings.py**
```python
"""
DEBUG = True

ALLOWED_HOSTS = []
"""

"""
A05:2021 – Security Misconfiguration fix: 
disable DEBUG mode in production
"""
DEBUG = False
# Should have the actual host list
ALLOWED_HOSTS = ["*"]
```

### 6. [A07:2021 – Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

> CWE-255 Credentials Management Errors &rarr; Password in Configuration File

**Problem**: **settings.py** contains `SECRET_KEY`

**Fix**: Make `SECRET_KEY` an environment variable:

```sh
$ export SECRET_KEY=secret
```
Comment out the existing `SECRET_KEY` and uncomment imports and code with the text *6. A07:2021 – Identification and Authentication Failures fix*:

**bookstore/settings.py**
```python
import os
from django.core.exceptions import ImproperlyConfigured

# SECRET_KEY = 'django-insecure-&f7)%=_8pb=+222o8za^$oe+wg6+gj+ksq0w43c(3x=gsb%z#j'

"""
6. A07:2021 – Identification and Authentication Failures fix: 
   make SECRET_KEY environment variable
"""
try: 
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    raise ImproperlyConfigured("SECRET_KEY missing from environment variables.")
```
