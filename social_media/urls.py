from django.urls import path, include
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profiles')
router.register(r'twittes', views.TwitteViewSet, basename='twittes')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')
router.register(r'twitte-charts', views.TwitteChartViewSet, basename='twitte-charts')
urlpatterns = [
    path('', include(router.urls)),
]
