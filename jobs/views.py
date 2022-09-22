import uuid

from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    RetrieveDestroyAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from categorys.models import Category
from jobs.models import Job, JobInvite, Contract, Review
from jobs.serializers import CreateUpdateJobSerializers, RetrieveJobSerializer, UpdateJobCategorySerializer, \
    CreateJobInviteSerializer, RetrieveJobInviteSerializer, ListJobSerializers, CreateProposalSerializer, \
    RetrieveUpdateProposalSerializer, ModifyProposalSerializer, CreateContractSerializer, ReviewCreateSerializer, \
    ReviewSerializer, ContractSerializer
from subscriptions.permissions import CustomerMembershipPermission
from transactions.models import Transaction
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


class GivenReviewListAPIView(ListAPIView):
    """List all reviews given by this user"""
    permission_classes = [LoggedInPermission]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        #  get the reviews given by this customer
        review = Review.objects.filter(customer_id=self.kwargs.get("customer_id"))
        #  if the review does not exist i raise a 404
        if not review:
            raise Http404
        return review


class ReceivedReviewListAPIView(ListAPIView):
    """List all reviews received by this user"""
    permission_classes = [LoggedInPermission]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        #  get the reviews given by this freelancer
        review = Review.objects.filter(freelancer_id=self.kwargs.get("freelancer_id"))
        #  if the review does not exist I raise a 404
        if not review:
            raise Http404
        return review


class ReviewDetailAPIView(RetrieveAPIView):
    """Retrieve information about a review """
    permission_classes = [LoggedInPermission]
    serializer_class = RetrieveJobSerializer
    lookup_field = "id"


class ModifyProposalAPIView(APIView):
    """This view enables accepting a proposal on a job ,and it can only be accepted by the customer
     who created the job and also once the job is accepted the payment for the will be moved to the
         instasaw account"""
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        # serializer which is used to get the freelancer is
        serializer = ModifyProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = self.kwargs.get("job_id")
        job = Job.objects.filter(id=job_id).first()
        if not job:
            return Response({"error": "Job not found"}, status=404)
        proposal_id = serializer.validated_data.get("proposal_id")
        action = serializer.validated_data.get("action")
        # check the job user
        if request.user != job.customer:
            return Response({"error": "You dont have access"})
        #  check job proposal of the freelancer exists
        job_proposal = job.proposal_set.filter(id=proposal_id).first()
        if not job_proposal:
            return Response({"error": "Job Proposal not found"}, status=404)
        #  before updating a proposal check if a contract for that proposal exists
        contract = Contract.objects.filter(freelancer=job_proposal.freelancer, job=job).first()
        if contract:
            return Response({"error": "You cant modify a proposal that already have a contract"})
        #  I know you might be thinking we can accept multiple user proposal .
        #  yes we can, but we can only create one contract for the job
        #  which deals with the money and everything so that prevent issues
        job_proposal.proposal_stage = action
        job_proposal.save()
        return Response({"message": f"Successfully Modified proposal to {action}"}, status=200)


class CreateContractAPIView(APIView):
    """
    This is the stage where the customer accept the user proposal and
     if he/she hasn't then we automatically accept the proposal
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        # create contract base on the data provided
        serializer = CreateContractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = self.kwargs.get("job_id")
        proposal_id = serializer.validated_data.get("proposal_id")
        amount = serializer.validated_data.get("amount")
        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")
        # customer wallet
        customer_wallet = request.user.wallet
        # check if the customer has up to the amount
        if not customer_wallet.can_withdraw(amount):
            return Response({"error": "You dont have up to this amount in your wallet"}, status=400)
        #  check the job if it exists
        job = Job.objects.filter(id=job_id, customer=self.request.user).first()
        if not job:
            return Response({"error": "Job does not exist"}, status=400)
        #  get the freelancer id
        proposal = job.proposal_set.filter(id=proposal_id).first()
        if not proposal:
            return Response({"error": "Proposal does not exist"}, status=400)
        #   get the id of the freelancer
        freelancer_id = proposal.freelancer.id
        #  check if the freelance exist
        freelancer = User.objects.filter(id=freelancer_id, user_type="FREELANCER").first()
        if not freelancer:
            return Response({"error": "Freelancer does not exist"}, status=400)

        # check the freelancer proposal
        freelancer_proposal = job.proposal_set.filter(freelancer=freelancer).first()
        if not freelancer_proposal:
            return Response(
                {"error": "This freelancer hasn't made a proposal yet . please him/her to"}, status=400)
        # Remove the money from the user balance
        # check if a contract already exist
        if Contract.objects.filter(job=job).exists():
            return Response({"error": "This job already have a contract"}, status=400)
        # before withdrawing i need to get the user previous balance
        previous_balance = customer_wallet.balance
        #  remove the money from the customer wallet for the project
        if not customer_wallet.withdraw_balance(amount):
            return Response({"error": "Error occurred"}, status=400)
        #  the contract
        contract = Contract.objects.create(
            customer=self.request.user,
            job=job,
            freelancer=freelancer,
            amount=amount,
            start_date=start_date,
            end_date=end_date,
        )
        #  once the contract has been created  we need to do three things which are
        #  Accept the proposal if it is not
        freelancer_proposal.proposal_stage = "ACCEPTED"
        freelancer_proposal.save()
        #  Create a transaction for the customer
        transaction = Transaction.objects.create(
            user=self.request.user,
            transaction_id=uuid.uuid4().hex,
            amount=amount,
            transaction_stage="SUCCESSFUL",
            transaction_type="DEBIT",
            transaction_category="WITHDRAWAL",
            previous_balance=previous_balance,
            current_balance=customer_wallet.balance
        )
        #  Make the job_stage PROCESSING
        job.project_stage = "PROCESSING"
        job.save()
        return Response({"message": "Contract successfully created"}, status=201)


class JobReviewCreateAPIView(APIView):
    """
    This class create review for a job post proposal once done
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data.get("job_id")
        proposal_id = serializer.validated_data.get("proposal_id")
        stars = serializer.validated_data.get("stars")
        description = serializer.validated_data.get("description")
        # check the job if its exists
        job = Job.objects.filter(id=job_id).first()
        if not job:
            return Response({"error": "Job does not exist"}, status=400)
        # check the proposal once the job exists
        proposal = job.proposal_set.filter(id=proposal_id).first()
        if not proposal:
            return Response({"error": "Proposal does not exist"}, status=400)
        # check if a contract was created and the contract is completed
        contract = Contract.objects.filter(job=job, freelancer=proposal.freelancer).first()
        if not contract:
            return Response({"error": "Contract does not exist. which means this job wasn't done"}, status=400)
        # check if review already exists
        review = Review.objects.filter(job=job, freelancer=proposal.freelancer).first()
        if review:
            return Response({"error": "Review already exists"}, status=200)
        # create the review
        Review.objects.create(
            job=job,
            freelancer=proposal.freelancer,
            customer=job.customer,
            stars=stars,
            description=description,
        )
        return Response({"message": "Review was successfully created"}, status=201)


