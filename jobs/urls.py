from django.urls import path

from .views import JobCreateAPIView, JobRetrieveUpdateDestroyAPIView, JobCategoryUpdateAPIView, CustomerJobListAPIView, \
    JobInviteListCreateAPIView, JobListAPIView, JobInviteRetrieveDestroyAPIView, ProposalRetrieveUpdateDestroyAPIView, \
    ProposalListAPIView, GivenReviewListAPIView, ReceivedReviewListAPIView, ReviewDetailAPIView, ModifyProposalAPIView, \
    CreateContractAPIView, CustomerContractListAPIView, FreelancerActiveContractsListAPIView, ContractRetrieveAPIView, \
    MarkContractCompletedAPIView

urlpatterns = [
    # Job routes
    # list a customer jobs
    path("customer_jobs/<str:customer_id>/", CustomerJobListAPIView.as_view(), name="list_customer_jobs"),
    # list jobs ( Reason why I made the create and list different urls is base on the customer permissions
    # for the CREATE it requires more verification)
    path("", JobListAPIView.as_view(), name="list_jobs"),
    path("create/", JobCreateAPIView.as_view(), name="create_job"),
    path("<str:id>/", JobRetrieveUpdateDestroyAPIView.as_view(), name="retrieve_update_destroy_job"),
    path("<str:id>/update_category/", JobCategoryUpdateAPIView.as_view(), name="update_job_category"),

    #  Job invite routes
    path("job_invites/<str:id>/", JobInviteListCreateAPIView.as_view(), name="create_job_invite"),
    #  retrieve and destroy a job invite
    path("job_invites/<str:job_id>/<str:job_invite_id>/", JobInviteRetrieveDestroyAPIView.as_view(),
         name="retrieve_destroy_job_invite"),

    # Job Proposal routes
    path("proposals/<str:job_id>/", ProposalListAPIView.as_view(), name="list_proposals"),
    path("proposals/<str:job_id>/<str:proposal_id>/", ProposalRetrieveUpdateDestroyAPIView.as_view(),
         name="retrieve_update_destroy_proposal"),
    path("proposals/<str:job_id>/modify/", ModifyProposalAPIView.as_view(), name="modify_proposal"),

    # Contract routes
    path("contracts/job/<str:job_id>/", CreateContractAPIView.as_view(), name="create_contract"),
    path("contracts/customer/<str:customer_id>/", CustomerContractListAPIView.as_view(), name="customer_contract_list"),
    path("contracts/freelancer/<str:freelancer_id>/", FreelancerActiveContractsListAPIView.as_view(),
         name="freelancer_contract_list"),
    path("contracts/<str:id>/", ContractRetrieveAPIView.as_view(), name="retrieve_contract"),
    path("contracts/mark_completed/<str:id>/", MarkContractCompletedAPIView.as_view(), name="mark_contract_completed"),

    # job reviews
    path("reviews/given/<str:customer_id>/", GivenReviewListAPIView.as_view(), name="list_reviews_given"),
    path("reviews/received/<str:freelancer_id>/", ReceivedReviewListAPIView.as_view(), name="list_reviews_received"),
    path("reviews/<str:id>/", ReviewDetailAPIView.as_view(), name="review_detail"),

]
