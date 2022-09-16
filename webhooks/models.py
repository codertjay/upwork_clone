from django.db import models


class Webhook(models.Model):
    """the id to get more info about a webhook which is gotten from paypal"""
    webhook_id = models.CharField(max_length=255)
