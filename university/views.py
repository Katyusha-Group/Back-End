from django.contrib.auth import get_user_model
from django.db.models import Count, ExpressionWrapper, F, FloatField, Case, When, Value, IntegerField, Prefetch, \
    BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from custom_config.ordering_filrers import TeacherOrderingFilter
from university.models import Course, Department, Semester, ExamTimePlace, BaseCourse, Teacher
from university.pagination import DefaultPagination
from university.scripts.get_or_create import get_course
from university.scripts.views_scripts import get_user_department, sort_departments_by_user_department
from university.serializers import DepartmentSerializer, SemesterSerializer, ModifyMyCourseSerializer, \
    CourseExamTimeSerializer, CourseSerializer, SummaryCourseSerializer, \
    CourseGroupSerializer, SimpleDepartmentSerializer, AllCourseDepartmentSerializer, BaseCourseTimeLineSerializer, \
    SimpleTeacherSerializer, TeacherTimeLineSerializer, TeacherSerializer
from rest_framework.views import APIView
from utils import project_variables


class SignupDepartmentListView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    serializer_class = SimpleDepartmentSerializer
    permission_classes = []

    def get_queryset(self):
        return Department.objects.filter(department_number__gt=0).all()


class DepartmentListView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'api': 'allowed'}

    def get_queryset(self):
        departments = Department.objects.all()
        user_department = get_user_department(self.request.user)
        return sort_departments_by_user_department(departments, user_department)


class AllDepartmentsListView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'api': 'all'}

    def get_queryset(self):
        departments = Department.objects.all().prefetch_related(
            'allowed_departments__course__base_course')
        user_department = get_user_department(self.request.user)
        return sort_departments_by_user_department(departments, user_department)


class SemesterViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = SemesterSerializer

    def get_queryset(self):
        return Semester.objects.all()


