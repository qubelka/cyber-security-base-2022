import datetime
from django.db import models
import hashlib
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator


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


def current_year():
    return datetime.date.today().year


class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    published = models.IntegerField(
        validators=[MaxValueValidator(1900), MinValueValidator(current_year())]
    )
    slug = models.SlugField(max_length=250, unique=True)
    total = models.IntegerField(default=50)
    sold = models.IntegerField(default=0)

    class Meta:
        ordering = ("-published",)

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse("book", args=[self.slug])

    @property
    def in_stock(self):
        return self.total - self.sold > 0

    @property
    def available(self):
        return self.total - self.sold
