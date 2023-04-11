from core.settings import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-v&!uiuu&^nb0rn@2e0u3-&qnt0g8@f+wt02z3du7@21t0klum-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# INSTALLED_APPS = []

SITE_ID = 2

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'katyusha',
        'USER': 'postgres',
        'PASSWORD': '@dmin2023',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles',
]

# CSRF_COOKIE_SECURE = True