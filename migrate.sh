#!/bin/bash
#  Get the environment variable of super user email  
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"dev.codertjay@gmail.com.com"}
#  move to the app location
cd /app/

#  collecstatic with no output shown 
/opt/venv/bin/python manage.py collectstatic --noinput
# Make migrations
/opt/venv/bin/python manage.py migrate --noinput
#  migrate the database
/opt/venv/bin/python manage.py migrate --noinput
#  create a super user with the email set
/opt/venv/bin/python manage.py createsuperuser --email $SUPERUSER_EMAIL --noinput || true
