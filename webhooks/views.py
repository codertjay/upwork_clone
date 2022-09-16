from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import LoggedInPermission, LoggedInStaffPermission
from webhooks.models import Webhook
from webhooks.serializers import CreateWebhookSerializer, DeleteWebhookSerializer
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


class ListenToWebhookAPIView(APIView):
    """
    this listens to webhook event for failed payments by the user
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        #  todo :  verify webhook and also convert user subscription for failed auto subscription
        return Response(status=200)
