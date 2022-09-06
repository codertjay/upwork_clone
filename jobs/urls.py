from django.urls import path

from .views import CreateJobAPIView, RetrieveUpdateDestroyJobAPIView, UpdateJobCategoryAPIView, ListCustomerJobAPIView, \
    JobInviteListCreateAPIView, ListJobAPIView, JobInviteRetrieveDestroyAPIView

urlpatterns = [
    # list a customer jobs
    path("customers_jobs/<int:customer_id>/", ListCustomerJobAPIView.as_view(), name="list_customer_jobs"),

    # list jobs ( Reason why I made the create and list different urls is base on the customer permissions
    # for the create which requires more verification)
    path("", ListJobAPIView.as_view(), name="list_jobs"),
    #  create job
    path("create/", CreateJobAPIView.as_view(), name="create_job"),
    path("<int:id>/", RetrieveUpdateDestroyJobAPIView.as_view(), name="retrieve_update_destroy_job"),
    path("<int:id>/update_category/", UpdateJobCategoryAPIView.as_view(), name="update_job_category"),

    #  job invite routes
    path("job_invites/<int:id>/", JobInviteListCreateAPIView.as_view(), name="create_job_invite"),
    #  retrieve and destroy a job invite
    path("job_invites/<int:job_id>/<int:job_invite_id>/", JobInviteRetrieveDestroyAPIView.as_view(),
         name="retrieve_destroy_job_invite"),
]