class CourseViewSet(ListModelMixin, GenericViewSet):
    http_method_names = ['get', 'put', 'head', 'options']
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    lookup_url_kwarg = 'course_number'

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_permissions(self):
        if self.action in ['my_courses', 'my_exams', 'my_summary']:
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            self.permission_classes = [IsAdminUser]
        return super(CourseViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'my_courses' and self.request.method == 'PUT':
            return ModifyMyCourseSerializer
        elif self.action == 'my_exams' and self.request.method == 'GET':
            return CourseExamTimeSerializer
        elif self.action == 'my_summary' and self.request.method == 'GET':
            return SummaryCourseSerializer
        return CourseSerializer

    def get_queryset(self):
        return Course.objects.prefetch_related('teachers',
                                               'course_times',
                                               'exam_times',
                                               'base_course',
                                               'students',
                                               'allowed_departments__department__user_set').filter(
            semester=project_variables.CURRENT_SEMESTER).all()

    def get_object(self):
        return get_course(course_code=self.kwargs['course_number'], semester=project_variables.CURRENT_SEMESTER)

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course)
        return Response(data=serializer.data)

    @action(detail=False, methods=['GET', 'PUT'])
    def my_courses(self, request):
        student = request.user
        if request.method == 'GET':
            courses = CourseSerializer(
                (student.courses.prefetch_related('course_times',
                                                  'teachers',
                                                  'exam_times', )
                 .select_related('base_course__department')
                 .prefetch_related(Prefetch('base_course__department', Department.objects.all())).all()),
                many=True,
                context=self.get_serializer_context()
            )
            return Response(status=status.HTTP_200_OK, data=courses.data)
        elif request.method == 'PUT':
            serializer = ModifyMyCourseSerializer(data=request.data, context={'user_id': request.user.id})
            serializer.is_valid(raise_exception=True)
            _, created = serializer.save(student=student)
            message = 'Course added to calendar' if created else 'Course deleted from calendar'
            return Response(status=status.HTTP_200_OK, data={'message': message})

    @action(detail=False, methods=['GET'])
    def my_exams(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        exam_ids = student.courses.prefetch_related('exam_times', 'base_course').values('exam_times')
        exams = ExamTimePlace.objects.filter(pk__in=exam_ids)
        serializer = CourseExamTimeSerializer(exams, many=True)
        return Response(data=serializer.data)

    @action(detail=False, methods=['GET'])
    def my_summary(self, request):
        user = get_user_model().objects.get(id=request.user.id)
        course_data = user.courses.prefetch_related('base_course')
        courses = SummaryCourseSerializer(
            course_data,
            many=True,
            context={'user': user}
        )
        return Response(status=status.HTTP_200_OK,
                        data={'unit_count': sum([course.base_course.total_unit for course in course_data]),
                              'data': courses.data})


class BaseCoursesTimeLineListAPIView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = BaseCourseTimeLineSerializer

    def get_queryset(self):
        return BaseCourse.objects.filter(course_number=self.kwargs['course_number']).all()


class TeachersTimeLineListAPIView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherTimeLineSerializer

    def get_queryset(self):
        return Teacher.objects.filter(pk=self.kwargs['teacher_id']).all()


class CourseGroupListView(ModelViewSet):
    serializer_class = CourseGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        base_course_id = self.kwargs['base_course_id']
        if base_course_id is None:
            raise ValidationError({'detail': 'Enter course_number as query string in the url.'}, )
        elif base_course_id.isdigit() is True:
            base_course_id = int(base_course_id)
        else:
            raise ValidationError({'detail': 'Enter course_number as query number in the url.'}, )
        user = self.request.user
        courses = (
            Course.objects
            .select_related('base_course', 'semester')
            .prefetch_related('teachers',
                              'course_times',
                              'exam_times',
                              'students')
            .filter(base_course_id=base_course_id, semester_id=project_variables.CURRENT_SEMESTER,
                    sex__in=[user.gender, 'B'])
            .annotate(empty_capacity=ExpressionWrapper(
                F('capacity') - F('registered_count'),
                output_field=IntegerField()
            ))
            .annotate(student_count=Count('students'))
            .annotate(
                color_intensity_percentage_first=ExpressionWrapper(
                    (((F('capacity') - F('registered_count') - F('waiting_count')) * 100) / (
                            F('capacity') + F('waiting_count') + (1.2 * F('student_count')))),
                    output_field=FloatField())
            )
            .annotate(
                capacity_is_less_zero=Case(
                    When(empty_capacity__lte=0, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
            .order_by('capacity_is_less_zero', 'empty_capacity', 'color_intensity_percentage_first')
            .all()
        )
        if courses.exists():
            return courses
        else:
            raise ValidationError({'detail': 'No course with this course_number in database.'}, )


class BaseAllCourseDepartment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id, *args, **kwargs):
        all_courses = (
            Course.objects
            .filter(base_course__department_id=department_id, semester=project_variables.CURRENT_SEMESTER)
            .select_related('base_course')
            .prefetch_related('course_times', 'exam_times', 'students', 'teachers')
            .all()
        )
        return Response(AllCourseDepartmentSerializer(all_courses, many=True, context={'user': self.request.user}).data)


class AllCourseDepartmentList(BaseAllCourseDepartment):
    def get(self, request, *args, **kwargs):
        return super(AllCourseDepartmentList, self).get(request, request.user.department_id, *args, **kwargs)


class AllCourseDepartmentRetrieve(BaseAllCourseDepartment):
    def get(self, request, department_id, *args, **kwargs):
        return super(AllCourseDepartmentRetrieve, self).get(request, department_id, *args, **kwargs)


class TeacherViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    serializer_class = SimpleTeacherSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [SearchFilter, TeacherOrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'total_score', 'total_vote_count']

    def get_queryset(self):
        return Teacher.objects.filter(courses__semester=project_variables.CURRENT_SEMESTER).distinct().all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TeacherSerializer(instance, context={'user': request.user})
        return Response(serializer.data)
