from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone

from django.conf import settings

from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class BlogCategory(models.Model):
    """This category is meant for only the blog post it is different from the category for job post and catalogue
    Reason why i created a new one is to prevent users from seeing blog categorys
     which could not be appropriate for the nomal category like shirt
    """
    name = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class BlogManager(models.Manager):
    """
    the creates helper function tied to the blog models that enables us create
    more queries and other ....
    """

    def all_published_blogs(self):
        #  list all blog post with published_date is less than now
        return self.filter(published_date__lte=timezone.now())


class Blog(models.Model):
    """
    If the user is deleted I don't intend to delete the blog post
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    view_count = models.IntegerField(default=0)
    # todo: forgot to add this on cacoo
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="blog")
    read_time = models.IntegerField(default=0)
    blog_categorys = models.ManyToManyField(BlogCategory, related_name="blog")
    published_date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = BlogManager()

    class Meta:
        ordering = ['-timestamp']

    def comments(self):
        """return all the comments without parents"""
        return self.comment_set.comment_without_parent()


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a blog post before it is being saved
    # todo: calculate blog read time
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Blog)


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class CommentManager(models.Manager):
    def comment_without_parent(self):
        """this returns all the comment but exclude the comments which are replies """
        return self.filter(parent=None)


class Comment(models.Model):
    """
    this comment has a parent id which enables it to have a reply or more of like a thread
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='comment_likes', through=CommentLike, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = CommentManager()

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


def create_slug(instance, new_slug=None):
    """
    This creates a slug for a blog ost before it is being
     saved and if the slug exist it add the id the old post to the slug
    :param instance: blog post
    :param new_slug: slug passed if existed
    :return: slug
    """
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Blog.objects.filter(slug=slug).order_by('-id')
    if qs.exists():
        new_slug = f'{slug}-{qs.first().id}'
        return create_slug(instance, new_slug=new_slug)
    return slug
