from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),   # Основной чат
    path('page_one/', views.page_one, name='page_one'),  # Первая новая страница
    path('page_two/', views.page_two, name='page_two'),  # Вторая новая

]
