from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from plans.utils import PAYPAL_URL
from users.utils import get_paypal_access_token

PAYPAL_URL = settings.PAYPAL_URL


def paypal_subscription_details(plan_id):
    """
    This enables checking  subscription for user on PayPal which we use to know
    if the user current subscription is active
    :param plan_id: the plan id the user want to subscribe to
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/subscriptions/{plan_id}"
    response = requests.request(
        'GET', f"{url}",
        json={},
        headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def get_paypal_subscription_plan_id(paypal_subscription_id):
    """
    This function is used to get the  plan id using the subscription id of a user gotten from paypal
    it is just used to verify the user plan id he paid for
    currently use in the post request on the user_subscription url
    :param paypal_subscription_id: the user subscription id which is used to get more details about a user subscription
    :return: paypal_subscription_plan_id
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/subscriptions/{paypal_subscription_id}"
    response = requests.request(
        'GET', f"{url}",
        json={},
        headers=headers)
    if response.status_code == 200:
        return response.json().get('plan_id')
    return None


def get_paypal_subscription_status(paypal_subscription_id):
    """
    This function is used to get the status of a subscription
    :param paypal_subscription_id: the user subscription id which is used to get more details about a user subscription
    :return: True or False if the subscription is active or Not
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/subscriptions/{paypal_subscription_id}"
    response = requests.request(
        'GET', f"{url}",
        json={},
        headers=headers)
    if response.status_code == 200:
        subscription_status = response.json().get('status')
        if subscription_status == 'ACTIVE' or subscription_status == "APPROVAL_PENDING" or subscription_status == "APPROVED":
            return True
    return False
