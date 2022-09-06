from rest_framework import serializers

from categorys.models import Category
from categorys.serializers import CategorySerializer
from jobs.models import Job, JobInvite, Proposal
from users.serializers import UserSerializer


class CreateUpdateJobSerializers(serializers.ModelSerializer):
    """
    Used for updating, listing and creating a job by a customer
    """

    class Meta:
        model = Job
        fields = [
            "name",
            "description",
            "budget",
            "categorys",
            "location",
            "duration",
        ]

    def create(self, validated_data):
        # the categorys is in this form categorys=[1,2,3,4] which are the id's
        categorys = validated_data.pop('categorys')
        instance = Job.objects.create(**validated_data)
        for item in categorys:
            try:
                #  getting a category through the id passed . the reason why i am using try and except here is
                #  if the item does not exist django raise an error
                category = Category.objects.get(id=item)
                #  if the category exist then i add it to the item created
                if category:
                    instance.categorys.add(category)
            except Exception as a:
                print(a)
        return instance


class RetrieveJobSerializer(serializers.ModelSerializer):
    """
    The serializer to get the detail and all info of a job .
    """
    customer = UserSerializer
    categorys = CategorySerializer(many=True)
    job_invites_count = serializers.SerializerMethodField(read_only=True)
    accepted_job_invites_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        models = Job
        fields = [
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


class UpdateJobCategorySerializer(serializers.ModelSerializer):
    """This is used to add or remove a category from a job or add a category """
    action = serializers.ChoiceField(choices=CATEGORY_ACTION_CHOICES)
    category_id = serializers.IntegerField()


class CreateJobInviteSerializer(serializers.ModelSerializer):
    """this is meant for creating a job invite"""

    class Meta:
        model = JobInvite
        fields = [
            "freelancer_id",
        ]


class RetrieveJobInviteSerializer(serializers.ModelSerializer):
    """ this is meant to get all detail of the job invites and it used on the job invite retrieve api """
    customer = UserSerializer(read_only=True)
    freelancer = UserSerializer(read_only=True)

    class Meta:
        model = JobInvite
        fields = [
            "customer",
            "freelancer",
            "job",
            "accepted",
            "timestamp",
        ]


class CreateJobProposalSerializer(serializers.ModelSerializer):
    """this is meant for creating a job proposal """

    class Meta:
        model = Proposal
        fields = [
            "amount",
            "content",
        ]
