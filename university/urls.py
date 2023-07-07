from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'courses', viewset=views.CourseViewSet, basename='courses')
router.register(r'teachers', viewset=views.TeacherViewSet, basename='teachers')

urlpatterns = [
    path('', include(router.urls)),
    path('departments/', views.DepartmentListView.as_view(), name='departments'),
    path('departments/names', views.SignupDepartmentListView.as_view(), name='department_names'),
    path('departments/all', views.AllDepartmentsListView.as_view(), name='all_departments'),
    path('timeline/courses/<int:course_number>', views.BaseCoursesTimeLineListAPIView.as_view(), name='timeline'),
    path('timeline/teachers/<int:teacher_id>', views.TeachersTimeLineListAPIView.as_view(), name='timeline'),
    path('coursegroups/<base_course_id>', views.CourseGroupListView.as_view({'get': 'list'}), name='coursegroups'),
    path('allcoursesdepartment/', views.AllCourseDepartmentList.as_view(), name='allcoursedepartment'),
    path('allcourses-based-department/<int:department_id>', views.AllCourseDepartmentRetrieve.as_view(),
         name='allcoursedepartment_retrieve'),
]
