from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.permissions import NotLoggedInPermission, LoggedInPermission
from users.serializers import VerifyEmailSerializer, UserProfileUpdateSerializer


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

        # login the user to access him/ her on the request
        self.login()
        #  overriding the login of allauth to add this if user is not verified
        if not request.user.verified:
            return Response({"message": "Please verify your email address."},
                            status=400)
        return self.get_response()


class InstasawRegisterAPIView(RegisterView):
    """
    Register view which contains throttle and can be access three times in a minute
    """
    throttle_scope = 'authentication'

    # permission_classes = [NotLoggedInPermission]

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
                return Response({'message': 'Please pass in the correct data'}, status=400)
            if user.validate_email_otp(otp):
                user.verified = True
                user.save()
                return Response({'message': 'Successfully verify your mail'}, status=200)
            return Response({'message': 'Email Not Verified .Time exceeded or OTP is invalid'}, status=400)
        except Exception as a:
            print("error-----", a)
            return Response({'message': 'There was an error performing your request.Email Not Verified'}, status=400)


class UserProfileUpdateAPIView(APIView):
    """
    User update api view enables you to update the user api
    """
    permission_classes = [LoggedInPermission]

    def put(self, request):
        """Update a user profile base on the data passed also we used related name to access
        the user profile"""
        serializer = UserProfileUpdateSerializer(instance=self.request.user.user_profile, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=200,
            data={"message": "successfully updated user profile",
                  "data": UserProfileUpdateSerializer(request.user.user_profile).data
                  })
