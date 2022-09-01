from django.db import models

from django.conf import settings

# Create your models here.
from categorys.models import Category

User = settings.AUTH_USER_MODEL


class Catalogue(models.Model):
    """
    A freelancer can have get many catalogue
    The catalogue is project type which has sub items that list all items under it
    """
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="catalogue")
    description = models.TextField()
    categorys = models.ManyToManyField(Category)
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
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    catalogue = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="catalogue_item_set")
    name = models.CharField(max_length=250, blank=True, null=True)
    image = models.ImageField(upload_to="catalogue_item")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
