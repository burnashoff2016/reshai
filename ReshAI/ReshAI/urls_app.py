
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  # Если нужно оставить панель администратора:
                  path("admin/", admin.site.urls),

                  # Маршруты аутентификации:
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('accounts/', include('accounts.urls')),

                  # Основной функционал, например chatapp:
                  path('app/', include('chatapp.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
