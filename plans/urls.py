from django.urls import path

from .views import PlanCreateAPIView, PlanListAPIView, PlanRetrieveUpdateDestroyAPIView

urlpatterns = [
    #  subscriptions plan urls
    path("", PlanListAPIView.as_view(), name="list_subscriptions"),
    path("<str:id>/", PlanRetrieveUpdateDestroyAPIView.as_view(), name="create_retrieve_destroy"),
    path("create/", PlanCreateAPIView.as_view(), name="create_subscription"),

]
