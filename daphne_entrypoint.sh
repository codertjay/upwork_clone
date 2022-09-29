#!/bin/bash
APP_PORT=${PORT:-8002}
cd /app/
/opt/venv/bin/daphne  instasaw_api.asgi:application --bind "0.0.0.0:${APP_PORT}"
