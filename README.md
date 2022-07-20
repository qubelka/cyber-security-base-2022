# Cyber security base 2022 course project 

## Project has the following vulnerabilities  from OWASP Top10:2021 list:

### 1. [A01:2021 – Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)


**Problem**: `index.html` has a link to statistics-page which should be visible only to the staff, but the statistics view function does not check whether the user accessing the page is staff member or not. Anyone, even the users that are not registered can access the page by going to the url `localhost:8000/statistics`.

**Fix**: add decorator that checks whether the user is staff member before running the view function:


**helpers.py**
```javascript
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
```javascript
@staff_only 
def statistics(request):
    stats = Book.objects.all()
    return render(request, "books/statistics.html", {"stats": stats})
```
