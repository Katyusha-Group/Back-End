from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'courses', viewset=views.CourseViewSet, basename='courses')
router.register(r'teachers', viewset=views.TeacherViewSet, basename='teachers')

urlpatterns = [
    path('', include(router.urls)),
    # semesters:
    path('semesters/', views.SemestersViewList.as_view(), name='semesters'),

    # departments:
    path('departments/', views.DepartmentsListView.as_view(), name='departments'),
    path('departments/names', views.SignupDepartmentListView.as_view(), name='department-names'),
    path('departments/sorted-names', views.SortedNamesDepartmentListView.as_view(), name='sorted-department-names'),

    # timelines:
    path('timeline/courses/<int:course_number>', views.BaseCoursesTimeLineListAPIView.as_view(),
         name='course-timeline'),
    path('timeline/teachers/<int:teacher_pk>', views.TeachersTimeLineListAPIView.as_view(), name='teacher-timeline'),

    # courses:
    path('coursegroups/<base_course_pk>', views.CourseGroupListView.as_view({'get': 'list'}), name='course-groups'),
    path('allcoursesdepartment/', views.AllCourseDepartmentList.as_view(), name='all-course-department'),
    path('allcourses-based-department/<int:department_number>', views.AllCourseDepartmentRetrieve.as_view(),
         name='all-course-department_retrieve'),
]
