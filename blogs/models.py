from django.db import models
from django.utils import timezone

from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL


class Blog(models.Model):
    """
    If the user is deleted I don't intend to delete the blog post
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    view_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to="blog")
    read_time = models.IntegerField(default=0)
    # fixme : make category a model for blog or choices
    # blog_category = models.CharField()
    published_date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class Comment(models.Model):
    """
    this comment has a parent id which enables it to have a reply or more of like a thread
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def children(self):
        """ the bottom level this is the reply to the comments, so
        we use when looping through the normal comments like a nested comment
         we still use it in our api serializer for the children """
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        """ Note the parent is the first comment created
        if there is no parent it would return false
        note we are going to use it in our api where we define the replies
        for the children """
        if self.parent is not None:
            return False
        return True
