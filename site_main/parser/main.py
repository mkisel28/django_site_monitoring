
import time
from pathlib import Path
 
from django.conf import settings
import django



BASE_DIR = Path(__file__).resolve().parent.parent
 
settings.configure(
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'website_parsing',
        'USER': 'postgres',
        'PASSWORD': 'Maksim2001',
        'HOST': 'localhost',
        'PORT': '5432',
        }
    },
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
],
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} | {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{",
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': 'debug1.log',
                'encoding': 'utf-8', 
                "formatter": "verbose",
            },
            "console": {
                'level': 'INFO',
                "formatter": "verbose",
            
                "class": "logging.StreamHandler",

            },
        },
        'loggers': {
            'django': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'controller': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'parsers': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'notification': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
        },
    },


    LANGUAGE_CODE='ru-ru',
    TIME_ZONE="Europe/Moscow",
    USE_I18N=True,
    USE_TZ=True)

django.setup()

from newspaper import Article
article = Article(url)
from controller import main, top_words


while True:

    main()
    top_words()

    time.sleep(60*5)
