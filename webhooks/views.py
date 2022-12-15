from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction
from users.permissions import LoggedInPermission, LoggedInStaffPermission
from webhooks.models import Webhook, WebhookEvent
from webhooks.serializers import CreateWebhookSerializer, DeleteWebhookSerializer, WebhookEventSerializer
from webhooks.utils import create_webhook, delete_webhook, list_webhook


class CreateWebhookAPIView(APIView):
    """this class create webhook base on PayPal documentation but right now we are only using it to create
    failed subscription webhook only
    """
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]

    def post(self, request, *args, **kwargs):
        serializer = CreateWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        webhook_url = serializer.validated_data.get("webhook_url")
        name = serializer.validated_data.get("name")
        webhook_id = create_webhook(webhook_url=webhook_url, name=name)
        #  create a webhook which we listen to
        if not webhook_id:
            return Response({"error": "You cannot create a webhook right now"}, status=400)
        #  create a webhook with the id provided
        Webhook.objects.create(webhook_id=webhook_id)
        return Response({"message": "Webhook successfully created"}, status=200)


class DeleteWebhookAPIView(APIView):
    """this class delete webhook base on PayPal documentation
    """
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]

    def post(self, request, *args, **kwargs):
        # For debugging to list the webhook is if it exists
        print(list_webhook())
        serializer = DeleteWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        webhook_id = serializer.validated_data.get("webhook_id")
        #  delete a webhook which we listen to using the id of the webhook
        if not delete_webhook(webhook_id=webhook_id):
            return Response({"error": "You cant delete a webhook that doesn't exist"}, status=400)
        webhook = Webhook.objects.filter(webhook_id=webhook_id).first()
        if webhook:
            webhook.delete()
        return Response({"message": "Successfully deleted webhook"}, status=200)


""""
PAYOUT 
The possible values are:

SUCCESS. Funds have been credited to the recipient’s account.
FAILED. This payout request has failed, so funds were not deducted from the sender’s account.
PENDING. Your payout request was received and will be processed.
UNCLAIMED. The recipient for this payout does not have a PayPal account. A link to sign up for a PayPal account was sent
to the recipient. However, if the recipient does not claim this payout within 30 days, the funds are returned to your 
account.
RETURNED. The recipient has not claimed this payout, so the funds have been returned to your account.
ONHOLD. This payout request is being reviewed and is on hold.
BLOCKED. This payout request has been blocked.
REFUNDED. This payout request was refunded.
REVERSED. This payout request was reversed
"""


class ListenToWebhookEventAPIView(APIView):
    """
    this listens to webhook event for failed payments by the user
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        webhook, created = WebhookEvent.objects.get_or_create(event_id=request.data.get("id"),
                                                              webhook_event=request.data)
        # This is meant for payout when the user withdraws money from their account
        if data.get("resource_type") == "payouts_item":
            #  to be very sure I need to check if the status is really FAILED
            transaction_id = data.get("resource").get("sender_batch_id")
            transaction = Transaction.objects.filter(transaction_id=transaction_id).first()
            if not transaction:
                return Response(status=200)
            transaction_stage = data.get("resource").get("transaction_status")
            if (
                    transaction_stage == "FAILED" or
                    transaction_stage == "RETURNED" or
                    transaction_stage == "REFUNDED" or
                    transaction_stage == "REVERSED" or
                    transaction_stage == "BLOCKED"
            ):
                # refund the money of the user
                transaction.refund_balance()
                transaction.transaction_stage = "FAILED"
                transaction.save()
            elif transaction_stage == "UNCLAIMED":
                # If the money has not been claimed after
                transaction.transaction_stage = "PROCESSING"
                transaction.save()
            elif transaction_stage == "SUCCESSFUL":
                # If the transaction was successful
                transaction.transaction_stage = "SUCCESSFUL"
                transaction.save()
        # Lets check for subscription if auto subscribe failed
        elif data.get("resource_type") == "payouts_item":
            pass

        return Response(status=200)


# check this code to learn how to verify webhook
# https://github.com/paypal/PayPal-Python-SDK/blob/master/paypalrestsdk/notifications.py


class WebhookEventListAPIView(ListAPIView):
    """List all webhook events"""
    serializer_class = WebhookEventSerializer
    queryset = WebhookEvent.objects.all()
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]


class WebhookEventDetailAPIView(RetrieveAPIView):
    """Detail  of a webhook event"""
    serializer_class = WebhookEventSerializer
    queryset = WebhookEvent.objects.all()
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]
    lookup_field = "id"


{
    "payout_item_id": "8AELMXH8UB2P8",
    "transaction_id": "0C413693MN970190K",
    "activity_id": "0E158638XS0329106",
    "transaction_status": "SUCCESS",
    "payout_item_fee": {
        "currency": "USD",
        "value": "0.35"
    },
    "payout_batch_id": "Q8KVJG9TZTNN4",
    "payout_item": {
        "amount": {
            "value": "9.87",
            "currency": "USD"
        },
        "recipient_type": "EMAIL",
        "note": "Thanks for your patronage!",
        "receiver": "receiver@example.com",
        "sender_item_id": "14Feb_234"
    },
    "time_processed": "2018-01-27T10:17:41Z",
    "links": [
        {
            "rel": "self",
            "href": "https://api-m.sandbox.paypal.com/v1/payments/payouts-item/8AELMXH8UB2P8",
            "method": "GET"
        },
        {
            "href": "https://api-m.sandbox.paypal.com/v1/payments/payouts/Q8KVJG9TZTNN4",
            "rel": "batch",
            "method": "GET"
        }
    ]
}

{'id': 'WH-64R10817XA050051G-3RL93107GC167834E', 'event_version': '1.0', 'create_time': '2022-09-21T10:27:08.853Z',
 'resource_type': 'payouts', 'event_type': 'PAYMENT.PAYOUTSBATCH.SUCCESS',
 'summary': 'Payouts batch completed successfully.', 'resource': {
    'batch_header': {'payout_batch_id': 'B76ZYZAL3F2NL', 'batch_status': 'SUCCESS',
                     'time_created': '2022-09-21T10:26:49Z', 'time_completed': '2022-09-21T10:26:50Z',
                     'sender_batch_header': {'sender_batch_id': 'c4b90b1454e54f5ab455a7652f5e7109'},
                     'funding_source': 'BALANCE', 'amount': {'currency': 'USD', 'value': '50.00'},
                     'fees': {'currency': 'USD', 'value': '0.25'}, 'payments': 1}, 'links': [
        {'href': 'https://api.sandbox.paypal.com/v1/payments/payouts/B76ZYZAL3F2NL', 'rel': 'self', 'method': 'GET',
         'encType': 'application/json'}]}, 'links': [
    {'href': 'https://api.sandbox.paypal.com/v1/notifications/webhooks-events/WH-64R10817XA050051G-3RL93107GC167834E',
     'rel': 'self', 'method': 'GET'}, {
        'href': 'https://api.sandbox.paypal.com/v1/notifications/webhooks-events/WH-64R10817XA050051G-3RL93107GC167834E/resend',
        'rel': 'resend', 'method': 'POST'}]}
