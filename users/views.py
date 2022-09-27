from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, UserProfile
from users.permissions import NotLoggedInPermission, LoggedInPermission
from users.serializers import VerifyEmailSerializer, UserProfileUpdateSerializer, UserProfileDetailSerializer, \
    UserDetailSerializer, UserUpdateSerializer, TokenSerializer


class InstasawLoginAPIView(LoginView):
    """
    Login view which contains throttle and can be access three times in a minute
    """
    throttle_scope = 'authentication'
    permission_classes = [NotLoggedInPermission]

    def post(self, request, *args, **kwargs):
        """
        :param args: 
        :param kwargs: 
        :return: it returns response using TokenSerializer serializer it checks if the user is not verified and
        if the user
        is not then it uses the default response from the  TokenSerializer
        """
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        self.login()
        # login the user to access him/ her on the request
        #  overriding the login of allauth to add this if user is not verified
        if not request.user.verified:
            # fixme :add verify mail send otp
            return Response({"message": "Please verify your email address."},
                            status=400)
        return self.get_response()


class InstasawRegisterAPIView(RegisterView):
    """
    Register view which contains throttle and can be access three times in a minute
    """
    throttle_scope = 'authentication'
    permission_classes = [NotLoggedInPermission]

    def create(self, request, *args, **kwargs):
        #  using the default serializer which was set
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #  create a user
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        #  means the user was created if the data exist, but we need to
        #  check if the user is verified
        if data:
            if not user.verified:
                #  I am sending 400 status to enable the frontend know the user is not verified
                response = Response(
                    {"message": "Please verify your email address."},
                    status=201,
                    headers=headers,
                )
            else:
                response = Response(
                    data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        return response


class RequestEmailOTPAPIView(APIView):
    """ This is used to request otp via email and if requested via email then we must verify via email
     with this function VerifyEmailAddressAPIView"""
    permission_classes = [NotLoggedInPermission]
    throttle_scope = 'monitor'

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            #  sends an otp to the user email
            if user.send_email_otp():
                return Response({'message': 'Successfully sent OTP'}, status=200)
        elif not user:
            return Response({'message': 'Please make sure you send the right mail address '}, status=404)
        return Response({'message': 'There was an error performing your request please try again later '}, status=400)


class VerifyEmailOTPAPIView(APIView):
    """
    This is used to verify an email using the otp passed and also it uses cache which was set to expire after 10 min
    """
    permission_classes = [NotLoggedInPermission]
    throttle_scope = 'monitor'

    def post(self, request):
        try:
            serializer = VerifyEmailSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.data.get('email')
            otp = serializer.data.get('otp')
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'error': 'Please pass in the correct data'}, status=400)
            if user.validate_email_otp(otp):
                user.verified = True
                user.save()
                return Response({'message': 'Successfully verify your mail'}, status=200)
            return Response({'error': 'Email Not Verified .Time exceeded or OTP is invalid'}, status=400)
        except Exception as a:
            print("error-----", a)
            return Response({'error': 'There was an error performing your request.Email Not Verified'}, status=400)


class UserUpdateAPIView(APIView):
    """
    This view is responsible for updating a user  models in which if he wants to switch profile
     to being a freelancer or the other
    """
    permission_classes = [LoggedInPermission]

    def put(self, request):
        """
        Update a user which already exit
         and also I am passing context={'request': request} on the UserProfileUpdateSerializer to enable access of other
        params on other serializer during verification
        """
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, context={'request': request})
        #  check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Successfully updated user', 'data': UserDetailSerializer(request.user).data}, status=200)


class UserProfileUpdateAPIView(APIView):
    """
    User update api view enables you to update the user api
    """
    permission_classes = [LoggedInPermission]

    def put(self, request):
        """Update a user profile base on the data passed also we used related name to access
        the user profile

        """
        serializer = UserProfileUpdateSerializer(instance=self.request.user.user_profile, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=200,
            data={"message": "successfully updated user profile",
                  "data": UserProfileDetailSerializer(request.user.user_profile).data
                  })


class FreelancerListAPIView(ListAPIView):
    """
    This view returns list of all the freelancers, and it also has some filtering base
     on location and other fields like city

    using a filter backend for the filtering of the user and also the ordering filter
    SearchFilter : used for query
    OrderingFilter : used for ordering
    DjangoFilterBackend : used for filtering with  keys like ?gender=MALE
    """
    model = UserProfile
    queryset = UserProfile.objects.verified_freelancers_profiles()
    permission_classes = [LoggedInPermission]
    serializer_class = UserProfileDetailSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__email',
        'description',
        'nationality',
        'gender',
        'address',
        'business_name',
        'country',
    ]

    def get_queryset(self):
        """this is getting the filtered queryset from search filter
                 then adding more filtering   """
        queryset = self.filter_queryset(self.queryset.all())
        # FIXME: ASK QUESTION ON HOW THE QUERY WILL LOOK LIKE

        return queryset


class FreelancerDetailAPIView(RetrieveAPIView):
    # Get the detail of a freelancer using the id
    permission_classes = [LoggedInPermission]
    serializer_class = UserProfileDetailSerializer
    queryset = UserProfile.objects.verified_freelancers_profiles()
    lookup_field = "id"
