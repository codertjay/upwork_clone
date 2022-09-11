from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BlogListAPIView, BlogCreateAPIView, BlogRetrieveUpdateDestroyAPIView, CommentListCreateAPIView, \
    CommentRetrieveUpdateDestroyAPIView, CommentLikeAPIView, BlogCategoryViewSetsAPIView

urlpatterns = [
    #  blog url
    path("", BlogListAPIView.as_view(), name="blog_list"),
    path("create/", BlogCreateAPIView.as_view(), name="blog_create"),
    #  I have to add blog/  to prevent the url from using the wrong view
    path("blog/<str:slug>/", BlogRetrieveUpdateDestroyAPIView.as_view(), name="blog_retrieve_update_destroy"),

    # comments url
    #  list all comments on a blog post
    path("comments/<str:blog_slug>/", CommentListCreateAPIView.as_view(), name="comment_list_create"),
    #  return the detail of a comment and also this deletes the comment and update it
    #  currently the blog_slug is not used in the filtering is just meant to arrange the url
    path("comments/<str:blog_slug>/<int:pk>/", CommentRetrieveUpdateDestroyAPIView.as_view(),
         name="comment_retrieve_update_destroy"),
    #  enables like a comment
    path("comment_like/<int:pk>/", CommentLikeAPIView.as_view(),
         name="comment_like"),
]
#  add the blog category url to the urlpatterns above
router = DefaultRouter()
router.register(r'blog_category', BlogCategoryViewSetsAPIView, basename='blog_category')
urlpatterns += router.urls
