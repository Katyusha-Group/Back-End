from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('courses', viewset=views.CourseViewSet, basename='courses')

urlpatterns = [
    path('', include(router.urls)),
    # path('courses/', views.CourseViewSet.as_view(), name='courses'),
    path('departments/', views.DepartmentListView.as_view(), name='departments')
]
