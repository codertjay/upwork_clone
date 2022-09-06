from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from categorys.models import Category
from jobs.serializers import CreateUpdateJobSerializers, RetrieveJobSerializer, UpdateJobCategorySerializer, \
    CreateJobInviteSerializer, RetrieveJobInviteSerializer
from subscriptions.permissions import CustomerMembershipPermission
from users.permissions import LoggedInPermission


class ListJobAPIView(ListAPIView):
    """List all jobs """
    permission_classes = [LoggedInPermission]
    serializer_class = CreateUpdateJobSerializers
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "description",
        "budget",
        "categorys",
        "location",
        "project_stage",
        "duration",
    ]

    def get_queryset(self):
        """this is getting the filtered queryset from search filter
                 then adding more filtering   """
        queryset = self.filter_queryset(self.queryset.all())
        # FIXME: ASK QUESTION ON HOW THE QUERY WILL LOOK LIKE

        return queryset


class ListCustomerJobAPIView(ListAPIView):
    """List all jobs for a particular customer"""
    permission_classes = [LoggedInPermission]
    serializer_class = CreateUpdateJobSerializers

    def get_queryset(self):
        #  this returns all the job the logged-in user has created
        #  get the project_stage that is passed in the params and I changed it to upper case
        project_stage = self.request.GET.get('project_stage').upper()
        #  check the project stage
        if project_stage == "ACTIVE":
            return self.request.user.job_customers.filter(project_stage=project_stage)
        elif project_stage == "PROCESSING":
            return self.request.user.job_customers.filter(project_stage=project_stage)
        elif project_stage == "COMPLETED":
            return self.request.user.job_customers.filter(project_stage=project_stage)
        #  if the IF statement wasn't given it returns all the jobs for that particular customer
        return self.request.user.job_customers.all()


class CreateJobAPIView(ListCreateAPIView):
    """it uses the two permission_classes. the first checks the authentication headers
     and the second checks the customer"""
    permission_classes = [LoggedInPermission & CustomerMembershipPermission]
    serializer_class = CreateUpdateJobSerializers

    def get_queryset(self):
        #  this returns all the job the logged-in user has created
        return self.request.user.job_customers.all()

    def post(self, request, *args, **kwargs):
        #  we use the kwarg to get the catalogue_id get the catalogue
        serializer = CreateUpdateJobSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user)
        return Response({"message successfully created Job "}, status=201)


class RetrieveUpdateDestroyJobAPIView(RetrieveUpdateDestroyAPIView):
    """this view is meant to retrieve the detail of a job , update a job and also delete a job """
    permission_classes = [LoggedInPermission]
    serializer_class = RetrieveJobSerializer
    lookup_field = "id"

    def get_queryset(self):
        #  this returns all the job the logged-in user has created
        return self.request.user.job_customers.all()

    def retrieve(self, request, *args, **kwargs):
        """override the retrieve function to use our custom serializer"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # instance we are updating
        instance = self.get_object()
        #  check the customer if he has permission to update a post
        if instance.customer != request.user:
            return Response({"error": "You are not allowed to update the job "}, status=400)
        # updating the job and also the partial is to prevent required fields
        serializer = CreateUpdateJobSerializers(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  check the customer if he has permission to delete a post
        if instance.customer != request.user:
            return Response({"error": "You are not allowed to delete this job "}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class UpdateJobCategoryAPIView(APIView):
    """
    The update job category only takes in the freelancer id and also the job id is passed in the params
    and the action which is either ADD or RE
    """
    permission_classes = [LoggedInPermission]

    def put(self):
        # job id passed from the urls
        job_id = self.kwargs.get("id")
        # returns the current user jobs which is not completed
        customer_job = self.request.user.job_customers.filter_active_and_processing_jobs().filter(id=job_id).first()
        if not customer_job:
            return Response({"message": "Job does not exist"}, status=404)
        #  check the customer if he has permission to delete a post
        if customer_job.customer != self.request.user:
            return Response({"error": "You are not allowed to update this job category"}, status=400)
        serializer = UpdateJobCategorySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        category_id = serializer.data["category_id"]
        action = serializer.data["action"]
        #  filtering if the category exists
        category = Category.objects.filter(id=category_id).first()
        if not category:
            return Response({"message": "Category does not exist"}, status=404)
        if action == "ADD":
            customer_job.categorys.add(category)
            customer_job.save()
        elif action == "REMOVE":
            customer_job.categorys.remove(category)
            customer_job.save()
        return Response({"message": "Successfully updated job category"}, status=200)


class JobInviteListCreateAPIView(ListCreateAPIView):
    """
    This view is used to create a job invite of a particular job, and also it requires the
     freelancer id to be passed, and also
     It list the job invites associated to a job post
    """
    permission_classes = [LoggedInPermission]
    serializer_class = RetrieveJobInviteSerializer

    def get_queryset(self):
        # the job id passed on the url params
        job_id = self.kwargs.get("id")
        # filtering only active and processing jobs
        job = self.request.user.job_customers.filter_active_and_processing_jobs.filter(id=job_id).first()
        #  returns all the job invites
        return job.jobinvite_set.all()

    def post(self, request, *args, **kwargs):
        # the job id passed on the url params
        job_id = self.kwargs.get("id")
        # filtering only active and processing jobs
        job = self.request.user.job_customers.filter_active_and_processing_jobs.filter(id=job_id).first()
        if not job:
            return Response({"message": "Job doesnt exist with the id provided"}, status=404)
        #  check the customer if he has permission to delete a post
        if job.customer != self.request.user:
            return Response({"error": "You are not allowed to create an invite on this job post."}, status=400)
        #  check if the user has created up to 20 invites for a job
        if job.jobinvite_set.count() >= 20:
            return Response({"error": "You are not allowed to create job invite above 20"}, status=400)
        serializer = CreateJobInviteSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        freelancer_id = serializer.data.get("freelancer_id")
        # check if the freelancer id is not the logged-in user
        if self.request.user.id == freelancer_id:
            return Response({"message": "You cant invite your self to work on this job"}, status=400)
        serializer.save(customer=self.request.user)
        return Response({"message": "Successfully create job"}, status=201)


class JobInviteRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    """
    This view is meant to delete or retrieve a job post
    """
    permission_classes = [LoggedInPermission]
    serializer_class = RetrieveJobInviteSerializer

    def get_object(self):
        """currently overriding the default get object
        Using the Job_id and the job_invite_id passed on the params to get the job invite instance
        """
        job_id = self.kwargs.get("job_id")
        job_invite_id = self.kwargs.get("job_invite_id")
        #  filter the user jobs if he has that job with the id passed
        job = self.request.user.job_customers.filter(id=job_id).first()
        if not job:
            #  if the job does not exist I raise a 404 error
            raise Http404
        #  filtering the job invite
        job_invite = job.jobinvite_set.filter(id=job_invite_id).first()
        if not job_invite:
            #  if the job_invite does not exist I raise a 404 error
            raise Http404
        return job_invite

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  check if the current user is the owner of the job invite
        if instance.customer != request.user:
            return Response({"error": "You dont have permission to update this job invite"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


