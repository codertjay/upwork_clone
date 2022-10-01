#!/bin/bash
APP_PORT=${PORT:-8000}
cd /app/
# /opt/venv/bin/daphne  instasaw_api.asgi:application --bind "0.0.0.0:${APP_PORT}"
/opt/venv/bin/daphne -b 0.0.0.0 -p $APP_PORT instasaw_api.asgi:application

