from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from categorys.serializers import CategorySerializer
from jobs.models import Job, JobInvite, Proposal, Contract, PROPOSAL_STAGE_CHOICES, Review
from users.serializers import UserDetailSerializer, UserSerializer


class ListJobSerializers(serializers.ModelSerializer):
    """
    Used for listing jobs
    """
    categorys = CategorySerializer(many=True, read_only=True)
    customer = UserDetailSerializer(read_only=True)
    job_invites_count = serializers.SerializerMethodField(read_only=True)
    accepted_job_invites_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "name",
            "description",
            "budget",
            "location",
            "duration",
            "timestamp",
            "job_invites_count",
            "accepted_job_invites_count",
            "categorys",
            "customer",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_job_invites_count(self, obj):
        #  this returns the job invites count
        return obj.job_invites_count()

    def get_accepted_job_invites_count(self, obj):
        #  this returns the job invites count
        return obj.accepted_job_invites_count()


class CreateUpdateJobSerializers(serializers.ModelSerializer):
    """
    Used for updating and creating a job by a customer
    """

    class Meta:
        model = Job
        fields = [
            "id",
            "name",
            "description",
            "budget",
            "categorys",
            "location",
            "duration",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        # the categorys is in this form categorys=[<category instance>, ...] which are the instances of a category
        categorys = validated_data.pop('categorys')
        instance = Job.objects.create(**validated_data)
        for item in categorys:
            try:
                instance.categorys.add(item)
            except Exception as a:
                print(a)
        return instance


class RetrieveJobSerializer(serializers.ModelSerializer):
    """
    The serializer to get the detail and all info of a job .
    """
    customer = UserDetailSerializer(read_only=True)
    categorys = CategorySerializer(many=True)
    job_invites_count = serializers.SerializerMethodField(read_only=True)
    accepted_job_invites_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "customer",
            "name",
            "description",
            "budget",
            "location",
            "project_stage",
            "duration",
            "job_invites_count",
            "accepted_job_invites_count",
            "timestamp",
            "categorys",
        ]

    def get_job_invites_count(self, obj):
        #  this returns the job invites count
        return obj.job_invites_count()

    def get_accepted_job_invites_count(self, obj):
        #  this returns the job invites count
        return obj.accepted_job_invites_count()


CATEGORY_ACTION_CHOICES = (
    ("ADD", "ADD"),
    ("REMOVE", "REMOVE"),
)


class UpdateJobCategorySerializer(serializers.Serializer):
    """This is used to add or remove a category from a job or add a category """
    action = serializers.ChoiceField(choices=CATEGORY_ACTION_CHOICES)
    category_id = serializers.CharField()


class CreateJobInviteSerializer(serializers.Serializer):
    """this is meant for creating a job invite"""
    freelancer_id = serializers.CharField()


class RetrieveJobInviteSerializer(serializers.ModelSerializer):
    """ this is meant to get all detail of the job invites and it used on the job invite retrieve api """
    customer = UserDetailSerializer(read_only=True)
    freelancer = UserDetailSerializer(read_only=True)

    class Meta:
        model = JobInvite
        fields = [
            "customer",
            "freelancer",
            "job_id",
            "accepted",
            "timestamp",
        ]


class RetrieveUpdateProposalSerializer(serializers.ModelSerializer):
    """This url is meant to list all proposals and also retrieve them"""
    freelancer = UserDetailSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "freelancer",
            "job_id",
            "proposal_stage",
            "amount",
            "content",
            "timestamp",
        ]
        read_only_fields = ["job_id", "id", "freelancer"]


class CreateProposalSerializer(serializers.ModelSerializer):
    """this is meant for creating a job proposal """

    class Meta:
        model = Proposal
        fields = [
            "amount",
            "content",
        ]


class ModifyProposalSerializer(serializers.Serializer):
    """
    this serializer is used for accepting a proposal  it requires the proposal  id
    """
    proposal_id = serializers.CharField()
    #  the action to modify a proposal
    action = serializers.ChoiceField(choices=PROPOSAL_STAGE_CHOICES)


class CreateContractSerializer(serializers.Serializer):
    """
    this serializer is used to creating contract on a job post
    """
    proposal_id = serializers.CharField(max_length=250)
    amount = serializers.DecimalField(max_digits=1000, decimal_places=2)
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate_start_date(self, obj):
        #  this is just to prevent the user from using past date to create this
        current_date = timezone.now().date() - timedelta(days=0)
        if current_date > obj:
            raise serializers.ValidationError("Current date cant be greater than start date")
        return obj

    def validate_end_date(self, obj):
        #  this is just to prevent the user from using past date to create this
        current_date = timezone.now().date() - timedelta(days=0)
        if current_date > obj:
            raise serializers.ValidationError("Current date cant be greater than end date")
        return obj


class ReviewCreateSerializer(serializers.Serializer):
    """
    This takes in the job id and also the proposal id we would like to write a review on
    """
    proposal_id = serializers.CharField()
    job_id = serializers.CharField()
    stars = serializers.IntegerField(max_value=5, min_value=1)
    description = serializers.CharField()


class ReviewSerializer(serializers.ModelSerializer):
    """
    This serializer is meant for listing review and also getting the detail of the review
    """
    freelancer = UserSerializer(read_only=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "job_id",
            "freelancer",
            "customer",
            "stars",
            "description",
            "timestamp",
        ]


class ContractSerializer(serializers.ModelSerializer):
    """
    This is used to list all contract  and also the detail of a contract .
    """
    freelancer = UserSerializer(read_only=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            "customer",
            "freelancer",
            "job_id",
            "amount",
            "completed",
            "start_date",
            "end_date",
            "timestamp",
        ]

