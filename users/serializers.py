from allauth.account.adapter import get_adapter
from users.models import User, UserProfile
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from users.models import USER_TYPE_CHOICES
from users.tasks import login_notification_email


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration for the instasew user serializer
    this adds extra fields to the django default RegisterSerializer
    """

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES)
    # the password
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'user_type',
            'password1',
            'password2',
        )

    def get_cleaned_data(self):
        """
        the default RegisterSerializer uses password1 and password2
        so  just get the data from password and  confirm_password and add it to the field for verification
        and also this enables us to pass extra data
        """
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'user_type': self.validated_data.get('user_type', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }

    def save(self, request):
        """
        Due to adding extra fields to the user model we created an adapter
        in the users app to save the  user extra field
        """
        # using the custom adapter I created on the adapters.py in the users app
        adapter = get_adapter()
        user = adapter.new_user(request)
        # if the user is not passed i tend to save it as customer
        user.user_type = self.validated_data.get('user_type', 'CUSTOMER')
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        return user


class TokenSerializer(serializers.ModelSerializer):
    """
    In here I am checking if the user email has been verified before
    sending him his details
    """
    user = serializers.SerializerMethodField(read_only=True)
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Token
        fields = ('access', 'refresh', 'user',)

    def get_access(self, obj):
        """
        This access token is a jwt token that get expired after a particular time given which could either be 1 hour
        """
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh.access_token)

    def get_refresh(self, obj):
        """
        The refresh token gotten from  rest_framework_simplejwt.tokens
        :param obj: instance
        """
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh)

    def get_user(self, obj):
        try:
            """
            it uses the custom serializer i created for authentication only so i just need this 
            serializer method field to pass extra datas
            """
            if obj.user.verified:
                #  send a mail to the user once he is authenticated to prevent issues if he isnt he owner of an accout
                #  using celery task to make it faster
                login_notification_email.delay(
                    obj.user.first_name, obj.user.email)
            return UserSerializer(obj.user, read_only=True).data
        except Exception as a:
            # just for debugging purposes
            print('====================', a)
            return 'error'


# This serializer is used only when users login or register to get information
class UserSerializer(serializers.ModelSerializer):
    """
    This returns more detail about a user, and it is only used when the user
    logs in or register, and also in other serializers as user,freelancer and customer
    """

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'verified',
            'user_type',
        ]
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 4}}


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to update a user which exists
    """
    first_name = serializers.CharField(max_length=250, required=False, allow_blank=False)
    last_name = serializers.CharField(max_length=250, required=False, allow_blank=False)
    email = serializers.EmailField(required=False, allow_blank=False)
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES, allow_blank=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'user_type',
        ]

    def validate_email(self, obj):
        """This checks if the email has been used before and if it already exists by another user it raises an error
        and also the request is passed from the view to access the current user
        """
        logged_in_user = self.context['request'].user
        user = User.objects.filter(email=obj).first()
        if user:
            if logged_in_user.email != user.email:
                raise serializers.ValidationError(
                    'Please use a valid email that has not been used before')
        return obj


class VerifyEmailSerializer(serializers.Serializer):
    """
    This is used to verify the email address with otp of a user
    """
    otp = serializers.CharField(max_length=4)
    email = serializers.EmailField()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Used for updating a user profile
    """

    class Meta:
        model = UserProfile
        fields = [
            "gender",
            "date_of_birth",
            "profile_image",
            "address",
            "mobile",
            "business_name",
            "description",
            "nationality",
            "country",
            "city",
        ]


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Used to returning more details of a user profile , and also with the image of the
    profile image we are also able to return that
    """
    user = UserSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "gender",
            "date_of_birth",
            "profile_image",
            "address",
            "mobile",
            "business_name",
            "description",
            "nationality",
            "country",
            "city",
        ]

    def get_profile_image(self, obj):
        return obj.profile_image_url
