# Create your views here.
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from users.permissions import LoggedInPermission
from .models import Catalogue
from .serializers import CatalogueListCreateSerializer


class CatalogueListCreateAPIView(ListCreateAPIView):
    permission_classes = [LoggedInPermission]
    serializer_class = CatalogueListCreateSerializer

    def get_queryset(self):
        # queryset to get the current user catalogue
        catalogues = Catalogue.objects.filter(freelancer=self.request.user)
        return catalogues

    def create(self, request, *args, **kwargs):
        """
        Create a catalogue for the logged in freelancer
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = CatalogueListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(freelancer=self.request.user)
        return Response(status=201, data={"message": "Successfully created catalogue", "data": serializer.data})
