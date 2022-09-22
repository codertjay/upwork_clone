from enum import auto

from django.db import models


class Webhook(models.Model):
    """the id to get more info about a webhook which is gotten from paypal"""
    webhook_id = models.CharField(max_length=255)


class WebhookEvent(models.Model):
    """
    this saves a webhook notification for reference purpose before we use the webhook for the required purpose
    """
    event_id = models.CharField(max_length=255)
    webhook_event = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
