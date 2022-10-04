from decouple import config

SECRET_KEY = config("SECRET_KEY")

DEBUG = config('DEBUG', default=False, cast=bool)
if DEBUG == True:
    from .local import *
elif DEBUG == False:
    from .production import *
