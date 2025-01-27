from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Создаём или обновляем профиль пользователя."""
    if created:
        # Если пользователь только что создан, создаём профиль
        UserProfile.objects.create(user=instance)
    else:
        # Если пользователь уже существует, сохраняем профиль (если что-то изменилось)
        instance.profile.save()
