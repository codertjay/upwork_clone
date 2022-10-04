from .base import *

print('Using production')

DEBUG = False
SECRET_KEY = config("SECRET_KEY")

# fixme: remove later to the domain or ipaddress
ALLOWED_HOSTS = ["*"]

#  read more https://docs.djangoproject.com/en/4.1/ref/middleware/#http-strict-transport-security
# fixme: uncomment this later
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 3600  # one hour
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
#  I JUST ONLY SET THE DATABASE FOR POSTGRES BUT IT COULD BE MODIFIED
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_DB', default=''),
        'USER': config('POSTGRES_USER', default=''),
        'PASSWORD': config('POSTGRES_PASSWORD', default=''),
        'HOST': config('POSTGRES_HOST', default=''),
        'PORT': config('POSTGRES_PORT', default=''),
    }
}

PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_SECRET_KEY = config('PAYPAL_SECRET_KEY')
PAYPAL_URL = config('PAYPAL_URL')
