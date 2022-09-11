from django.utils import timezone
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import LoggedInStaffPermission, LoggedInPermission, NotLoggedInPermission
from .models import Subscription
from .serializers import SubscriptionSerializer, MakePaymentSerializer, UserSubscriptionSerializer, WalletSerializer


# Create your views here.


class CreateSubscriptionAPIView(CreateAPIView):
    """Create a new subscription for users and can only be created by the staff members"""
    serializer_class = SubscriptionSerializer
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]


class ListSubscriptionsAPIView(ListAPIView):
    """
    List all subscription types, and you don't have to be authenticated to access this url
    """
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = [NotLoggedInPermission]


class RetrieveUpdateDestroySubscriptionAPIView(RetrieveUpdateDestroyAPIView):
    """
    This deletes the subscription, create a new on or update it .
    Note: I require it should be updated but not deleted base on some users might have subscribed to what
    you would like to delete
    """
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    # will check if the user is staff on the update and destroy function below
    permission_classes = [LoggedInPermission]
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        # update the subscription
        instance = self.get_object()
        # check if the user is staff
        if not request.user.is_staff:
            return Response({"error": "You dont have permission to update this subscription"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete the subscription
        instance = self.get_object()
        # check if the user is staff
        if not request.user.is_staff:
            return Response({"error": "You dont have permission to delete this subscription"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class UserSubscriptionAPIView(APIView):
    """
    This view deals with payment and updating a user base on the id of the subscription he is making payment with
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        # serializing the user_subscription instance
        serializer = UserSubscriptionSerializer(request.user.user_subscription)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        # fixme: right now i am just passing the id of the subscription to update the user subscription
        #  not yet handling the payment but this view would be handling the payment
        serializer = MakePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #  getting the subscription
        subscription = Subscription.objects.filter(id=serializer.data['subscription_id']).first()
        if not subscription:
            return Response({"message": "Subscription id does not exist"}, status=400)
        #  updating the user subscription with the subscription we filtered
        #  getting the user subscription with the related name
        user_subscription = request.user.user_subscription
        user_subscription.subscription = subscription
        # setting the time it was updated which enables us to know when to cancel the subscription or monitor
        user_subscription.last_payed = timezone.now()
        user_subscription.save()
        return Response({"message": "Subscription updated successfully"}, status=200)


class WalletAPIView(APIView):
    """
    This returns the wallet balance of the logged-in user and all his require details
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        serializer = WalletSerializer(instance=self.request.user.wallet)
        return Response(serializer.data, status=200)
