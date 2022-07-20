# Cyber security base 2022 course project 

## Project has the following vulnerabilities  from OWASP Top10:2021 list:

### 1. [A01:2021 – Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)


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