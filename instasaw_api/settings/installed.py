INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

]

EXTERNAL_INSTALLED_APPS = [

    #  for authentications
    'allauth',
    'allauth.account',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'rest_framework',
    #  if using token authentication
    'rest_framework.authtoken',
    #  using only jwt
    'rest_framework_simplejwt',
]

LOCAL_INSTALLED_APPS = [
    'users',
    'jobs',
    'catalogues',
    'blogs',
]
INSTALLED_APPS += EXTERNAL_INSTALLED_APPS
INSTALLED_APPS += LOCAL_INSTALLED_APPS
