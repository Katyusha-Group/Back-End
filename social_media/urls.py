from django.urls import path, include
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profiles')
urlpatterns = [
    path('', include(router.urls)),
]
