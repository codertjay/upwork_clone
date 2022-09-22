import requests
from django.conf import settings

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


def get_paypal_subscription_plan_id_and_next_billing_date(paypal_subscription_id):
    """
Please don't mind how long this function is

    This function is used to get the  plan id using the subscription id of a user gotten from PayPal
    it is just used to verify the user plan id he paid for
    currently use in the post request on the user_subscription url
    :param paypal_subscription_id: the user subscription id which is used to get more details about a user subscription
    :return: paypal_subscription_plan_id and next_billing_date if successful or valid
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
        plan_id = response.json().get('plan_id')
        next_billing_time = response.json().get("billing_info").get("next_billing_time")
        return {
            "plan_id": plan_id,
            "next_billing_date": next_billing_time,
        }
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
        if subscription_status == 'ACTIVE' or subscription_status == "APPROVED":
            return True
    return False


def cancel_paypal_subscription(paypal_subscription_id):
    """
    this function cancel PayPal subscription on a particular user
    :param paypal_subscription_id: the user paypal_subscription_id
    :return:
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/subscriptions/{paypal_subscription_id}/cancel"
    response = requests.request(
        'POST', f"{url}",
        json={
            "reason": "User no more interested"
        },
        headers=headers)
    if response.status_code == 204:
        return True
    return False



