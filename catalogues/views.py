from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from users.permissions import LoggedInPermission
from .models import Catalogue, CatalogueItem
from .serializers import CatalogueDetailSerializer, CatalogueListSerializer, \
    CatalogueCreateUpdateSerializer, CatalogueItemSerializer


class CatalogueListCreateAPIView(ListCreateAPIView):
    permission_classes = [LoggedInPermission]
    serializer_class = CatalogueListSerializer

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
        serializer = CatalogueCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(freelancer=self.request.user)
        return Response(status=201, data={"message": "Successfully created catalogue", "data": serializer.data})


class CatalogueRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    This view is meant to retrieve a catalogue update it, and also destroy the catalogue
    """
    serializer_class = CatalogueDetailSerializer
    permission_classes = [LoggedInPermission]
    lookup_field = 'pk'

    def get_queryset(self):
        """
        returns the detail of a user catalogue using the catalogue detail serializer
        :return:
        """
        catalogues = Catalogue.objects.filter(freelancer=self.request.user)
        return catalogues

    def update(self, request, *args, **kwargs):
        """
        Overriding the default update we need to just add the  CatalogueCreateUpdateSerializer for updating
        by adding partial=True enables us to pass less fields without having required error
        """
        instance = self.get_object()
        serializer = CatalogueCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ListCreateCatalogueItem(ListCreateAPIView):
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

    def get_queryset(self):
        """
        It returns a queryset of all the category items on a category
        :return:
        """
        catalogue_id = self.kwargs.get("catalogue_id")
        catalogue_item_id = self.kwargs.get("pk")
        catalogue = Catalogue.objects.filter(id=catalogue_id).first()
        #  return the catalogue items under a catalogue using the property I created
        #  check for the catalogue_item_id
        if not catalogue:
            #  it returns no queryset of the catalogue items
            return CatalogueItem.objects.none()
        else:
            return catalogue.catalogue_item_set.all()

    def get_object(self):
        #  getting a catalogue item from the queryset
        return self.get_queryset().filter(id=self.kwargs.get("pk")).first()

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
            # if the instance doesn't exist then i return 400 status
            return Response({"message": "item does not exist"}, status=400)
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
        self.perform_destroy(instance)
        return Response(status=204)
