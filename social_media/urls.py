from django.urls import path, include
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profiles')
router.register(r'twittes', views.TwitteViewSet, basename='twittes')
router.register(r'followings-twittes', views.FollowingTwittesViewSet, basename='followings-twittes')
router.register(r'for-you-twittes', views.ForYouTwittesViewSet, basename='for-you-twittes')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')
router.register(r'twitte-charts', views.TwitteChartViewSet, basename='twitte-charts')
router.register(r'report-twitte', views.ReportTwitteViewSet, basename='report-twitte')
router.register(r'manage-reported-twittes', views.ManageReportedTwittesViewSet, basename='manage-reported-twittes')
router.register(r'manage-twittes', views.ManageTwittesViewSet, basename='manage-twittes')

urlpatterns = [
    path('', include(router.urls)),
]