class FreelancerActiveContractsListAPIView(ListAPIView):
    """
    This is used list all active contract made by a customer for a freelancer
    """
    permission_classes = [LoggedInPermission]
    serializer_class = ContractSerializer

    def get_queryset(self):
        freelancer_id = self.kwargs.get("freelancer_id")
        # it only shows the contract if it is not completed
        contracts = Contract.objects.filter(freelancer_id=freelancer_id, completed=False)
        if not contracts.exists():
            raise Http404
        return contracts


class CustomerContractListAPIView(ListAPIView):
    """
    This I used to list the contracts created by a customer
    """
    permission_classes = [LoggedInPermission]
    serializer_class = ContractSerializer

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_id")
        #  only shows contracts that are not completed
        contracts = Contract.objects.filter(customer_id=customer_id, completed=False)
        if not contracts.exists():
            raise Http404
        return contracts


class ContractRetrieveAPIView(RetrieveAPIView):
    """this is used to get the detail of a contract"""
    permission_classes = [LoggedInPermission]
    serializer_class = ContractSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Contract.objects.all()


class MarkContractCompletedAPIView(APIView):
    """
    This is used to mark a contract completed and also fund the customer wallet  who finished the contract,create a
     transaction for the freelancer and also changed the job  project_stage to completed
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        # get the contract id from the url
        contract_id = self.kwargs.get("id")
        #  check if the contract exist and also the customer must be the logged-in user .
        #  because he was the once who created the contract
        contract = Contract.objects.filter(id=contract_id).first()
        if not contract:
            return Response({"error": "Contract does not exist"}, status=400)
        # we need to check also who is accessing .
        # and note the customer must be the once who owns the contract or the user must be a staff user
        if contract.customer != request.user or request.user.is_staff == False:
            return Response({"error": "You dont have access to update this contract"})
        # create a transaction for the freelancer who would
        freelancer_wallet = request.user.wallet
        #  we need to get the freelancer previous balance before updating his wallet
        freelancer_previous_balance = freelancer_wallet.balance
        #  Fund the freelancer wallet
        if contract.completed:
            return Response({"error": "Contract has already being completed"}, status=400)
        if not freelancer_wallet.fund_balance(contract.amount):
            # Create a transaction for the freelancer if failed
            transaction = Transaction.objects.create(
                previous_balance=freelancer_previous_balance,
                current_balance=freelancer_wallet.balance,
                user=contract.freelancer,
                transaction_id=uuid.uuid4().hex,
                transaction_category="AMOUNT FUNDING",
                transaction_type="CREDIT",
                transaction_stage="FAILED",
                amount=contract.amount,
            )
            return Response({"error": "Error Funding freelancer wallet"}, status=400)
        # After funding the balance we need to mark the contract as completed
        contract.completed = True
        contract.save()

        # Create a transaction for the freelancer if successful
        transaction = Transaction.objects.create(
            previous_balance=freelancer_previous_balance,
            current_balance=freelancer_wallet.balance,
            user=contract.freelancer,
            transaction_id=uuid.uuid4().hex,
            transaction_category="AMOUNT FUNDING",
            transaction_type="CREDIT",
            transaction_stage="SUCCESSFUL",
            amount=contract.amount,
        )
        #  Update the job as completed
        job = contract.job
        job.project_stage = "COMPLETED"
        job.save()
        return Response({"message": "Successfully marked contract as completed"}, status=200)
