from rest_framework import serializers


class CreateWebhookSerializer(serializers.Serializer):
    webhook_url = serializers.URLField()
    name = serializers.CharField()


class DeleteWebhookSerializer(serializers.Serializer):
    webhook_id = serializers.CharField()
