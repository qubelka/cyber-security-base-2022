from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("statistics", views.statistics, name="statistics"),
    path("books/<slug:slug>", views.book, name="book"),
    # A03:2021 – Injection fix: use Django templates
    # path("comment/<slug:slug>", views.comment, name="comment"),
    path("comment", views.comment, name="comment"),
]
