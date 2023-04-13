from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from university.pagination import DefaultPagination
from university.models import Course, Department, Semester
from university.serializers import DepartmentSerializer, SemesterSerializer, SimpleCourseSerializer, \
    MyCourseSerializer, AddCourseSerializer, CourseExamTimeSerializer


class DepartmentViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.all()


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
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == 'my_courses' and self.request.method == 'PUT':
            return AddCourseSerializer
        elif self.action == 'my_courses' and self.request.method == 'GET':
            return MyCourseSerializer
        elif self.action == 'my_exams' and self.request.method == 'GET':
            return CourseExamTimeSerializer
        return SimpleCourseSerializer

    def get_queryset(self):
        # TODO: Filter based on student sex
        department = self.request.query_params.get('department_pk', None)
        semester = self.request.query_params.get('semester_pk', None)
        if department is not None:
            return Course.objects \
                .filter(base_course__department=department) \
                .select_related('base_course')
        elif department is not None and semester is not None:
            return Course.objects \
                .filter(base_course__department=department,
                        base_course__semester=semester) \
                .select_related('base_course')

        # TODO: When user department is done, change this line of code
        return Course.objects.all().select_related('base_course')

    @action(detail=False, methods=['GET', 'PUT'])
    def my_courses(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        if request.method == 'GET':
            courses = MyCourseSerializer(student.courses.all(), many=True)
            return Response(courses.data)
        elif request.method == 'PUT':
            serializer = AddCourseSerializer(data=request.data, context={'user_id': request.user.id})
            serializer.is_valid(raise_exception=True)
            serializer.save(student=student)
            return Response(status=201)

    @action(detail=False, methods=['GET'])
    def my_exams(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        courses = student.courses.all()
        exams = []
        for course in courses:
            for exam in course.exam_times.all():
                exams.append(exam)
        serializer = CourseExamTimeSerializer(exams, many=True)
        return Response(serializer.data)
