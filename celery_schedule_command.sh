#!/bin/bash
cd /app/
# Use the venv
/opt/venv/bin/celery -A instasaw_api beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler