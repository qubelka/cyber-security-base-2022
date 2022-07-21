# Cyber security base 2022 course project 

## Running the application

```sh
$ cd bookstore
$ python3 manage.py runserver 
```

## Project has the following vulnerabilities  from OWASP Top10:2021 list:

### 1. [A01:2021 – Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)

> *"Bypassing access control checks by modifying the URL (parameter tampering or force browsing), internal application state, or the HTML page, or by using an attack tool modifying API requests."*

**Problem**: `index.html` has a link to statistics-page which should be visible only to the staff, but the statistics view function does not check whether the user accessing the page is staff member or not. Anyone, even the users that are not registered can access the page by going to the url `localhost:8000/statistics`.

**Fix**: add decorator that checks whether the user is staff member before running the view function:


**helpers.py**
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

**views.py**
```python
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

We can comment out existing `User` model code:

**models.py**
```python
'''
class UserManager(models.Manager):
    def create_user(self, username, password):
        if username == "":
            raise ValidationError({"username": ("Username is required.")})
        if password == "":
            raise ValidationError({"password": ("Password is required.")})
        if len(username) > 150:
            raise ValidationError(
                {"username": ("Username must be max 150 characters long.")}
            )
        user = self.model(username=username)
        user.set_password(password)
        user.save()
        return user


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=32)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    def __str__(self):
        return self.username

    def set_password(self, password):
        self.password = hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        return hashlib.md5(password.encode()).hexdigest() == self.password
'''
```

and import `User` from `django.contrib.auth.models` in **views.py** and **helpers.py**:

**views.py**
```python
from django.contrib.auth.models import User
# from .models import User

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
                if user:
                    authenticate(request, username, password1)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return render(request, "books/register.html")
            return redirect("index")
    return render(request, "books/register.html")
```

**helpers.py**
```python
from django.contrib.auth.models import User
# from .models import User
...
```

### 3. [A03:2021 – Injection](https://owasp.org/Top10/A03_2021-Injection/)

> *"User-supplied data is not validated, filtered, or sanitized by the application."*

**Problem**: `book`-view renders plain HTML and contains a form for leaving comments. This page is vulnerable to Cross Site Scripting (XSS) attacks. 

For example by leaving a comment 
```html 
<script>window.location="https://craftinginterpreters.com";</script>
```
page visitors will be always redirected to the site `craftinginterpreters.com`. 

**Fix**: Use Django templates. Django templates protect against the majority of XSS attacks. The following changes to the code will enable Django template in `book`-view:

**urls.py**
```python 
urlpatterns = [
    ...
    path("comment/<slug:slug>", views.comment, name="comment"),
]
```

**views.py**
```python 
@login_required
def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    comments = book.comments.all()
    return render(request, "books/book.html", {"book" : book, "comments": comments})
```

**book.html**

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

**views.py**

```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from .models import User
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
```

We also change **helpers.py** to use Django built-in `User`-model with `UserCreationForm`:

**helpers.py**
```python
from django.contrib.auth.models import User
# from .models import User
...
```

And create a new registration template which uses forms:

**register_with_forms.html**
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