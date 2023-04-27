import json

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
    CourseGroupSerializer, SimpleBaseCourseSerializer, SimpleDepartmentSerializer, AllCourseDepartmentSerializer
from rest_framework.views import APIView
from .models import BaseCourse
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




class CourseStudentCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs ):
        course_id = kwargs['base_course_id']
        if course_id is None:
            raise ValidationError({'detail': 'Enter course_number as query string in the url.'}, )
        else:
            if '_' in course_id:
                course_id_major, group_number = course_id.split('_')
                if course_id_major.isdigit() is True:
                    course_id_major = int(course_id_major)
                else:
                    raise ValidationError({'detail': 'course_number must be in integer format.'})
                if group_number.isdigit() is True:
                    group_number =f'0{int(group_number)}'
                else:
                    raise ValidationError({'detail': 'group_number must be in integer format.'})
            else:
                raise ValidationError({'detail': 'course_number must be in this format: course_number-group_number'})

        courses = Course.objects.filter(base_course_id=course_id_major, class_gp=group_number)
        if courses.exists():
            return Response(data={'count': courses.first().students.count()})
        else:
            raise ValidationError({'detail': 'No course with this course_number in database.'}, )


class AllCourseDepartment(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def time_edit(start, end):
        start = int(((str(start)))[:2])

        if start == 7:
            return 0
        elif start == 9:
            return 1
        elif start == 10:
            return 2
        elif start == 13:
            return 3
        elif start == 15:
            return 4
        elif start == 16:
            return 5
        elif start == 18:
            return 6
        else:
            return 7


    def get(self, request, *args, **kwargs):
        user_department_id = self.request.user.department_id
        all_courses = Course.objects.filter(base_course__department_id=user_department_id)
        courses_list = []
        for course in all_courses:

            if course.course_times.filter(day=0).exists():

                start_time_str = str(course.course_times.all().values_list('start_time', flat=True)[0])
                end_time_str = str(course.course_times.all().values_list('end_time', flat=True)[0])
                time_format = self.time_edit(start_time_str, end_time_str)


                courses_list.append({**AllCourseDepartmentSerializer(course).data, 'day': 0, 'time' : time_format} )



            elif course.course_times.filter(day=1).exists():
                start_time_str = str(course.course_times.all().values_list('start_time', flat=True)[0])
                end_time_str = str(course.course_times.all().values_list('end_time', flat=True)[0])
                time_format = self.time_edit(start_time_str, end_time_str)


                courses_list.append({**AllCourseDepartmentSerializer(course).data, 'day': 1, 'time' : time_format})


            elif course.course_times.filter(day=2).exists():
                start_time_str = str(course.course_times.all().values_list('start_time', flat=True)[0])
                end_time_str = str(course.course_times.all().values_list('end_time', flat=True)[0])
                time_format = self.time_edit(start_time_str, end_time_str)

                courses_list.append({**AllCourseDepartmentSerializer(course).data, 'day':2, 'time' : time_format})


            elif course.course_times.filter(day=3).exists():
                start_time_str = str(course.course_times.all().values_list('start_time', flat=True)[0])
                end_time_str = str(course.course_times.all().values_list('end_time', flat=True)[0])
                time_format = self.time_edit(start_time_str, end_time_str)

                courses_list.append({**AllCourseDepartmentSerializer(course).data, 'day': 3, 'time' : time_format})


            elif course.course_times.filter(day=4).exists():
                start_time_str = str(course.course_times.all().values_list('start_time', flat=True)[0])
                end_time_str = str(course.course_times.all().values_list('end_time', flat=True)[0])
                time_format = self.time_edit(start_time_str, end_time_str)

                courses_list.append({**AllCourseDepartmentSerializer(course).data, 'day': 4, 'time' : time_format})


            elif course.course_times.filter(day=5).exists():
                start_time_str = str(course.course_times.all().values_list('start_time', flat=True)[0])
                end_time_str = str(course.course_times.all().values_list('end_time', flat=True)[0])
                time_format = self.time_edit(start_time_str, end_time_str)

                courses_list.append({**AllCourseDepartmentSerializer(course).data, 'day': 5, 'time' : time_format})


        return Response(courses_list)
