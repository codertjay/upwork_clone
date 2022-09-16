from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import LoggedInPermission
from .models import UserSubscription
from plans.models import Plan
from .serializers import UserSubscriptionSerializer, UserSubscriptionDetailSerializer
from .utils import get_paypal_subscription_plan_id


class UserSubscriptionAPIView(APIView):
    """
    This view deals with payment and updating a user base on the id of the subscription he is making payment with
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        """serializing the user_subscription instance and 
        also the context on the serializer instance enables me tob access the request """
        user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        serializer = UserSubscriptionDetailSerializer(user_subscription, context={"request": request})
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        """
        this  update the user subscription  base on the
        paypal_subscription_id provided
        """
        user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        serializer = UserSubscriptionSerializer(data=request.data)
        plan_id = serializer.validated_data.get("plan_id")
        paypal_subscription_id = serializer.validated_data.get("paypal_subscription_id")
        plan = Plan.objects.filter(id=plan_id).first()
        if not plan:
            return Response({"error": "Plan does not exist"}, status=400)

        #  to prevent the user from bypassing the system by sending a subscription with the wrong id
        if plan.paypal_plan_id != get_paypal_subscription_plan_id(
                user_subscription.paypal_subscription_id):
            return Response({"error": "You cant subscribe with a plan id that doesn't  exist in our system"},
                            status=400)
        #  updating the plan and the paypal_subscription_id
        user_subscription.plan = plan
        user_subscription.paypal_subscription_id = paypal_subscription_id
        user_subscription.save()
        return Response({"message": "Subscription updated successfully"}, status=200)
