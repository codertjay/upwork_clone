from django.urls import path

from catalogues.views import CatalogueListCreateAPIView, CatalogueRetrieveUpdateDestroyAPIView, \
    CatalogueItemRetrieveUpdateDeleteAPIView, CatalogueItemListCreateAPIView, FreelancerCatalogueListCreateAPIView

urlpatterns = [
    #  all users catalogues
    path("", CatalogueListCreateAPIView.as_view(), name="catalogue_list_create"),
    #  for a specific user
    path("freelancer_catalogues/<str:user_id>/", FreelancerCatalogueListCreateAPIView.as_view(),
         name="freelancer_catalogue_list_create"),
    path("<str:id>/", CatalogueRetrieveUpdateDestroyAPIView.as_view(), name="catalogue_detail"),
    #  this url is for handling creating of catalogue items, and creating catalogue item
    path("catalogue_items/<str:catalogue_id>/", CatalogueItemListCreateAPIView.as_view(),
         name="catalogue_item_retrieve_update"),
    #  this url is meant for deleting catalogue item , updating,getting the detail
    path("catalogue_items/<str:catalogue_id>/<str:id>/",
         CatalogueItemRetrieveUpdateDeleteAPIView.as_view(),
         name="catalogue_item_retrieve_update"),
]
