from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
router.register(r'semesters', views.SemesterViewSet, basename='semesters')
router.register(r'departments', views.DepartmentViewSet, basename='departments')
router.register(r'courses', views.CourseViewSet, basename='courses')

urlpatterns = [
    path('', include(router.urls)),
]


