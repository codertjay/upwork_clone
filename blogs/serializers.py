from rest_framework import serializers

from blogs.models import Blog, BlogCategory, Comment
from users.serializers import UserProfileSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    """
    This serializer is meant to show details of a particular blog category or show all
    """

    class Meta:
        model = BlogCategory
        fields = ["id", "name", "timestamp"]


class BlogUpdateCreateSerializer(serializers.ModelSerializer):
    """This Creates a blog post and also used to update the blog post
    """
    published_date = serializers.DateField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "description",
            "image",
            "slug",
            "blog_categorys",
            "published_date",
        ]
        read_only_fields = ["id", "timestamp", "slug"]

    def create(self, validated_data):
        # the blog_categorys is in this form blog_categorys=[<blog_category instance>, ...] which are the instances
        # of a category
        blog_categorys = validated_data.pop('blog_categorys')
        instance = Blog.objects.create(**validated_data)
        for item in blog_categorys:
            try:
                instance.blog_categorys.add(item)
            except Exception as a:
                print(a)
        return instance


class BlogListSerializer(serializers.ModelSerializer):
    """This serializer is meant list a blog post . so it might not contain the full content of the blog
    user__profile : this is using the profile models in order to get the profile image of the user who made the blog post
    """
    user_profile = serializers.SerializerMethodField(read_only=True)
    blog_categorys = BlogCategorySerializer(many=True)

    class Meta:
        model = Blog
        fields = [
            "id",
            "slug",
            "user_profile",
            "title",
            "description",
            "view_count",
            "image",
            "read_time",
            "blog_categorys",
            "published_date",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_user_profile(self, obj):
        """get the profile info of a user which provides the image and other information"""
        return UserProfileSerializer(obj.user.user_profile, read_only=True).data


class BlogDetailSerializer(serializers.ModelSerializer):
    """this contains more info for the blog post , like the comments and other fields """
    comments = serializers.SerializerMethodField(read_only=True)
    user_profile = serializers.SerializerMethodField(read_only=True)
    blog_categorys = BlogCategorySerializer(many=True)

    class Meta:
        model = Blog
        read_only_fields = [
            "user__profile",
            "view_count",
            "timestamp",
            "comments",
        ]
        fields = [
            "id",
            "slug",
            "user_profile",
            "title",
            "description",
            "view_count",
            "image",
            "read_time",
            "published_date",
            "timestamp",
            "blog_categorys",
            "comments",
        ]

    def get_comments(self, obj):
        """return all comments on a blog post and also structure the replies"""
        serializer = CommentSerializer(obj.comments(), many=True)
        return serializer.data

    def get_user_profile(self, obj):
        """get the profile info of a user which provides the image and other information"""
        return UserProfileSerializer(obj.user.user_profile, read_only=True).data


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    This creates a comment and also update  comment
     made   parent_id not required
    """
    parent_id = serializers.IntegerField(required=False)

    class Meta:
        model = Comment
        fields = [
            "parent_id",
            "content",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer used to get the detail of a comment and also the child which are the replies of the
    comment """
    replies = serializers.SerializerMethodField(read_only=True)
    like_counts = serializers.SerializerMethodField(read_only=True)
    reply_counts = serializers.SerializerMethodField(read_only=True)
    user_profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        read_only_fields = [
            "reply_count",
            "replies",
            "like_counts",
            "user_profile",
            "blog_id",
        ]
        fields = [
            "id",
            "user_profile",
            "blog_id",
            "content",
            "reply_counts",
            "like_counts",
            'replies',
            "timestamp",
        ]

    def get_replies(self, obj):
        """ what we are trying to do here is getting the
         children which are the comment replies
         this obj.children() is a query set of all  """
        if obj.is_parent:
            return CommentReplySerializer(obj.children(), many=True).data
        return None

    def get_reply_counts(self, obj):
        """returns th total replies on a comment """
        if obj.is_parent:
            return obj.children().count()
        return None

    def get_like_counts(self, obj):
        """this returns the total count on likes on a comment"""
        return obj.likes.all().count()

    def get_user_profile(self, obj):
        """get the profile info of a user which provides the image and other information"""
        return UserProfileSerializer(obj.user.user_profile, read_only=True).data


class CommentReplySerializer(serializers.ModelSerializer):
    """Comment serializer used to serializer the reply of a comment"""
    user_profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user_profile",
            "blog_id",
            "content",
            "timestamp",
        ]

    def get_user_profile(self, obj):
        """get the profile info of a user which provides the image and other information"""
        return UserProfileSerializer(obj.user.user_profile, read_only=True).data
