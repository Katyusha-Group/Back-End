from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from university.pagination import DefaultPagination
from university.filters import CourseFilter
from university.models import Course, Department, Semester, ExamTimePlace
from university.serializers import DepartmentSerializer, SemesterSerializer, SimpleCourseSerializer, \
    MyCourseSerializer, AddCourseSerializer, CourseExamTimeSerializer
from university.scripts import app_variables


class DepartmentViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        user = get_user_model().objects.get(id=user_id)
        return Department.objects.filter(
            department_number__in=app_variables.GENERAL_DEPARTMENTS + [user.department.department_number]).all()


class SemesterViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = SemesterSerializer

    def get_queryset(self):
        return Semester.objects.all()


class CourseViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleCourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter

    def get_serializer_class(self):
        if self.action == 'my_courses' and self.request.method == 'PUT':
            return AddCourseSerializer
        elif self.action == 'my_courses' and self.request.method == 'GET':
            return MyCourseSerializer
        elif self.action == 'my_exams' and self.request.method == 'GET':
            return CourseExamTimeSerializer
        return SimpleCourseSerializer

    def get_queryset(self):
        department = self.request.query_params.get('department_number', None)
        user_id = self.request.user.id
        user = get_user_model().objects.get(id=user_id)
        courses = Course.objects.filter(Q(sex=user.gender) | Q(sex='B'))
        if department is not None and department.isdigit():
            department = int(department)
            if department in app_variables.GENERAL_DEPARTMENTS or department == user.department.department_number:
                return courses.filter(base_course__department=department) \
                    .select_related('base_course')
        return courses.filter(
            base_course__department__in=app_variables.GENERAL_DEPARTMENTS + [
                user.department.department_number]).select_related('base_course')

    @action(detail=False, methods=['GET', 'PUT'])
    def my_courses(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        if request.method == 'GET':
            courses = MyCourseSerializer(student.courses.all(), many=True)
            return Response(status=status.HTTP_200_OK, data=courses.data)
        elif request.method == 'PUT':
            serializer = AddCourseSerializer(data=request.data, context={'user_id': request.user.id})
            serializer.is_valid(raise_exception=True)
            serializer.save(student=student)
            return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def my_exams(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        exam_ids = student.courses.values('exam_times')
        exams = ExamTimePlace.objects.filter(pk__in=exam_ids)
        serializer = CourseExamTimeSerializer(exams, many=True)
        return Response(data=serializer.data)
