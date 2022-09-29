#!/bin/bash
cd /app/

nohup celery -A instasaw_api worker  --loglevel=info >/dev/null 2>&1 &
nohup celery -A instasaw_api beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler >/dev/null 2>&1 &