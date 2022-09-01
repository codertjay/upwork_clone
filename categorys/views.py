from rest_framework.viewsets import ModelViewSet

from users.permissions import LoggedInPermission
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSetsAPIView(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [LoggedInPermission]
    queryset = Category.objects.all()

