from rest_framework.permissions import BasePermission


class CustomerMembershipPermission(BasePermission):
    """
    This permission is meant for the customer and the freelancer it prevents customer with free subscription to create
    multiple jobs it inherits from the logged in permission

    """
    message = "Permission Denied"

    def has_permission(self, request, view):
        #  if the user is not authenticated
        if not request.user.is_authenticated:
            return False
        # check if he isn't currently a freelancer
        if request.user.user_type == "FREELANCER":
            return False
        #  logged in user subscription type
        user_subscription_type = request.user.user_subscription.subscription.subscription_type
        #  using Q lookup to get the user created jobs which is not completed
        user_create_job_queryset = request.user.job_customers.filter_active_and_processing_jobs()
        if user_subscription_type == "FREE":
            #  if the created job which is still progress of the user is  ACTIVE or
            # PROCESSING we cant create job for that user
            if user_create_job_queryset.count() >= 1:
                return False
        # reason while i use elif instead of just else is just to be sure
        elif user_subscription_type == "SILVER":
            return True
        elif user_subscription_type == "PLATINUM":
            return True


