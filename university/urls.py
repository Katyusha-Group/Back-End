from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'courses', viewset=views.CourseViewSet, basename='courses')
# other_router = routers.SimpleRouter()
# other_router.register(r'coursegroups', views.CourseGroupListView, basename='coursegroups')
#

urlpatterns = [
    path('', include(router.urls)),
    path('departments/', views.DepartmentListView.as_view(), name='departments'),
    path('departments/names', views.SignupDepartmentListView.as_view(), name='department_names'),
    path('departments/all', views.AllDepartmentsListView.as_view(), name='all_departments'),
    path('timeline/<int:course_number>', views.TimelineViewSet.as_view(), name='timeline'),
    path('coursegroups/<base_course_id>', views.CourseGroupListView.as_view({'get': 'list'}), name='coursegroups'),
    path('teacher/<int:pk>', views.TeacherProfileRetrieveAPIView.as_view(), name='teacher'),
    # path('cou/', include(other_router.urls)),
    path('course_student_count/<base_course_id>', views.CourseStudentCountView.as_view(), name='course_student_count'),
    path('allcoursesdepartment/', views.AllCourseDepartment.as_view(), name='allcoursedepartment'),
    path('allcourses-based-department/<int:department_id>', views.All.as_view(), name='all'),
]
