"""
Django settings for ReshAI project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-le$($#9#8^n2l*169u+p9!3fl@xd=)s2la%c%ms^9mgqkjrqxb')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DJANGO_DEBUG', True))

ALLOWED_HOSTS = [
    'lvh.me',
    '.lvh.me',
    "localhost",
    "127.0.0.1",
    "app.resh-ai.ru",
    "www.app.resh-ai.ru",
    "resh-ai.ru",
    "www.resh-ai.ru",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_hosts',
    'accounts.apps.AccountsConfig',
    'chatapp',
    'mainapp',
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'middleware.maintenance_middleware.MaintenanceModeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

MAINTENANCE_MODE = False  # True - сайт в режиме тех.работ, False - сайт работает

ROOT_HOSTCONF = 'ReshAI.hosts'
DEFAULT_HOST = 'www'
ROOT_URLCONF = 'ReshAI.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ReshAI.wsgi.application'
ASGI_APPLICATION = 'ReshAI.asgi.application'
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'reshai',  # Имя вашей базы данных
        'USER': 'artem',  # Имя пользователя
        'PASSWORD': 'Qz754wx04ec95',  # Пароль server
        # 'PASSWORD': 'reshai',  # Пароль local
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTH_USER_MODEL = 'accounts.CustomUser'  # custom user model

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = "/var/www/reshai/staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # send emails to console
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB


