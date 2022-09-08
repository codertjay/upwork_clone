from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from users.models import User
from users.permissions import LoggedInPermission
from .models import Catalogue, CatalogueItem
from .serializers import CatalogueDetailSerializer, CatalogueListSerializer, \
    CatalogueCreateUpdateSerializer, CatalogueItemSerializer


class CatalogueListCreateAPIView(ListCreateAPIView):
    """This view enables listing of catalogue of a user it requires the id of the user to be passed on the url """
    permission_classes = [LoggedInPermission]
    serializer_class = CatalogueListSerializer
    queryset = Catalogue.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "freelancer__first_name",
        "freelancer__last_name",
        "name",
        "description",
    ]

    def get_queryset(self):
        """this is getting the filtered queryset from search filter
                 then adding more filtering   """
        queryset = self.filter_queryset(self.queryset.all())
        # FIXME: ASK QUESTION ON HOW THE QUERY WILL LOOK LIKE

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a catalogue for the logged in freelancer
        """
        if self.request.user.user_type == "CUSTOMER":
            return Response(
                {"error": "Customers are not allowed to create catalogue please switch account to freelancer"},
                status=400)

        serializer = CatalogueCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(freelancer=self.request.user)
        return Response(status=201, data={"message": "Successfully created catalogue", "data": serializer.data})


class FreelancerCatalogueListCreateAPIView(ListCreateAPIView):
    """This view enables listing of catalogue of a user it requires the id of the user to be passed on the url """
    permission_classes = [LoggedInPermission]
    serializer_class = CatalogueListSerializer

    def get_queryset(self):
        # queryset to get the  user id catalogue
        user_id = self.kwargs.get("user_id")
        if not user_id:
            #  if the user id is not passed it raise a 404 response
            raise Http404
        user = User.objects.filter(id=user_id).first()
        if not user:
            # if the user does not exist it raise a 404 response
            raise Http404
        catalogues = Catalogue.objects.filter(freelancer=user)
        return catalogues


class CatalogueRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    This view is meant to retrieve a catalogue update it, and also destroy the catalogue
    """
    serializer_class = CatalogueDetailSerializer
    permission_classes = [LoggedInPermission]
    lookup_field = 'pk'
    queryset = Catalogue.objects.all()

    def update(self, request, *args, **kwargs):
        """
        Overriding the default update we need to just add the  CatalogueCreateUpdateSerializer for updating
        by adding partial=True enables us to pass less fields without having required error
        """
        instance = self.get_object()
        #  check if the user has access to deleting this catalogue
        if instance.freelancer != self.request.user:
            return Response({"error": "You dont have permission to update this catalogue"}, status=400)
        serializer = CatalogueCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  check if the user has access to deleting this catalogue
        if instance.freelancer != self.request.user:
            return Response({"error": "You dont have permission to update this catalogue"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class CatalogueItemListCreateAPIView(ListCreateAPIView):
    """
    This view enables creating of a catalogue item under a catalogue
    """
    permission_classes = [LoggedInPermission]
    serializer_class = CatalogueItemSerializer

    def get_queryset(self):
        catalogue_id = self.kwargs.get("catalogue_id")
        catalogue = Catalogue.objects.filter(id=catalogue_id).first()
        #  return the catalogue items under a catalogue using the property I created
        if not catalogue:
            return CatalogueItem.objects.none()
        return catalogue.catalogue_items

    def post(self, request, *args, **kwargs):
        #  we use the kwarg to get the catalogue_id get the catalogue
        catalogue_id = self.kwargs.get("catalogue_id")
        catalogue = Catalogue.objects.filter(id=catalogue_id).first()
        if not catalogue:
            return Response({"message": "Catalogue doesn't exist"}, status=404)
        serializer = CatalogueItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(catalogue=catalogue, freelancer=self.request.user)
        return Response({"message successfully created catalogue item"}, status=201)


class CatalogueItemRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    """
    This view is meant to get the detail of a catalogue item, delete , and update
    """
    permission_classes = [LoggedInPermission]
    serializer_class = CatalogueItemSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        It returns an object of a catalogue item using the catalogue id and the catalogue
        item pk to filter
        """
        catalogue_id = self.kwargs.get("catalogue_id")
        catalogue = Catalogue.objects.filter(id=catalogue_id).first()
        if not catalogue:
            #  if no catalogue i raise 404 page not found
            raise Http404
        catalogue_items = catalogue.catalogue_item_set.all()
        return catalogue_items.filter(id=self.kwargs.get("pk")).first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            # if the instance doesn't exist then i return 404 status
            return Response({"message": "item does not exist"}, status=404)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            # if the instance doesn't exist then I return 400 status
            return Response({"message": "item does not exist"}, status=400)
        #  check if the logged-in user is the freelancer who created the catalogue item
        if instance.freelancer != self.request.user:
            return Response({"error": "Not owner of the catalogue item"}, status=400)
        #  the partial enable us to update fields even if they are not passed in the database
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            # if the instance doesn't exist then I return 400 status
            return Response({"message": "item does not exist"}, status=400)
        #  check if the logged-in user is the freelancer who created the catalogue item
        if instance.freelancer != self.request.user:
            return Response({"error": "Not owner of the catalogue item"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)
