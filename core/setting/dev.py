import os
from pathlib import Path
from core.settings import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-v&!uiuu&^nb0rn@2e0u3-&qnt0g8@f+wt02z3du7@21t0klum-'

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_KEY = 'django-insecure-v&!uiuu&^nb0rn@2e0u3-&qnt0g8@f+wt02z3du7@21t0klum-'

ALLOWED_HOSTS = ['www.katyushaiust.ir', 'katyushaiust.ir', '127.0.0.1']

# INSTALLED_APPS = []

# SITE_ID = 2

# Database

# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles',
]

