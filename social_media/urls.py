from django.urls import path, include
from accounts import views
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

router = routers.DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
]
