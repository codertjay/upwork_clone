from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
import uuid
from plans.models import Plan
from subscriptions.utils import get_paypal_subscription_status, cancel_paypal_subscription

User = settings.AUTH_USER_MODEL


class UserSubscription(models.Model):
    """
    User subscription which is default set to free which has a foreign key to the subscription model
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4(), editable=False, unique=True)
    user = models.OneToOneField(User, related_name='user_subscription', on_delete=models.CASCADE)
    #  if plan is  null then the user plan is known as free
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, blank=True, null=True)
    paypal_subscription_id = models.CharField(max_length=250, blank=True, null=True)
    # last time a user made payment
    last_payed = models.DateTimeField(blank=True, null=True)
    cancel_on_next = models.BooleanField(default=False)
    next_billing_date = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        #  before saving any UserSubscription I verify the paypal_subscription_id  is active
        if self.plan:
            #  if user has a plan
            if self.plan.plan_type != "FREE":
                paypal_subscription_status = self.check_paypal_subscription_status
                #  if it is not active I changed the subscription to free
                if not paypal_subscription_status:
                    self.convert_user_subscription_to_free()
        elif not self.plan:
            #  if the user has no plan then we use the free plan for the user
            free_subscription, created = Plan.objects.get_or_create(
                plan_type="FREE",
                name="FREE")
            self.plan = free_subscription
        return super(UserSubscription, self).save(*args, **kwargs)

    @property
    def check_paypal_subscription_status(self):
        """
        this function enables checking the subscription status using the  paypal_subscription_id
        :return:  true of false
        """
        try:
            if get_paypal_subscription_status(self.paypal_subscription_id):
                return True
            return False
        except Exception as a:
            #  an error can occur since if a user is on free tier he currently have no subscription on
            #  PayPal and doesn't have paypal_subscription_id
            print(a)
            return False

    def cancel_paypal_subscription(self):
        """
        this function cancel subscription on PayPal to prevent payment being called all the time
        """
        if cancel_paypal_subscription(self.paypal_subscription_id):
            return True
        return False

    def convert_user_subscription_to_free(self):
        """  this convert  the user subscription to free plan"""
        free_subscription, created = Plan.objects.get_or_create(
            plan_type="FREE",
            name="FREE")
        self.plan = free_subscription
        if self.paypal_subscription_id:
            self.cancel_paypal_subscription()
        self.save()


def post_save_create_user_subscription(sender, instance, *args, **kwargs):
    """
    This creates user_subscription once a user is being created
    :param sender:  this is just the model instance
    :param instance:  the user created or updated
    """
    if instance:
        user_subscription = UserSubscription.objects.filter(user=instance).first()
        if not user_subscription:
            user_subscription = UserSubscription.objects.create(user=instance)


post_save.connect(post_save_create_user_subscription, sender=User)
