from rest_framework import serializers

from webhooks.models import WebhookEvent


class CreateWebhookSerializer(serializers.Serializer):
    webhook_url = serializers.URLField()
    name = serializers.CharField()


class DeleteWebhookSerializer(serializers.Serializer):
    webhook_id = serializers.CharField()


class WebhookEventSerializer(serializers.ModelSerializer):
    """
    this is just to list all event sent by paypal
    """

    class Meta:
        model = WebhookEvent
        fields = [
            "event_id",
            "webhook_event",
        ]
