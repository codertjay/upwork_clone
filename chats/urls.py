from .views import MessageViewSet, ConversationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# conversation route
router.register("conversations", ConversationViewSet)
urlpatterns = router.urls
#  message route
router.register("messages", MessageViewSet)
# add the messages users to the urlspatterns
urlpatterns += router.urls
