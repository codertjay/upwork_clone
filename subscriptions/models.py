from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.utils import timezone

from django.conf import settings

User = settings.AUTH_USER_MODEL

SUBSCRIPTION_TYPE_CHOICES = (
    ("FREE", "FREE"),
    ("SILVER", "SILVER"),
    ("PLATINUM", "PLATINUM"),
)


class Subscription(models.Model):
    """
    Available subscription type for the users to choose
    """
    name = models.CharField(max_length=250)
    subscription_type = models.CharField(max_length=50, choices=SUBSCRIPTION_TYPE_CHOICES)
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=timezone.now)


class UserSubscription(models.Model):
    """
    User subscription which is default set to free which has a foreign key to the subscription model
    """
    user = models.OneToOneField(User, related_name='user_subscription', on_delete=models.CASCADE)
    #  if subscription is  null then the user subscription is known as free
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, blank=True, null=True)
    # last time a user made payment
    last_payed = models.DateField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)


def post_save_create_user_subscription(sender, instance, *args, **kwargs):
    """
    This creates user_subscription once a user is being created
    :param instance:  the user created or updated
    """
    if instance:
        user_subscription, created = UserSubscription.objects.get_or_create(user=instance)
        if created:
            #  Create a free subscription model if it doesn't exist or get it
            free_subscription, created = Subscription.objects.get_or_create(subscription_type="FREE", price=0.0)
            # setting the user subscription to free if the user was newly created
            user_subscription.subscription = free_subscription
            user_subscription.save()


post_save.connect(post_save_create_user_subscription, sender=User)


class Wallet(models.Model):
    """
    The wallet models enables tracking of the user, by getting info of amount spent, amount earned
    and the user current balance which can be withdrawn
    """
    user = models.OneToOneField(User, related_name="wallet", on_delete=models.CASCADE)
    earned = models.FloatField(default=0.0)
    spent = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)


