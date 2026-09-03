from .base import *

DEBUG = True

# Never fire GA4 for local development traffic.
GA_MEASUREMENT_ID = ''
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda self: True
}

INSTALLED_APPS = [
    'django_extensions',
    'debug_toolbar',
] + INSTALLED_APPS


MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'webapp': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'werkzeug': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
