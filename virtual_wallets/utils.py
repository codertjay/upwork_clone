import requests
from django.conf import settings
from django.utils import timezone

from users.utils import get_paypal_access_token

PAYPAL_URL = settings.PAYPAL_URL


def create_paypal_payment(amount):
    """
    this function creates payment on PayPal for a user before it is being approved
    :param amount:
    :return: json response
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v2/checkout/orders"
    response = requests.request(
        'POST', f"{url}",
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{amount}"
                    }
                }
            ]
        },
        headers=headers)
    if response.status_code == 201:
        return response.json()
    return None


def verify_paypal_payment(paypal_id):
    """
    Verify the capture response from the capture order toe check the amount the user paid using
    the payment id and the amount gotten from PayPal
    :param amount: amount paid
    :param paypal_id: order id gotten from PayPal after successful payment
    :return:
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'}
    print('access token', access_token)
    response = requests.request('GET', f"{PAYPAL_URL}v2/checkout/orders/{paypal_id}/", json={},
                                headers=headers)
    print(response.json())
    if response.json().get('status') == 'COMPLETED' or response.json().get('status') == 'APPROVED':
        return True
    return False


def create_paypal_payout(email, amount, transaction_id):
    """
    this function enables withdrawing funds for user
    :param transaction_id: the  transaction id which is a random uuid. which enables us to know who own the webhook once a webhook
    is payout
    :param email: the email we are funding
    :param amount: the amount the user want to withdraw
    :return:
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'}
    timestamp = timezone.now().timestamp()
    response = requests.request(
        'POST', f"{PAYPAL_URL}v1/payments/payouts/",
        json={
            "sender_batch_header": {
                "sender_batch_id": f"{transaction_id}",
                "email_subject": "You have a payout!",
                "email_message": "You have received a payout! Thanks for using our service!"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{amount}",
                        "currency": "USD"
                    },
                    "note": "Thanks for your patronage!",
                    "sender_item_id": f"{transaction_id}",
                    "receiver": f"{email}",
                    "notification_language": "en-US"
                },
            ]
        },
        headers=headers)
    if response.status_code == 201:
        batch_status = response.json().get("batch_header").get("batch_status")
        payout_batch_id = response.json().get("batch_header").get("payout_batch_id")
        #  I only return the values which are needed to work with this transaction
        return {
            "batch_status": batch_status,
            "payout_batch_id": payout_batch_id
        }
    return False
