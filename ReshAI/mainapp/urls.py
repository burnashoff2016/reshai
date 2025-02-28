from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('chat/', views.chat_redirect, name='chat_redirect'),
    path('price/', views.price, name='price'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
