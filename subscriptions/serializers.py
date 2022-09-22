from rest_framework import serializers

from plans.serializers import PlanSerializer
from subscriptions.models import UserSubscription
from users.serializers import UserSerializer


class UserSubscriptionDetailSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to view the user subscription only, and it is not accepting any post or put request
    """
    plan = PlanSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "user",
            "plan",
            "paypal_subscription_id",
            "next_billing_date",
            "cancel_on_next",
            "last_payed",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", "user"]


class UserSubscriptionSerializer(serializers.Serializer):
    """
    this serializer is used to update the user subscription after a payment was successful
    """
    plan_id = serializers.CharField(max_length=250)
    paypal_subscription_id = serializers.CharField(max_length=250)

    def validate_paypal_subscription_id(self, obj):
        """This checks if the paypal_subscription_id has been used before and if it already exists by another user it
        raises an error and also the request is passed from the view to access the current user
        """
        #  check the paypal_subscription_id if it has been used by another user
        logged_in_user_subscription = self.context['request'].user.user_subscription
        user_subscription = UserSubscription.objects.filter(paypal_subscription_id=obj).first()
        if user_subscription:
            #  in here we are preventing the user from using the PayPal subscription id of another user
            if logged_in_user_subscription != user_subscription:
                raise serializers.ValidationError(
                    'Please use a valid subscription id that has not been used before by another user')
        return obj


