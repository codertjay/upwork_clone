from rest_framework import serializers

from categorys.serializers import CategorySerializer
from jobs.models import Job, JobInvite, Proposal
from users.serializers import UserSerializer


class ListJobSerializers(serializers.ModelSerializer):
    """
    Used for listing jobs
    """
    categorys = CategorySerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
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
            "job_invites_count",
            "accepted_job_invites_count",
            "categorys",
            "customer",
        ]
        read_only_fields = ["id"]

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
    customer = UserSerializer(read_only=True)
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
    category_id = serializers.IntegerField()


class CreateJobInviteSerializer(serializers.Serializer):
    """this is meant for creating a job invite"""
    freelancer_id = serializers.IntegerField()


class RetrieveJobInviteSerializer(serializers.ModelSerializer):
    """ this is meant to get all detail of the job invites and it used on the job invite retrieve api """
    customer = UserSerializer(read_only=True)
    freelancer = UserSerializer(read_only=True)

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
    freelancer = UserSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = [
            "freelancer",
            "job_id",
            "proposal_stage",
            "amount",
            "content",
            "timestamp",
        ]
        read_only_fields = ["job_id", "freelancer"]


class CreateProposalSerializer(serializers.ModelSerializer):
    """this is meant for creating a job proposal """

    class Meta:
        model = Proposal
        fields = [
            "amount",
            "content",
        ]
