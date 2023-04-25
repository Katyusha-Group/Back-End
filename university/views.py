from django.contrib.auth import get_user_model
from django.db.models import Q, F, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from university.models import Course, Department, Semester, ExamTimePlace, AllowedDepartment
from university.serializers import DepartmentSerializer, SemesterSerializer, ModifyMyCourseSerializer, \
    CourseExamTimeSerializer, CourseSerializer, SummaryCourseSerializer, MyCourseSerializer, \
    CourseGroupSerializer, SimpleBaseCourseSerializer, SimpleDepartmentSerializer
from utils import project_variables


class SignupDepartmentListView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    serializer_class = SimpleDepartmentSerializer

    def get_queryset(self):
        return Department.objects.filter(department_number__gt=0).all()


class DepartmentListView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        return Department.objects.prefetch_related('allowed_departments__course__base_course').all()


class AllDepartmentsListView(ListAPIView):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        all_courses = SimpleBaseCourseSerializer(AllowedDepartment.objects
                                                 .filter(department_id=0, course__sex__in=[request.user.gender, 'B'])
                                                 .annotate(course_number=F('course__base_course__course_number'))
                                                 .annotate(name=F('course__base_course__name'))
                                                 .values('course_number', 'name')
                                                 .annotate(group_count=Count('course_number'))
                                                 .order_by(), many=True)
        return Response(data={'id': '0', 'name': 'تمام دانشکده ها', 'base_courses': all_courses.data})


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
            return MyCourseSerializer
        elif self.action == 'my_exams' and self.request.method == 'GET':
            return CourseExamTimeSerializer
        elif self.action == 'my_summary' and self.request.method == 'GET':
            return SummaryCourseSerializer
        return CourseSerializer

    def get_queryset(self):
        base_course = self.request.query_params.get('course_number', None)
        allowed_only = self.request.query_params.get('allowed_only', False)
        user_id = self.request.user.id
        user = get_user_model().objects.get(id=user_id)
        try:
            base_course = int(base_course)
            if allowed_only:
                courses = (Course.objects.filter(Q(sex=user.gender) | Q(sex='B'))
                           .filter(base_course=base_course, allowed_departments__department=user.department))
            else:
                courses = (Course.objects.filter(Q(sex=user.gender) | Q(sex='B'))
                           .filter(base_course=base_course))
            if not courses.exists():
                raise ValidationError(detail='No course with this course_number in database.')
            else:
                return courses.prefetch_related('teacher', 'course_times', 'exam_times', 'base_course').all()
        except TypeError:
            if self.action != 'my_exams' and self.action != 'my_courses' and self.action != 'my_summary':
                raise ValidationError(detail='Enter course_number as query string in the url.')

    @action(detail=False, methods=['GET', 'PUT'])
    def my_courses(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        if request.method == 'GET':
            courses = MyCourseSerializer(
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


class CourseGroupListView(ModelViewSet):
    serializer_class = CourseGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_course_id = self.kwargs['base_course_id']
        if base_course_id is None:
            raise ValidationError({'detail': 'Enter course_number as query string in the url.'}, )
        elif base_course_id.isdigit() is True:
            base_course_id = int(base_course_id)
        else:
            raise ValidationError({'detail': 'Enter course_number as query number in the url.'}, )

        courses = Course.objects.filter(base_course_id=base_course_id)
        if courses.exists():
            return courses.prefetch_related('teacher', 'course_times', 'exam_times', 'base_course').all()
        else:
            raise ValidationError({'detail': 'No course with this course_number in database.'}, )
