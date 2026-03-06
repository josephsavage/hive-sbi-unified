# app/hive_sbi_webapp/settings/prod.py

from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

ALLOWED_HOSTS = ['*'] 

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'webapp': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'werkzeug': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    }
}

