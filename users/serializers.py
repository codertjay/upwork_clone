from allauth.account.adapter import get_adapter
from users.models import User
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken


# used when signing up with the url
class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration for the instasew user serializer
    this adds extra fields to the django default RegisterSerializer

    """

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    # the password
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'user_type',
            'password',
            'confirm_password',
        )

    def get_cleaned_data(self):
        """
        the default RegisterSerializer uses password1 and password2
        so  just get the data from password and  confirm_password and add it to the field for verification
        """
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'user_type': self.validated_data.get('user_type', ''),
            'password1': self.validated_data.get('password', ''),
            'password2': self.validated_data.get('confirm_password', ''),
        }

    def save(self, request):
        """
        Due to adding extra fields to the user model we created an adapter
        in the users app to save the  user extra field
        """
        # using the custom adapter I created on the adapters.py in the users app
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        return user


class TokenSerializer(serializers.ModelSerializer):
    """
    In here I am checking if the user email has been verified before
    sending him his details
    """
    user = SerializerMethodField(read_only=True)
    access = SerializerMethodField(read_only=True)
    refresh = SerializerMethodField(read_only=True)

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
            it uses the custom serializer i created for authentication only
            """
            return UserSerializer(obj.user, read_only=True).data
        except Exception as a:
            # just for debugging purposes
            print('====================', a)
            return 'error'


# This serializer is used only when users login or register to get information
class UserSerializer(serializers.ModelSerializer):
    """
    This returns more detail about a user, and it is only used when the user
    logs in or register
    """

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'user_type',
        ]
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 4}, 'otp': {'write_only': True}}
