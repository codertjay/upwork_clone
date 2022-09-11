from .views import CategoryViewSetsAPIView
from rest_framework.routers import DefaultRouter

"""
I created a view set that enables me to create, update, list and delete a catalogue
if you would like to change the routes then you can just add `.as_view({'get': 'list'})`
"""
router = DefaultRouter()
router.register(r'', CategoryViewSetsAPIView, basename='categorys')
urlpatterns = router.urls
