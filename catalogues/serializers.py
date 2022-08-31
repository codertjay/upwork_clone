from rest_framework import serializers

from catalogues.models import Catalogue
from users.serializers import UserSerializer


class CatalogueListCreateSerializer(serializers.ModelSerializer):
    """
    The serializer is used when creating a catalogue and also the freelancer is read only

    """
    freelancer = UserSerializer(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            'freelancer',
            'name',
            'image',
            'description',
            'categorys',
            'timestamp',
        ]


class CatalogueDetailSerializer(serializers.ModelSerializer):
    """
    This contains list of items inside a catalog and also the catalogue itself
    """
    freelancer = UserSerializer(read_only=True)
    catalogue_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            'freelancer',
            'name',
            'image',
            'description',
            'categorys',
            'timestamp',
        ]

    def get_catalogue_items(self,obj):
        serializer = CatalogueItemSerializer(obj.c)




class CatalogueItemSerializer(serializers.ModelSerializer):
    """
    Serializer used to create a catalogue item, update the catalogue item, list and the detail
    """
