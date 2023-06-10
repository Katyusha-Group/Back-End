from django.conf import settings
import jwt
from django.contrib.auth import get_user_model

from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ViewSet, ModelViewSet
from accounts.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import hashlib



class UserViewSet(ViewSet):
    permission_classes = []
    def get_song(self, request, song_id):
        song = get_object_or_404(User, id=song_id)
        serializer = UserSerializer(song)
        return Response({'status': 'OK', 'inf': serializer.data,})

    def get_courses_on_calendar(self, request, user_id):
        student = get_user_model().objects.get(id=user_id)
        if request.method == 'GET':
            courses = CourseSerializer(
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



class CourseViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'head', 'options']
    permission_classes = []
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == 'my_courses' and self.request.method == 'PUT':
            return ModifyMyCourseSerializer
        # elif self.action == 'my_exams' and self.request.method == 'GET':
        #     return CourseExamTimeSerializer
        # elif self.action == 'my_summary' and self.request.method == 'GET':
        #     return SummaryCourseSerializer
        # return CourseSerializer

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
                raise ValidationError(detail='No course with this course_number exists in database.')
            else:
                return courses.prefetch_related('teacher', 'course_times', 'exam_times', 'base_course').all()
        except TypeError:
            if self.action != 'my_exams' and self.action != 'my_courses' and self.action != 'my_summary':
                raise ValidationError(detail='Enter course_number as query string in the url.')

    @action(detail=False, methods=['GET', 'PUT'])
    def my_courses(self, request):
        student = get_user_model().objects.get(id=request.user.id)
        if request.method == 'GET':
            courses = CourseSerializer(
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

    # @action(detail=False, methods=['GET'])
    # def my_exams(self, request):
    #     student = get_user_model().objects.get(id=request.user.id)
    #     exam_ids = student.courses.prefetch_related('exam_times', 'base_course').values('exam_times')
    #     exams = ExamTimePlace.objects.filter(pk__in=exam_ids)
    #     serializer = CourseExamTimeSerializer(exams, many=True)
    #     return Response(data=serializer.data)
    #
    # @action(detail=False, methods=['GET'])
    # def my_summary(self, request):
    #     user = get_user_model().objects.get(id=request.user.id)
    #     course_data = user.courses.prefetch_related('base_course')
    #     courses = SummaryCourseSerializer(
    #         course_data,
    #         many=True,
    #         context={'user': user}
    #     )
    #     return Response(status=status.HTTP_200_OK,
    #                     data={'unit_count': sum([course.base_course.total_unit for course in course_data]),
    #                           'data': courses.data})

class TelegramLink(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id

        number = str(user_id).encode('utf-8')

        # Hash the number
        hash_object = hashlib.sha256(number)
        hashed_number = hash_object.hexdigest()

        from .models import User_telegram
        if User_telegram.objects.filter(user_id=user_id).exists():
            return Response({'status': 'OK', 'link telegram': f"https://t.me/katyushaiust_bot?start={hashed_number[:10]}"})
        else:

            user_telegram = User_telegram.objects.create(
                hashed_number=hashed_number[:10],
                user_id=user_id,
            )

        # Take the first 10 characters of the hash
        return Response({'status': 'OK', 'link telegram': f"https://t.me/katyushaiust_bot?start={hashed_number[:10]}"})

