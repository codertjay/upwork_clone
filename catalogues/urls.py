from django.urls import path

from catalogues.views import CatalogueListCreateAPIView

urlpatterns = [
    path("", CatalogueListCreateAPIView.as_view(), name="catalogue_list_create"),
]
