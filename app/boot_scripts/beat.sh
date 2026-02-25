#!/bin/sh

# 1. Ensure the persistent volume directory exists and is owned by the 'app' user
mkdir -p /app/beat_data
chown -R app:app /app/beat_data

# 2. Execute celery as the app user, pointing the schedule file inside the volume
exec su -m app -c 'celery -A hive_sbi_api beat -l info -s /app/beat_data/celerybeat-schedule --pidfile=/home/app/celery.pid'
