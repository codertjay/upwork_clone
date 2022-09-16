from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import UserSubscription


@shared_task
def cancel_all_user_subscriptions_with_cancel_next():
    """
    This tasks cancel all user subscription with the value cancel next when it is set to true
    and convert them to free
    :return:
    """
    user_subscription_qs = UserSubscription.objects.filter(cancel_on_next=True)
    for user_subscription in user_subscription_qs:
        #  canceling the subscription three days before the date it should be canceled
        three_days_before_now = timedelta(days=3)
        date_to_be_cancelled = user_subscription + three_days_before_now
        if date_to_be_cancelled >= timezone.now():
            user_subscription.convert_user_subscription_to_free()
    return True
