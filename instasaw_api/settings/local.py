from .base import *

print('Using local')
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DEBUG = True

ALLOWED_HOSTS = ['*']
SECRET_KEY = config("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


PAYPAL_CLIENT_ID = config('DEBUG_PAYPAL_CLIENT_ID')
PAYPAL_SECRET_KEY = config('DEBUG_PAYPAL_SECRET_KEY')
PAYPAL_URL = config('DEBUG_PAYPAL_URL')

CORS_ALLOW_ALL_ORIGINS=True