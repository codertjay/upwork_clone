import requests

from users.utils import PAYPAL_URL, get_paypal_access_token


def verify_paypal_payment(amount, paypal_id):
    """
    Verify the capture response from the capture order toe check the amount the user paid using
    the payment id and the amount gotten from PayPal
    :param amount: amount paid
    :param paypal_id: order id gotten from PayPal after successful payment
    :return:
    """
    try:
        access_token = get_paypal_access_token()
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {access_token}'}
        print('access token', access_token)
        response = requests.request('GET', f"{PAYPAL_URL}v2/checkout/orders/{paypal_id}/", json={},
                                    headers=headers)
        print(response.json())
        if response.json().get('status') == 'COMPLETED' or response.json().get('status') == 'APPROVED':
            amount_details = response.json().get("purchase_units")[0].get('amount')
            print('the amount details', amount_details)
            # verify if the payment made is correct and check amount paid
            # minus one from our total because of some issues that might occur maybe .2 cent issue
            amount -= 1
            if float(amount_details.get('value')) >= amount and amount_details.get("currency_code") == "USD":
                return True
    except Exception as a:
        print(a)
        return False
