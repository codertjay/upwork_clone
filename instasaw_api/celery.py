import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instasaw_api.settings')

# used redis for saving task and running task
app = Celery('instasaw_api', broker=config("CELERY_BROKER_URL"), backend=config("CELERY_BROKER_URL"))
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.conf.broker_url = config("CELERY_BROKER_URL")

#  this is used to make an automation either send mail during a specific time
#  or delete some stuff or more
app.conf.beat_schedule = {
    #  this convert all subscription with cancel at when on due date
    "convert_user_subscription_to_free_on_due_date": {
        "task": 'subscriptions.tasks.cancel_all_user_subscriptions_with_cancel_next',
        "schedule": crontab(hour=23),
    },

}


@app.task
def debug_task():
    print(f'Request: ')
