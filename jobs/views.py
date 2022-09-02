from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView

from users.permissions import LoggedInPermission


class CreateJobSerializer(CreateAPIView):
    permission_classes = [LoggedInPermission]