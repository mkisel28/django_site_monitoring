import environ
from pathlib import Path
import os
env = environ.Env()
environ.Env.read_env("./.env")
BASE_DIR = Path(__file__).resolve().parent.parent


SESSION_COOKIE_AGE = 1209600  
DEBUG = True
ALLOWED_HOSTS = ['95.164.38.75:1137', '95.164.38.75', "db"]
CSRF_TRUSTED_ORIGINS = ['http://95.164.38.75:1137', 'http://95.164.38.75']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

STATIC_URL = "/static/"
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
