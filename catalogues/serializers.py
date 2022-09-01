from rest_framework import serializers

from catalogues.models import Catalogue, CatalogueItem
from categorys.serializers import CategorySerializer
from users.serializers import UserSerializer


class CatalogueListSerializer(serializers.ModelSerializer):
    """
    The serializer is used when creating a catalogue and also the freelancer is read only

    """
    freelancer = UserSerializer(read_only=True)
    # fixme: make this required
    image = serializers.ImageField(required=False)
    catalogue_items_count = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            'id',
            'name',
            'image',
            'description',
            'timestamp',
            'catalogue_items_count',
            'freelancer',
            'category',
        ]

    def get_catalogue_items_count(self, obj):
        """this returns the catalogue item count using the property we created"""
        return obj.catalogue_items.count()


class CatalogueCreateUpdateSerializer(serializers.ModelSerializer):
    """
    The serializer is used when creating a catalogue and also the freelancer is read only
    also the read_only in there prevent you from passing data to the freelance because the freelancer
    would be added the .save() method when saving the serailizer
    """
    freelancer = UserSerializer(read_only=True)
    # fixme: make this required
    image = serializers.ImageField(required=False)

    class Meta:
        model = Catalogue
        fields = [
            'id',
            'freelancer',
            'name',
            'image',
            'description',
            'category',
            'timestamp',
        ]

    def validate(self, obj):
        """
        we currently set category to allow null in the database of the Catalogue to prevent the
        catalogue from being deleted so if the category is not passed there wont be an error
        so i need to make sure it was passed
        """
        if not obj.get('category'):
            raise serializers.ValidationError(
                'Please provide a category id')
        return obj


class CatalogueDetailSerializer(serializers.ModelSerializer):
    """
    This contains list of items inside a catalog and also the catalogue itself
    """
    freelancer = UserSerializer(read_only=True)
    catalogue_items = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer(read_only=True)
    catalogue_items_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            'id',
            'name',
            'image',
            'description',
            'catalogue_items_count',
            'freelancer',
            'category',
            'catalogue_items',
            'timestamp',
        ]

    def get_catalogue_items(self, obj):
        """
        This enables us to access the catalogue items of a catalogue
        param obj: the instance
        :return: the serialized data of the CatalogueItemSerializer
        """
        serializer = CatalogueItemSerializer(obj.catalogue_items, many=True)
        return serializer.data

    def get_catalogue_items_count(self, obj):
        """this returns the catalogue item count using the property we created"""
        return obj.catalogue_items.count()


class CatalogueItemSerializer(serializers.ModelSerializer):
    """
    Serializer used to create a catalogue item, update the catalogue item, list and the detail
    """
    freelancer = UserSerializer(read_only=True)

    class Meta:
        model = CatalogueItem
        fields = [
            "id",
            "freelancer",
            "name",
            "image",
            "timestamp",
        ]
