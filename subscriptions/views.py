import uuid

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from plans.models import Plan
from transactions.models import Transaction
from users.permissions import LoggedInPermission
from .models import UserSubscription
from .serializers import UserSubscriptionSerializer, UserSubscriptionDetailSerializer
from .utils import get_paypal_subscription_plan_id_and_next_billing_date


class UserSubscriptionAPIView(APIView):
    """
    This view deals with payment and updating a user base on the id of the subscription he is making payment with
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        """serializing the user_subscription instance and 
        also the context on the serializer instance enables me tob access the request """
        user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        if not user_subscription.plan:
            # if by mistake the user doesn't have a subscription plan then I create a free lan for the user
            #  we already wrote a post save signal to create a subscription plan for the user if it doesn't exist
            user_subscription.save()

        serializer = UserSubscriptionDetailSerializer(user_subscription, context={"request": request})
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        """
        this  update the user subscription  base on the
        paypal_subscription_id provided
        """
        user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        serializer = UserSubscriptionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        plan_id = serializer.validated_data.get("plan_id")
        paypal_subscription_id = serializer.validated_data.get("paypal_subscription_id")
        plan = Plan.objects.filter(id=plan_id).first()
        if not plan:
            return Response({"error": "Plan does not exist"}, status=400)
        #  to prevent the user from bypassing the system by sending a subscription with the wrong id
        response = get_paypal_subscription_plan_id_and_next_billing_date(paypal_subscription_id)
        if not response:
            #  if an error occurred and which means the response is none
            return Response({"error": "You cant subscribe with a plan id that doesn't  exist in our system"},
                            status=400)
        if plan.paypal_plan_id != response.get("plan_id"):
            return Response({"error": "You cant subscribe with a plan id that doesn't  exist in our system"},
                            status=400)
        #  updating the plan , the paypal_subscription_id  and also the next billing date
        user_subscription.plan = plan
        user_subscription.next_billing_date = response.get("next_billing_date")
        user_subscription.last_payed = timezone.now()
        user_subscription.paypal_subscription_id = paypal_subscription_id
        user_subscription.save()
        #  create a transaction
        transaction = Transaction.objects.create(
            previous_balance=self.request.user.wallet.balance,
            current_balance=self.request.user.wallet.balance,
            user=self.request.user,
            transaction_id=uuid.uuid4().hex,
            transaction_category="SUBSCRIPTION",
            transaction_type="DEBIT",
            transaction_stage="SUCCESSFUL",
            amount=plan.price,
        )
        return Response({"message": "Subscription updated successfully"}, status=200)


class CancelUserSubscriptionAPIView(APIView):
    """this view enables canceling a user subscription which is either  platinum or silver and convert it to free"""
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        user_subscription = request.user.user_subscription
        #  once this is set an automation will be written that checks all subscription
        #  and if the next billing date is the current day, or before it converts the subscription
        if user_subscription.plan.plan_type == "FREE":
            return Response({"error": "You cant cancel a free subscription"}, status=400)
        user_subscription.cancel_on_next = True
        user_subscription.save()
        return Response({"message": "Subscription as being set to cancel on next billing date"}, status=200)
