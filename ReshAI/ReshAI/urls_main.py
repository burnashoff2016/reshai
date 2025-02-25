# ReshAI/urls_main.py
from django.urls import path, include

urlpatterns = [
    path('', include('mainapp.urls')),
]
