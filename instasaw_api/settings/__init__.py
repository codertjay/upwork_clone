from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
if DEBUG == True:
    from .local import *
elif DEBUG == False:
    from .production import *
