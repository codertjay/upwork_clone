from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    RetrieveDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from categorys.models import Category
from jobs.models import Job, JobInvite
from jobs.serializers import CreateUpdateJobSerializers, RetrieveJobSerializer, UpdateJobCategorySerializer, \
    CreateJobInviteSerializer, RetrieveJobInviteSerializer, ListJobSerializers, CreateProposalSerializer, \
    RetrieveUpdateProposalSerializer, AcceptProposalSerializer
from subscriptions.permissions import CustomerMembershipPermission
from users.models import User
from users.permissions import LoggedInPermission


class JobListAPIView(ListAPIView):
    """List all jobs """
    permission_classes = [LoggedInPermission]
    serializer_class = ListJobSerializers
    filter_backends = [SearchFilter, OrderingFilter]
    queryset = Job.objects.all()
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


class CustomerJobListAPIView(ListAPIView):
    """List all jobs for a particular customer"""
    permission_classes = [LoggedInPermission]
    serializer_class = ListJobSerializers

    def get_queryset(self):
        #  this returns all the job the logged-in user has created
        #  get the project_stage that is passed in the params and I changed it to upper case
        project_stage = self.request.GET.get('project_stage', None)
        # get the id of the customer from the url
        customer_id = self.kwargs.get('customer_id')
        if not customer_id:
            # if the customer id does not exist I raise a 404 page
            raise Http404
        # filtering to get the customer
        customer = User.objects.filter(id=customer_id).first()
        if not customer:
            # if the customer  does not exist I raise a 404 page
            raise Http404
        #  check the project stage
        # only if the project stage was passed
        if project_stage:
            # changing the project_stage to upper case to enable exact filtering
            project_stage = project_stage.upper()
            if project_stage == "ACTIVE":
                #  the filtering was achieved through the related_names for job model to the customer
                return customer.job_customers.filter(project_stage=project_stage)
            elif project_stage == "PROCESSING":
                return customer.job_customers.filter(project_stage=project_stage)
            elif project_stage == "COMPLETED":
                return customer.job_customers.filter(project_stage=project_stage)
        #  if the IF statement wasn't given it returns all the jobs for that particular customer
        return customer.job_customers.all()


class JobCreateAPIView(CreateAPIView):
    """it uses the two permission_classes. the first checks the authentication headers
     and the second checks the customer"""
    permission_classes = [LoggedInPermission & CustomerMembershipPermission]
    serializer_class = CreateUpdateJobSerializers

    def post(self, request, *args, **kwargs):
        #  we use the kwarg to get the catalogue_id get the catalogue
        serializer = CreateUpdateJobSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user)
        return Response({"message successfully created Job "}, status=201)


class JobRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """this view is meant to retrieve the detail of a job , update a job and also delete a job """
    permission_classes = [LoggedInPermission]
    serializer_class = RetrieveJobSerializer
    lookup_field = "id"
    queryset = Job.objects.all()

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


class JobCategoryUpdateAPIView(APIView):
    """
    The update job category only takes in the freelancer id and also the job id is passed in the params
    and the action which is either ADD or RE
    """
    permission_classes = [LoggedInPermission]

    def put(self, request, *args, **kwargs):
        # job id passed from the urls
        job_id = self.kwargs.get("id")
        # returns the current user jobs which is not completed
        customer_job = self.request.user.job_customers.filter_active_and_processing_jobs().filter(id=job_id).first()
        if not customer_job:
            return Response({"error": "Job does not exist"}, status=404)
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
            if category not in customer_job.categorys.all():
                return Response({"message": "Category not in customer category"}, status=400)
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
        job = self.request.user.job_customers.filter_active_and_processing_jobs().filter(id=job_id).first()
        #  returns all the job invites
        return job.jobinvite_set.all()

    def post(self, request, *args, **kwargs):
        # the job id passed on the url params
        job_id = self.kwargs.get("id")
        # filtering only active and processing jobs
        job = self.request.user.job_customers.filter_active_and_processing_jobs().filter(id=job_id).first()
        if not job:
            return Response({"error": "Job doesnt exist with the id provided"}, status=404)
        #  check the customer if he has permission to delete a post
        if job.customer != self.request.user:
            return Response({"error": "You are not allowed to create an invite on this job post."}, status=400)
        #  check if the user has created up to 20 invites for a job
        if job.jobinvite_set.count() >= 20:
            return Response({"error": "You are not allowed to create job invite above 20"}, status=400)
        serializer = CreateJobInviteSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        freelancer_id = serializer.validated_data.get("freelancer_id")
        # check the freelancer id if he exists in the database and also the user must also be a freelancer
        freelancer = User.objects.filter(id=freelancer_id, user_type="FREELANCER").first()
        if not freelancer:
            return Response({"error": "Freelancer does not exist"}, status=400)
        # check if the freelancer id is not the logged-in user
        if self.request.user.id == freelancer_id:
            return Response({"message": "You cant invite your self to work on this job"}, status=400)
        #  to prevent creating invite on a job twice I use get or create
        job_invite, created = JobInvite.objects.get_or_create(customer=self.request.user, freelancer_id=freelancer_id,
                                                              job=job)

        return Response({"message": "Successfully create job Invite"}, status=201)


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


