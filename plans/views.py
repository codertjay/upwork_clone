from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from plans.models import Plan
from plans.serializers import PlanSerializer
from users.permissions import LoggedInPermission, LoggedInStaffPermission, NotLoggedInPermission


class PlanCreateAPIView(CreateAPIView):
    """Create a new plan for users and can only be created by the staff members"""
    serializer_class = PlanSerializer
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]


class PlanListAPIView(ListAPIView):
    """
    List all  plan types, and you don't have to be authenticated to access this url
    """
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    permission_classes = [NotLoggedInPermission]


class PlanRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    This deletes the  plan, create a new on or update it .
    Note: I require it should be updated but not deleted base on some users might have subscribed to what
    you would like to delete

    """
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    # will check if the user is staff on the update and destroy function below
    permission_classes = [LoggedInPermission]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        # update the plan
        instance = self.get_object()
        # status before it was updated
        old_plan_status = instance.plan_status
        # check if the user is staff
        if not request.user.is_staff:
            return Response({"error": "You dont have permission to update this plan"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # update the plan status if the status which was provided is not equals the user current one
        if old_plan_status == "ACTIVE" and serializer.validated_data.get(
                "plan_status") == "INACTIVE":
            if not instance.deactivate_plan_plan():
                #  if the plan was not deactivated then I changed it back to what it was
                _ = instance.plan_status == "INACTIVE"
                instance.save()
                return Response({"error": "Error updating plan status"}, status=400)
        if old_plan_status == "INACTIVE" and serializer.validated_data.get(
                "plan_status") == "ACTIVE":
            if not instance.activate_plan():
                #  if the plan was not activated then I changed it back to what it was
                _ = instance.plan_status == "ACTIVE"
                instance.save()
                return Response({"error": "Error updating plan status"}, status=400)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete the plan
        instance = self.get_object()
        # check if the user is staff
        if not request.user.is_staff:
            return Response({"error": "You dont have permission to delete this plan"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)
