from django.urls import path

from .views import JobCreateAPIView, JobRetrieveUpdateDestroyAPIView, JobCategoryUpdateAPIView, CustomerJobListAPIView, \
    JobInviteListCreateAPIView, JobListAPIView, JobInviteRetrieveDestroyAPIView, ProposalRetrieveUpdateDestroyAPIView, \
    ProposalListAPIView

urlpatterns = [
    # Job routes
    # list a customer jobs
    path("customer_jobs/<int:customer_id>/", CustomerJobListAPIView.as_view(), name="list_customer_jobs"),
    # list jobs ( Reason why I made the create and list different urls is base on the customer permissions
    # for the CREATE it requires more verification)
    path("", JobListAPIView.as_view(), name="list_jobs"),
    path("create/", JobCreateAPIView.as_view(), name="create_job"),
    path("<int:id>/", JobRetrieveUpdateDestroyAPIView.as_view(), name="retrieve_update_destroy_job"),
    path("<int:id>/update_category/", JobCategoryUpdateAPIView.as_view(), name="update_job_category"),

    #  Job invite routes
    path("job_invites/<int:id>/", JobInviteListCreateAPIView.as_view(), name="create_job_invite"),
    #  retrieve and destroy a job invite
    path("job_invites/<int:job_id>/<int:job_invite_id>/", JobInviteRetrieveDestroyAPIView.as_view(),
         name="retrieve_destroy_job_invite"),

    # Job Proposal routes
    path("proposals/<int:job_id>/", ProposalListAPIView.as_view(), name="list_proposals"),
    path("proposals/<int:job_id>/<int:proposal_id>/", ProposalRetrieveUpdateDestroyAPIView.as_view(),
         name="retrieve_update_destroy_proposal")

]
