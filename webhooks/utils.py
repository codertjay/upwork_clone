import requests
from django.conf import settings

from users.utils import get_paypal_access_token

PAYPAL_URL = settings.PAYPAL_URL


def create_webhook(webhook_url, name):
    """

    this function create webhook on PayPal to enable this projects listen to some special events we need
    :returns the id if the webhook on PayPal or false
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/notifications/webhooks"
    response = requests.request(
        'POST', f"{url}",
        json={
            "url": f"{webhook_url}",
            "event_types": [
                {
                    "name": f"{name}"
                }
            ]
        },
        headers=headers)
    if response.status_code == 201:
        return response.json().get("id")
    return False


def delete_webhook(webhook_id):
    """
    this function delete webhook on PayPal to enable this projects listen to some special events we need
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/notifications/webhooks/{webhook_id}"
    response = requests.request(
        'DELETE', f"{url}",
        json={},
        headers=headers)
    if response.status_code == 204:
        return True
    return False


{'id': '2AM78778P1057681D', 'url': 'https://api-m.sandbox.paypal.com/v1/notifications/webhooks',
 'event_types': [{'name': '*', 'description': 'ALL'}], 'links': [
    {'href': 'https://api.sandbox.paypal.com/v1/notifications/webhooks/2AM78778P1057681D', 'rel': 'self',
     'method': 'GET'},
    {'href': 'https://api.sandbox.paypal.com/v1/notifications/webhooks/2AM78778P1057681D', 'rel': 'update',
     'method': 'PATCH'},
    {'href': 'https://api.sandbox.paypal.com/v1/notifications/webhooks/2AM78778P1057681D', 'rel': 'delete',
     'method': 'DELETE'}]}
