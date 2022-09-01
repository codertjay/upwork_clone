from django.db import models

from categorys.models import Category
from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL

#  the project stage choice is used to check the status of the job
PROJECT_STAGE_CHOICES = (
    ("ACTIVE", "ACTIVE"),
    ("PROCESSING", "PROCESSING"),
    ("COMPLETED", "COMPLETED"),
)


class Job(models.Model):
    """
    The job models enables a customer to create job for freelancer
    and gives customer with in that location more access to bid
    project_stage: by default it is active when the job is created
    then changes to processing when a freelancer has been picked
    then changes to completed when the freelancer has completed the job
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    budget = models.FloatField()
    categorys = models.ManyToManyField(Category)
    location = models.CharField(max_length=250)
    project_stage = models.CharField(max_length=250, default="ACTIVE", choices=PROJECT_STAGE_CHOICES)
    # duration is measured  in days
    duration = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)


class JobInvite(models.Model):
    """
    The job invite enables the customer to send an invitation to  freelancers
    but i made sure if a job is deleted then the invite get deleted
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_customer")
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_freelancer")
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


PROPOSAL_STAGE_CHOICES = (
    ("PROCESSING", "PROCESSING"),
    ("INTERVIEWING", "INTERVIEWING"),
    ("ACCEPTED", "ACCEPTED"),
)


class Proposal(models.Model):
    """
    The proposal enables a freelancer to bid for a job which is still active only
    the proposal has three stages
    which are:
    - Processing : this is the default stage when it is being created
    - Interviewing : this stage is when the customer has chat the freelancer base on the proposal
    _ Accepted: this is when the customer has accepted the proposal

    The job id:
    The job id would also be used to get the list of jobs the user has applied to once looping
    through the user proposals
    """
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="proposal_freelancer")
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    proposal_stage = models.CharField(max_length=50, choices=PROPOSAL_STAGE_CHOICES)
    amount = models.FloatField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    """
    The review is related to a job which is still completed only
    a job must have only one review for the freelancer

    """
    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="freelancer")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    # the max number would be 5 and min number is 0
    stars = models.IntegerField(default=0)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class SavedJob(models.Model):
    """
    The saved  jobs provide list of jobs the user has saves in which he or she would like to apply to
    another time
    """
    freelancer = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_jobs = models.ManyToManyField(Job, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
