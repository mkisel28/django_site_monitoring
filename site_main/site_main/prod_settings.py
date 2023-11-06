import environ
from pathlib import Path
import os
env = environ.Env()
environ.Env.read_env(".env")
BASE_DIR = Path(__file__).resolve().parent.parent



DEBUG = False
ALLOWED_HOSTS = ['95.164.84.80', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
