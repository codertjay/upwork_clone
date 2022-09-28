from django.db import models
import uuid

# Create your models here.
class Category(models.Model):
    """
    This category is being used when creating a job , catalogue also
    it enables matching items base on filtering for that item either job or catalogue
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4(), editable=False, unique=True)
    name = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
