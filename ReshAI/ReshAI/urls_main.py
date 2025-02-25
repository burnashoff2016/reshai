
from django.urls import path
from django.http import HttpResponse
from django.urls import path, include

def main_index(request):
    return HttpResponse("Главная страница основного домена. Здесь в будущем будет ваше основное приложение.")

urlpatterns = [
    path('', include('mainapp.urls')),
]
