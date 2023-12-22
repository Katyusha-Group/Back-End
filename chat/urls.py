from django.urls import path, include
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('chat', views.ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