class ProposalListAPIView(ListCreateAPIView):
    """This view is meant to list all proposal of a job  and also create a proposal"""
    serializer_class = RetrieveUpdateProposalSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        #  the job id is passed on the urls, so  we get it from the kwargs
        job_id = self.kwargs.get("job_id")
        job = Job.objects.filter(id=job_id).first()
        if not job:
            #  if the job does not exist I raise  a http 404 page
            raise Http404
        #  returns all the proposal for that job post
        return job.proposal_set.all()

    def create(self, request, *args, **kwargs):
        job_id = self.kwargs.get("job_id")
        job = Job.objects.filter(id=job_id).first()
        if not job:
            #  if the job does not exist I return bad request
            return Response({"error": "Job with the ID on the URL does not exist"}, status=404)
        if self.request.user.user_type == "CUSTOMER":
            # customer are not allowed to make proposal
            return Response({"error": "Not allowed to create a  proposal.You must be a freelancer"})
        if job.customer == request.user:
            # preventing same user from making a proposal to his job even if he updates his user type
            return Response({"error": "Not allowed to make a proposal on your job"}, status=400)
        if job.proposal_set.filter(freelancer=self.request.user).exists():
            # if the user has already made a proposal then he is not allowed to propose on the job again
            return Response({"error": "Not allowed to make a proposal twice"}, status=400)
        # using the above serializer
        serializer = CreateProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(freelancer=self.request.user, proposal_stage="PROCESSING", job=job)
        return Response(serializer.data, status=201)


class ProposalRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """this enables deleting a proposal, editing the proposal and updating it
    the id of the job is passed on the url and also the proposal id
    """
    serializer_class = RetrieveUpdateProposalSerializer
    permission_classes = [LoggedInPermission]

    def get_object(self):
        #  I need to override the get_object and access the proposal using the ID's Passed
        job_id = self.kwargs.get("job_id")
        proposal_id = self.kwargs.get("proposal_id")
        job = Job.objects.filter(id=job_id).first()
        if not job:
            #  if the job does not exist i raise a http 404 page
            raise Http404
        #  using the job Id  to filter for the proposal url  and also using related_name to get the item
        proposal = job.proposal_set.filter(id=proposal_id).first()
        #  checking the proposal
        if not proposal:
            raise Http404
        return proposal

    def update(self, request, *args, **kwargs):
        #  override the default to enable us check if the freelancer updating this is then owner of the proposal
        instance = self.get_object()
        if instance.freelancer != request.user:
            return Response({"error": "You dont have permission to update this proposal"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        #  override the default and also check if the user is the owner of the proposal
        instance = self.get_object()
        if instance.freelancer != request.user:
            return Response({"error": "You dont have permission to update this proposal"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class AcceptProposalAPIView(APIView):
    """This view enables accepting a proposal on a job ,and it can only be accepted byt the customer
     who created the job
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = AcceptProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = self.kwargs.get("job_id")
        job = Job.objects.filter(id=job_id).first()
        if not job:
            return Response({"error": "Job not found"}, status=404)
        proposal_id = serializer.validated_data.get("proposal_id")
        job_proposal = job.proposal_set.filter(id=proposal_id)
        if not job_proposal:
            return Response({"error": "Job Proposal not found"}, status=404)
        if request.user != job.user:
            return Response({"error": "You dont have access"})

