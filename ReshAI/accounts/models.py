from django.contrib.auth.models import AbstractUser
from django.db import models

# Модель пользователя для auth
class CustomUser(AbstractUser):
    # Добавляем дополнительные поля
    # phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


# Модель профиля пользователя
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')  # Связываем с CustomUser
    bio = models.TextField(blank=True, null=True)  # Пример поля для биографии
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Поле для аватара
    date_of_birth = models.DateField(null=True, blank=True)  # Пример поля для даты рождения
    location = models.CharField(max_length=100, blank=True)  # Местоположение

    def __str__(self):
        return f"Profile of {self.user.username}"
