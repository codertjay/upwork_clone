from django.db import models
import uuid
from django.conf import settings

# Create your models here.
from categorys.models import Category

User = settings.AUTH_USER_MODEL


class Catalogue(models.Model):
    """
    A freelancer can have get many catalogue
    The catalogue is project type which has sub items that list all items under it
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="catalogue")
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    @property
    def catalogue_items(self):
        return self.catalogue_item_set.all()


class CatalogueItem(models.Model):
    """
    the catalogue item is a model which is under the catalogue
    a catalogue has many catalogue_item
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, related_name="catalogue_item_set")
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="catalogue_item")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
