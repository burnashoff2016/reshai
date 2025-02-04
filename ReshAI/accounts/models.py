from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
