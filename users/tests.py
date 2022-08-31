from decouple import config
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User

HTTP_INSTASAW_SK_HEADER = config("INSTASAW_SK_HEADER")


class UserTestCase(TestCase):

    def setUp(self):
        self.user_email = "dev.codertjay@gmail.com"
        self.password = "@Pas77sword12"
        self.user = User.objects.create(
            email=self.user_email,
            password=self.password,
            first_name="First1",
            last_name="Last1",
            user_type="CUSTOMER"
        )
        #  message returned if the user is not verified
        self.not_verified_message = "Please verify your email address."

    def get_api_client(self):
        """Returns APIClient instance which is authenticated"""
        client = APIClient()
        client.force_authenticate(user=self.user)
        client.credentials()
        return client

    def test_user_signup(self):
        client = APIClient()
        email = "favourdeveloper@gmail.com"
        password = "@pass$word"
        signup_response = client.post("/api/v1/auth/registration/", {
            "email": email,
            "user_type": "FREELANCER",
            "first_name": "First1",
            "last_name": "First2",
            "password1": password,
            "password2": password,
        }, )
        # Email address not yet verified
        self.assertEqual(signup_response.status_code, 400)
        self.assertEqual(signup_response.json().get("message"), self.not_verified_message)

    def test_not_verified_user_login(self):
        client = APIClient()
        print(self.user.user_type)
        login_response = client.post("/api/v1/auth/login/", {
            "email": self.user_email,
            "password": self.password,
        }, )
        print(login_response.json())
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(login_response.json().get("message"), self.not_verified_message)

    def test_verify_and_check_if_profile_created(self):
        """
        This test if the user profile was created,
        and also it verify the user first
        :return:
        """
        #  checks if the user profile is not none
        self.assertIsNotNone(self.user.user_profile)
        #  request otp for the set-up user
        client = APIClient()
        request_otp_response = client.post("/api/v1/auth/request_email_otp/", {
            "email": self.user_email,
        })
        print(request_otp_response.json())
        self.assertEqual(request_otp_response.status_code, 200)
        otp = input("Please input otp to verify account.")
        verify_email_response = client.post("/api/v1/auth/verify_email", {
            "otp": otp
        })
        self.assertEqual(verify_email_response.status_code, 200)

    def test_update_user_profile(self):
        """
        Update the user profile . which  was created using a signal once a user was created
        :return: 
        """
        client = APIClient()
        update_response = client.post("/api/v1/auth/profile_update", {
            "gender": "MALE",
            "date_of_birth": "2010-12-12",
            "mobile": "12345666",
            "address": "House address",
            "business_name": "My business name",
            "description": "My info ",
            "nationality": "Nigerian",
            "country": "Nigeria",
            "city": "Lagos"
        })
        print(update_response.json())
        self.assertEqual(update_response.status_code, 200)
