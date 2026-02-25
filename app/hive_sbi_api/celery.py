import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hive_sbi_api.settings")

# 2. Name the app after your project module for consistency
app = Celery("hive_sbi_api")

# 3. Load config from Django settings, using a 'CELERY' namespace.
# This step tells Celery to look at your Django settings and handles the setup.
app.config_from_object("django.conf:settings", namespace="CELERY")

# 4. Autodiscover tasks from all installed Django apps.
app.autodiscover_tasks()
