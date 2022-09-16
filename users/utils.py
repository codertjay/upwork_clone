import requests
from django.conf import settings

PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET_KEY = settings.PAYPAL_SECRET_KEY
PAYPAL_URL = settings.PAYPAL_URL


def get_paypal_access_token():
    """
    This get the access token from PayPal by logging in with both the  PAYPAL_CLIENT_ID and
    PAYPAL_SECRET_KEY
    :return: access_token
    """
    data = {"grant_type": "client_credentials"}
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    url = f"{PAYPAL_URL}v1/oauth2/token"
    response = requests.post(
        url,
        auth=(PAYPAL_CLIENT_ID,
              PAYPAL_SECRET_KEY),
        headers=headers,
        data=data).json()
    return response.get('access_token')


def generate_client_token():
    """
    Generate a user token which is used in the front end paypal url for payment
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'}
    url = f"{PAYPAL_URL}v1/identity/generate-token"
    response = requests.request('POST', f"{url}", json={},
                                headers=headers)
    if response.status_code == 200:
        return response.json().get('client_token')
    return None
