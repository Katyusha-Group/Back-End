from rest_framework import serializers
from accounts.models import *
from university.models import Course, ExamTimePlace, Teacher, CourseTimePlace
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

from university.serializers import SimpleCourseTimePlaceSerializer, SimpleExamTimePlaceSerializer


class SimpleCourseTimePlaceSerializer(serializers.ModelSerializer):
    course_day = serializers.SerializerMethodField(source='day')
    course_start_time = serializers.CharField(source='start_time')
    course_end_time = serializers.CharField(source='end_time')

    def get_course_day(self, obj):
        if obj.day == 0:
            return 'شنبه'
        elif obj.day == 1:
            return 'یکشنبه'
        elif obj.day == 2:
            return 'دوشنبه'
        elif obj.day == 3:
            return 'سه شنبه'
        elif obj.day == 4:
            return 'چهارشنبه'

    class Meta:
        model = CourseTimePlace
        fields = ['course_day', 'course_start_time', 'course_end_time', 'place']


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    from university.models import Department
    def get_department_name(self, obj):
        print(obj.department_id)
        return Department.objects.get(pk=obj.department_id).name
    class Meta:
        model = User
        fields = ('id', 'username', 'department_name' )
        read_only_fields = ('id',)

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['name', ]


class CourseSerializer(serializers.ModelSerializer):
    total_unit = serializers.IntegerField(source='base_course.total_unit', read_only=True)
    practical_unit = serializers.IntegerField(source='base_course.practical_unit', read_only=True)
    emergency_deletion = serializers.BooleanField(source='base_course.emergency_deletion', read_only=True)
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = SimpleCourseTimePlaceSerializer(many=True, read_only=True)
    teacher = TeacherSerializer(read_only=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name', 'class_gp', 'total_unit',
                  'practical_unit', 'capacity', 'registered_count',
                  'waiting_count', 'sex', 'guest_able', 'emergency_deletion',
                  'registration_limit', 'description', 'presentation_type',
                  'teacher', 'exam_times', 'course_times']


class ModifyMyCourseSerializer(serializers.Serializer):
    complete_course_number = serializers.CharField()

    def validate(self, attrs):
        # user_id = self.context['user_id']
        # user = get_user_model().objects.get(id=user_id)
        course_number, class_gp = attrs['complete_course_number'].split('_')
        courses = Course.objects.filter(class_gp=class_gp, base_course_id=course_number)
        if not courses.exists():
            raise serializers.ValidationError(
                detail='No course with the given course number was found.'
            )
        # if not courses.first().base_course.department.name in \
        #        [user.department.name] + project_variables.GENERAL_DEPARTMENTS:
        #     raise serializers.ValidationError(
        #         detail='This course can not be added, due to its department incompatibility with allowed departments',
        #     )
        return attrs

class IsItInDatabaseSerializer(serializers.Serializer):
    hashed_number = serializers.CharField(max_length=10, min_length=10, allow_null=True, allow_blank=True)
    telegram_chat_id = serializers.CharField(max_length=10, min_length=10, allow_null=True, allow_blank=True)
    name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)


class GetChatIderializer(serializers.Serializer):
    email = serializers.EmailField()
