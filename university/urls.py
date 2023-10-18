from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'courses', viewset=views.CourseViewSet, basename='courses')
router.register(r'teachers', viewset=views.TeacherViewSet, basename='teachers')

urlpatterns = [
    path('', include(router.urls)),
    path('semeters/', views.SemesterViewList.as_view(), name='semesters'),
    path('departments/', views.DepartmentsListView.as_view(), name='departments'),
    path('departments/names', views.SignupDepartmentListView.as_view(), name='department_names'),
    path('departments/sorted-names', views.SortedNamesDepartmentListView.as_view(), name='sorted_department_names'),
    path('timeline/courses/<int:course_number>', views.BaseCoursesTimeLineListAPIView.as_view(),
         name='course_timeline'),
    path('timeline/teachers/<int:teacher_id>', views.TeachersTimeLineListAPIView.as_view(), name='teacher_timeline'),
    path('coursegroups/<base_course_id>', views.CourseGroupListView.as_view({'get': 'list'}), name='course-groups'),
    path('allcoursesdepartment/', views.AllCourseDepartmentList.as_view(), name='all-course-department'),
    path('allcourses-based-department/<int:department_id>', views.AllCourseDepartmentRetrieve.as_view(),
         name='all-course-department_retrieve'),
]
