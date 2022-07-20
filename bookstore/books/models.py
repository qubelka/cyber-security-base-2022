from django.db import models
import hashlib
from django.core.exceptions import ValidationError
from django.db import models


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
