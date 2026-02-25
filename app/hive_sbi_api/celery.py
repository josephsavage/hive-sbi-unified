import os
from celery import Celery
from celery.schedules import crontab

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hive_sbi_api.settings")

# 2. Name the app after your project module for consistency
app = Celery("hive_sbi_api")

# 3. Load config from Django settings, using a 'CELERY' namespace.
# This step tells Celery to look at your Django settings and handles the setup.
app.config_from_object("django.conf:settings", namespace="CELERY")

# 4. Autodiscover tasks from all installed Django apps.
app.autodiscover_tasks()

# Structurally robust Beat Schedule
app.conf.beat_schedule = {
    'sync_members_18': {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=18, minute=0)},
    'sync_members_20': {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=20, minute=24)},
    'sync_members_22': {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=22, minute=48)},
    'sync_members_1':  {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=1, minute=12)},
    'sync_members_3':  {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=3, minute=36)},
    'sync_members_6':  {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=6, minute=0)},
    'sync_members_8':  {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=8, minute=24)},
    'sync_members_10': {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=10, minute=48)},
    'sync_members_13': {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=13, minute=12)},
    'sync_members_15': {'task': 'hive_sbi_api.sbi.tasks.sync_members', 'schedule': crontab(hour=15, minute=36)},
    'clean_task_results': {'task': 'hive_sbi_api.sbi.tasks.clean_task_results', 'schedule': crontab(hour=1, minute=30, day_of_week=1)},
}
