from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('page_one/', views.page_one, name='page_one'),
    path('page_two/', views.page_two, name='page_two'),
    path('profile/', views.profile, name='profile'),
    path('new_chat/', views.new_chat, name='new_chat'),
    path("get_chat_history/<int:chat_id>/", views.get_chat_history, name="get_chat_history"),
    path('delete_chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),


]
