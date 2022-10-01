#!/bin/bash
cd /app/

# Use the venv
/opt/venv/bin/celery -A instasaw_api worker  --loglevel=info
