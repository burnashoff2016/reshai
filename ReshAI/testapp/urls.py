from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.AllToDos.as_view(), name="index"),
    path("today/", views.TodayToDos.as_view(), name="today"),
    path("add/", views.add_todo, name="add"),
    path("chat/", views.chat, name="chat"),
]
