#!/bin/bash
APP_PORT=${PORT:-8001}
cd /app/
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm instasaw_api.wsgi:application --bind "0.0.0.0:${APP_PORT}"
