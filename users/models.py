import random
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    """
    This is used to add extra queryset or add more functionality to the user models
    by creating helper functions
    """

    def verified_freelancers(self):
        """ This contains list of all verified freelancers"""
        return self.filter(verified=True, user_type="FREELANCERS")

    def verified_customers(self):
        """ This contains list of all verified customers"""
        return self.filter(verified=True, user_type="CUSTOMERS")

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


USER_TYPE_CHOICES = (
    ("CUSTOMER", "CUSTOMER"),
    ("FREELANCER", "FREELANCER")
)


class User(AbstractBaseUser, PermissionsMixin):
    """
     user models  inheriting from AbstractBaseUser to add extra fields
     and PermissionsMixin to add permission
    I actually added blank and null in some fields
    the username field is converted to use the email field
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # this tells django the username field because sometimes you can change it to email or username itself
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    date_joined = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    class Meta:
        ordering = ['-timestamp']

    def send_email_otp(self):
        """
        Send an otp to the user email
        """
        # importing send_otp_to_email locally to prevent issues when importing from both
        from users.tasks import send_otp_to_email_task
        try:
            otp = random.randint(1000, 9999)
            next_ten_minutes = timezone.now() + timedelta(minutes=10)
            #  set the cache to be deleted in 10 minutes from our cache system
            cache.set(f'{self.email}{otp}', next_ten_minutes, 605)
            print(otp)
            # the task which sends the mail using celery
            send_otp_to_email_task.delay(email=self.email, first_name=self.first_name, last_name=self.last_name,
                                         otp=otp)
            return True
        except Exception as e:
            print(e)
            return False

    def validate_email_otp(self, otp):
        """
        Validate OTP  passed
        """
        try:
            deadline_time = cache.get(f"{self.email}{otp}")
            if deadline_time is None:
                return False
            if deadline_time > timezone.now():
                return True
            return False
        except Exception as e:
            print(e)
            return False


class UserProfileManager(models.Manager):

    def verified_freelancers_profiles(self):
        return self.filter(user__user_type="FREELANCER", user__verified=True)

    def verified_customers_profiles(self):
        return self.filter(user__user_type="CUSTOMER", user__verified=True)


GENDER_CHOICES = (
    ("MALE", "MALE"),
    ("FEMALE", "FEMALE")
)


class UserProfile(models.Model):
    """
    The user profile is a model that is connected to the user and if the user model is deleted then
    the user profile will also be deleted
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(blank=True, null=True, upload_to="user_profile")
    address = models.CharField(max_length=250, blank=True, null=True)
    mobile = models.IntegerField(blank=True, null=True)
    business_name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = UserProfileManager()

    @property
    def profile_image_url(self):
        #  adding this function to prevent issues when accesing the profile image if it doesnt exist
        try:
            image = self.profile_image.url
        except:
            image = None
        return image


def post_save_create_user_profile(sender, instance, *args, **kwargs):
    """
    This creates a user profile once a user is being created
    :param instance:  the user created or updated
    """
    if instance:
        user_profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(post_save_create_user_profile, sender=User)
