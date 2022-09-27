from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from blogs.models import Blog, Comment, CommentLike, BlogCategory
from users.permissions import NotLoggedInPermission, LoggedInPermission, LoggedInStaffPermission
from .serializers import BlogListSerializer, BlogDetailSerializer, CommentSerializer, CommentCreateUpdateSerializer, \
    BlogUpdateCreateSerializer, BlogCategorySerializer


class BlogCategoryViewSetsAPIView(ModelViewSet):
    """this view set enables the full crud which are create, retrieve,update and delete  """
    serializer_class = BlogCategorySerializer
    permission_classes = [LoggedInPermission]
    queryset = BlogCategory.objects.all()


class BlogListAPIView(ListAPIView):
    """Show all blog post. By default, it is paginated by 50 which has already being set in the settings/base.py file"""
    permission_classes = [NotLoggedInPermission]
    serializer_class = BlogListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    queryset = Blog.objects.all_published_blogs()
    search_fields = [
        "title",
        "slug",
    ]

    def get_queryset(self):
        """this is getting the filtered queryset from search filter
                 then adding more filtering   """
        queryset = self.filter_queryset(self.queryset.all())
        # FIXME: ASK QUESTION ON HOW THE QUERY WILL LOOK LIKE

        return queryset


class BlogCreateAPIView(CreateAPIView):
    """this creates a blog post, but it needs other permission to enable creating a blog post to prevent random from
    just writing post """
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]
    serializer_class = BlogUpdateCreateSerializer

    def create(self, request, *args, **kwargs):
        """to enable us to pass other fields like the user for th blog post we need to override this create function"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=201)


class BlogRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """using the slug for the lookup field and also filtering only through published blog posts"""
    lookup_field = 'slug'
    serializer_class = BlogDetailSerializer
    queryset = Blog.objects.all_published_blogs()
    permission_classes = [NotLoggedInPermission]

    def update(self, request, *args, **kwargs):
        """this update the blog post, but it checks if the user is the owner or a staff member"""
        instance = self.get_object()
        if instance.user != request.user or not request.user.is_staff:
            return Response({"error": "Dont have permission to update this post"}, status=400)
        serializer = BlogUpdateCreateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """this deletes the blog post, but it checks if the user is the owner or a staff member"""
        instance = self.get_object()
        if instance.user != request.user or not request.user.is_staff:
            return Response({"error": "Don't have permission to update this post"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class CommentListCreateAPIView(ListCreateAPIView):
    """this enables creating a comment and also listing all comments but excludes the reply comments on a blog post"""
    serializer_class = CommentSerializer
    permission_classes = [LoggedInPermission]

    def get_blog(self):
        """
        Helper function
        this uses the slug passed in the url to filter the blog post and if it doest not exist it raises 404
        :return: blog instance
        """
        blog_slug = self.kwargs.get("blog_slug")
        blog = Blog.objects.filter(slug=blog_slug).first()
        if not blog:
            raise Http404
        return blog

    def get_queryset(self):
        """return all comments on a blog post"""
        queryset = Comment.objects.comment_without_parent().filter(blog=self.get_blog())
        return queryset

    def create(self, request, *args, **kwargs):
        """this creates a comment and also create  replies when the parent comment id is passed
        and also prevent a user from making more than 20 comment on a blog post
        """
        if self.get_queryset().filter(user=self.request.user).count() > 20:
            return Response({"error": "Not allowed to make more than 20 comments on a blog post"}, status=400)
        serializer = CommentCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(blog=self.get_blog(), user=self.request.user)
        return Response(serializer.data, status=201)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    enables getting the detail of a comment, updating the comment and also deleting the comment
    """
    serializer_class = CommentCreateUpdateSerializer
    permission_classes = [NotLoggedInPermission]
    lookup_field = "id"
    queryset = Comment.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """the detail of the comment with replies"""
        instance = self.get_object()
        serializer = CommentSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """this update the comment of the blog post and also check the user updating the post"""
        instance = self.get_object()

        if instance.user != request.user or not request.user.is_staff:
            return Response({"error": "you don't have permission to update this comment"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user or not request.user.is_staff:
            return Response({"error": "you don't have permission to delete this comment"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class CommentLikeAPIView(APIView):
    """this class enables like  a comment """
    permission_classes = [LoggedInPermission]

    def get_comment(self):
        """helper function which enables us to get the comment through the id which passed in the url
        and if the comment does not exist i raise 404 error response
        """
        comment_id = self.kwargs.get("id")
        comment = Comment.objects.filter(id=comment_id).first()
        if not comment:
            raise Http404
        return comment

    def post(self, request, *args, **kwargs):
        """in here we check if the user has like the comment and if he had liked it i unlike the comment"""
        comment = self.get_comment()
        # check if the user has liked before
        if comment.likes.filter(email=self.request.user.email).exists():
            # if the user has liked then i delete the comment like model
            # which made the comment unliked . I Cant access the comment like with the comment so i had to filter
            #  using the comment like model
            comment_like = CommentLike.objects.filter(comment=comment, user=self.request.user).first()
            if not comment_like:
                #  but this is next to impossible to occur
                return Response({"message": "Comment not like by the user"}, status=200)
            comment_like.delete()
            return Response({"message": "Successfully unliked comment"}, status=200)
        comment_like, created = CommentLike.objects.get_or_create(user=self.request.user, comment=comment)
        if created:
            #  it returns success because we just liked the comment
            return Response({"message": "Successfully liked this comment"}, status=200)
        # this would not occur because we made a filter above but if it might I just need to handle it
        return Response({"message": "Already liked this comment"}, status=400)
