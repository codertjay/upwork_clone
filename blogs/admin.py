from django.contrib import admin

from .models import Comment, CommentLike, Blog

admin.site.register(CommentLike)
admin.site.register(Comment)
admin.site.register(Blog)
