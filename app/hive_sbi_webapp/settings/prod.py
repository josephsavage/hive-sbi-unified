# app/hive_sbi_webapp/settings/prod.py

from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

ALLOWED_HOSTS = ['*'] 

# --- API Endpoint Configuration ---
# Route traffic through Docker's internal network to the 'api' container on port 8009
SBIAPIURL = os.environ.get('SBI_API_URL', 'http://api:8009')
SBIAPIURL_V1 = os.environ.get('SBI_API_URL_V1', 'http://api:8009')

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
