
import time
from pathlib import Path
 
from django.conf import settings
import django

import environ



BASE_DIR = Path(__file__).resolve().parent.parent
 
settings.configure(
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "website_parsing",
        'USER': "postgres",
        'PASSWORD': "Maksim2001",
        'HOST': "localhost",
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
            'telegram_send': {
                'level': 'INFO',
                'class': 'telegram_bot.TelegramLoggingHandler',
                'token': '5839656131:AAEi-43ttcx3nDEh83ij0lz-ajh1EIfp7CU',
                'chat_id': '1689568914',
        },
        },
        'loggers': {
            'django': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'database': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'parsers': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'utils': {
                'handlers': ["console", "file"],
                'level': 'INFO',
                'propagate': True,
            },
            'telegram': {
                'handlers': ['console', 'file', 'telegram_send'],
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

from controller import main, top_words

import logging
logger = logging.getLogger("telegram")


while True:
    try:
        main()
        top_words()
    except Exception as e:
        logger.exception(f"Error: {e}")
        logger.critical(f"Error: {e}")
    time.sleep(60)
