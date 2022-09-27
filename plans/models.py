from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
import uuid

from plans.utils import create_paypal_plan, update_paypal_plan_amount, activate_paypal_plan, deactivate_paypal_plan

User = settings.AUTH_USER_MODEL

PLAN_TYPE_CHOICES = (
    ("FREE", "FREE"),
    ("SILVER", "SILVER"),
    ("PLATINUM", "PLATINUM"),
)
PLAN_STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE"),
)


class Plan(models.Model):
    """
    Available subscription type for the users to choose it more of like  plan
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250)
    # making it unique to prevent staff from creating deplicate subscription type
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPE_CHOICES, unique=True)
    #  the status of the subscription
    plan_status = models.CharField(max_length=50, choices=PLAN_STATUS, default="ACTIVE")
    paypal_plan_id = models.CharField(blank=True, null=True, max_length=1000)
    price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=99999)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def activate_plan(self):
        """this activates a  plan if it is not activate"""
        is_successful = activate_paypal_plan(self.paypal_plan_id)
        if is_successful:
            self.plan_status = "ACTIVE"
            self.save()
        return is_successful

    def deactivate_plan_plan(self):
        """this deactivates a  plan if it is not activated, and it returns bool if it was successful or
        not """
        is_successful = deactivate_paypal_plan(self.paypal_plan_id)
        if is_successful:
            self.plan_status = "INACTIVE"
            self.save()
        return is_successful


def post_save_create_plan(sender, instance, *args, **kwargs):
    """
    This creates  plan  base on the type provided
    if the plan_type is sliver the interval would be monthly ,
    and if platinum ................
    and if the plan id already exists and just try updating with the price which was set
    """
    if instance:
        # if the plan is active thats when we can create a paypal plan a get a plan id from paypal
        #  but it it is active and the plan has been created before then we only update the plan with paypal
        #  url to update amount
        if instance.plan_status == "ACTIVE":
            interval = "Month"
            if instance.plan_type == "SILVER":
                #  Setting the interval for silver
                interval = "Month"
            if instance.plan_type == "PLATINUM":
                #  Setting the interval for PLATINUM
                interval = "Year"
            if not instance.paypal_plan_id and instance.plan_type != "FREE":
                #  create the plan if we haven't created it .
                #  we first check if paypal_plan_id doesn't exist to prevent duplicate
                plan_id = create_paypal_plan(
                    amount=instance.price,
                    name=instance.plan_type,
                    interval=interval)
                if plan_id:
                    instance.paypal_plan_id = plan_id
                    instance.save()
            else:
                #  if the plan id already exist then I update the plan amount on PayPal
                update_paypal_plan_amount(amount=instance.price, plan_id=instance.paypal_plan_id)


post_save.connect(post_save_create_plan, sender=Plan)
