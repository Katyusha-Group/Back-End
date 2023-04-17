from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from university.models import Course, Department, Semester, ExamTimePlace
from university.serializers import DepartmentSerializer, SemesterSerializer, SimpleCourseSerializer, \
    ModifyMyCourseSerializer, CourseExamTimeSerializer, CourseSerializer
from university.scripts import app_variables


class DepartmentViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        user = get_user_model().objects.get(id=user_id)
        return Department.objects.filter(
            department_number__in=app_variables.GENERAL_DEPARTMENTS + [
                user.department.department_number]).prefetch_related('base_courses__courses')


class SemesterViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = SemesterSerializer

    def get_queryset(self):
        return Semester.objects.all()


class CourseViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'head', 'options']
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == 'my_courses' and self.request.method == 'PUT':
            return ModifyMyCourseSerializer
        elif self.action == 'my_courses' and self.request.method == 'GET':
            return SimpleCourseSerializer
        elif self.action == 'my_exams' and self.request.method == 'GET':
            return CourseExamTimeSerializer
        return CourseSerializer

    def get_queryset(self):
        base_course = self.request.query_params.get('course_number', None)
        user_id = self.request.user.id
        user = get_user_model().objects.get(id=user_id)
        try:
            base_course = int(base_course)
            courses = (Course.objects.filter(Q(sex=user.gender) | Q(sex='B'))
                       .filter(base_course=base_course))
            if not courses.exists():
                raise ValidationError(detail='No course with this course_number in database.')
            else:
                return courses.prefetch_related('teacher', 'course_times', 'exam_times', 'base_course').all()
        except TypeError:
            if self.action != 'my_exams' and self.action != 'my_courses':
                raise ValidationError(detail='Enter course_number as query string in the url.')

    @action(detail=False, methods=['GET', 'PUT'])
    def my_courses(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        if request.method == 'GET':
            courses = SimpleCourseSerializer(
                (student.courses.prefetch_related('teacher', 'course_times', 'exam_times', 'base_course').all()),
                many=True
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
