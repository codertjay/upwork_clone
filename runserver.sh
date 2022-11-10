#!/bin/bash
APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py runserver 0.0.0.0:${APP_PORT}

