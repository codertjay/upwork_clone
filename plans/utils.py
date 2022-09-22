from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from users.utils import get_paypal_access_token

#  using the url which was set in settings base on the server mode if its on debug or live
PAYPAL_URL = settings.PAYPAL_URL


def create_paypal_time_format(minutes: int):
    """
    this function helps to create a time in PayPal format, and it requires the minutes
     which is added to current time to be returned
    :param minutes: the minutes to be added to current time
    :return:
    """
    time = timezone.now() + timedelta(minutes=20)
    # setting the effective time to this format 2022-11-01T00:00:00Z
    effective_time = f"{time.year}-{time.month}-{time.day}T{time.hour}:{time.minute}:{time.second}Z"
    return effective_time


def create_paypal_product(name):
    """
    this enables creating product for subscription plan .
    its more of like PayPal requires a product id to creates subscription plan
    :return: product_id form PayPal
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/catalogs/products"
    timestamp = timezone.now().timestamp()
    response = requests.request(
        'POST', f"{url}",
        json={
            "name": name,
            "type": "SERVICE",
            "id": f"{timestamp}",
            "description": f"{name} product",
            "category": "SERVICES",
            "image_url": "https://goldfish-app-ds6s2.ondigitalocean.app/static/media/mockup.53cce83449ac827503c2.png",
            "home_url": "https://goldfish-app-ds6s2.ondigitalocean.app/static/media/mockup.53cce83449ac827503c2.png"
        },
        headers=headers)
    if response.status_code == 201:
        return response.json().get("id")
    return None


def create_paypal_plan(amount, name, interval):
    """
    Created an order from PayPal which include the price
    :param interval:  which could be month , week or year
    :param name:  the name of the subscription
    :param amount: the amount we want the user t to pay on the schedule
    :return the plan_id or None
    """
    #  using the access token I created above
    intervals = ["Day", "Week", "Month", "Year"]
    #  I check if the interval provided is valid
    if interval not in intervals:
        return None
    #  create a product id
    product_id = create_paypal_product(name)
    if product_id is None:
        #  if product id is not returned
        return None
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/plans"
    response = requests.request(
        'POST', f"{url}",
        json={
            "product_id": product_id,
            "name": name,
            "description": f"Plan for user for {interval} package.",
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": interval.upper(),
                        # THE TOTAL COUNT THE USER WILL BE BILLED ON THIS MONTHLY PLAN or YEAR PLAN
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    # the total time the subscription could be called . if total_cycles is 0 then it is infinite
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": int(amount),
                            "currency_code": "USD"
                        }
                    }
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "payment_failure_threshold": 1
            },

        },
        headers=headers)
    if response.status_code == 201:
        if response.json().get("status") == "ACTIVE":
            return response.json().get("id")
    return None


def update_paypal_plan_amount(amount, plan_id):
    """
   Update a plan price
    :param plan_id: the plan id we want to update
    :param amount: the amount we want the user has to pay on the schedule
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/plans/{plan_id}/update-pricing-schemes"
    effective_time = create_paypal_time_format(20)
    response = requests.request(
        'POST', f"{url}",
        json={
            "pricing_schemes": [
                {
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": int(amount),
                            "currency_code": "USD"
                        },
                        "roll_out_strategy": {
                            "effective_time": effective_time,
                            "process_change_from": "NEXT_PAYMENT"
                        }
                    }
                },

            ]
        },
        headers=headers)
    if response.status_code == 204:
        return True
    return False


def activate_paypal_plan(plan_id):
    """
   Activate the plan if it was deactivated before
    :param plan_id: the plan id we want to update
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/plans/{plan_id}/activate"
    response = requests.request(
        'POST', f"{url}",
        json={},
        headers=headers)
    #  it returns 204 on successful update
    if response.status_code == 204:
        return True
    return False


def deactivate_paypal_plan(plan_id):
    """
   Deactivate the plan if it is active
    :param plan_id: the plan id we want to update
    """
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'
               }
    url = f"{PAYPAL_URL}v1/billing/plans/{plan_id}/deactivate"
    response = requests.request(
        'POST', f"{url}",
        json={},
        headers=headers)
    #  it returns 204 on successful update
    if response.status_code == 204:
        return True
    return False
