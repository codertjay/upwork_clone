from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction
from users.permissions import LoggedInPermission, LoggedInStaffPermission
from webhooks.models import Webhook, WebhookEvent
from webhooks.serializers import CreateWebhookSerializer, DeleteWebhookSerializer, WebhookEventSerializer
from webhooks.utils import create_webhook, delete_webhook


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
        # this is only for failed payout
        if data.get("event_type") == "PAYMENT.PAYOUTS-ITEM.FAILED":
            #  to be very sure I need to check if the status is really FAILED
            if data.get("resource").get("transaction_status") == "FAILED":
                transaction_id = data.get("resource").get("sender_batch_id")
                transaction = Transaction.objects.filter(transaction_id=transaction_id,
                                                         transaction_stage="PROCESSING").first()
                if transaction:
                    # refund the money of the user
                    transaction.refund_balance()
                    return Response(status=200)

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
