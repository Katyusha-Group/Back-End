from django.db.models import Count, Q
from rest_framework import serializers

from .models import Department, Semester, Course, ExamTimePlace, CourseTimePlace, Teacher, BaseCourse
from utils import project_variables
from .scripts.get_or_create import get_course


class SimpleBaseCourseSerializer(serializers.Serializer):
    course_number = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    group_count = serializers.IntegerField(read_only=True)


class SimpleDepartmentSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source='department_number', read_only=True)
    label = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Department
        fields = ['label', 'value']


class DepartmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='department_number', read_only=True)
    base_courses = serializers.SerializerMethodField(read_only=True)

    def get_base_courses(self, obj: Department):
        user = self.context.get('user')
        if self.context['api'] == 'allowed':
            courses = BaseCourse.objects.filter(
                Q(courses__allowed_departments__department=user.department) & Q(department__exact=obj) & Q(
                    courses__semester_id__exact=project_variables.CURRENT_SEMESTER) & Q(
                    courses__sex__in=[user.gender, 'B']))
        else:
            courses = BaseCourse.objects.filter(
                Q(department__exact=obj) & Q(courses__semester_id__exact=project_variables.CURRENT_SEMESTER) & Q(
                    courses__sex__in=[user.gender, 'B']))
        courses = (
            courses
            .values('course_number', 'name')
            .annotate(group_count=Count('course_number'))
            .order_by())
        serializer = SimpleBaseCourseSerializer(data=courses, many=True, context=self.context)
        serializer.is_valid()
        return serializer.data

    class Meta:
        model = Department
        fields = ['id', 'name', 'base_courses']


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['year']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'teacher_image']


class SimpleExamTimePlaceSerializer(serializers.ModelSerializer):
    exam_start_time = serializers.CharField(source='start_time')
    exam_end_time = serializers.CharField(source='end_time')

    class Meta:
        model = ExamTimePlace
        fields = ['date', 'exam_start_time', 'exam_end_time']


class SimpleCourseTimePlaceSerializer(serializers.ModelSerializer):
    course_day = serializers.CharField(source='day')
    course_start_time = serializers.CharField(source='start_time')
    course_end_time = serializers.CharField(source='end_time')

    class Meta:
        model = CourseTimePlace
        fields = ['course_day', 'course_start_time', 'course_end_time', 'place']


class SimpleCourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name',
                  'registered_count', 'capacity']


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


class MyCourseSerializer(serializers.ModelSerializer):
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = SimpleCourseTimePlaceSerializer(many=True, read_only=True)
    teacher = TeacherSerializer(read_only=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name', 'capacity',
                  'registered_count', 'waiting_count', 'exam_times',
                  'course_times', 'teacher']


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

    def save(self, **kwargs):
        user = kwargs['student']
        course = get_course(course_code=self.validated_data['complete_course_number'],
                            semester=project_variables.CURRENT_SEMESTER)
        if course in user.courses.all():
            user.courses.remove(course)
            created = False
        else:
            user.courses.add(course)
            created = True
        course.save()
        user.save()
        return course, created


class CourseExamTimeSerializer(serializers.ModelSerializer):
    complete_course_number = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: ExamTimePlace):
        return str(obj.course.base_course.course_number) + '_' + obj.course.class_gp

    class Meta:
        model = ExamTimePlace
        fields = ['complete_course_number', 'date', 'start_time', 'end_time']


class SummaryCourseSerializer(serializers.ModelSerializer):
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    total_unit = serializers.IntegerField(source='base_course.total_unit', read_only=True)

    def get_complete_course_number(self, obj: Course):
        course_number_str = str(obj.base_course.course_number)
        return course_number_str[:2] + '-' + course_number_str[2:4] + '-' + course_number_str[4:7] + '-' + obj.class_gp

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name', 'total_unit']


class TeacherTimeLineSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Teacher
        fields = ['teacher_name']


class CourseTimeLineSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        if 'teacher' in representation:
            teacher_representation = representation.pop('teacher')
            for sub_key in teacher_representation:
                representation[sub_key] = teacher_representation[sub_key]
        return representation

    teacher = TeacherTimeLineSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['semester', 'teacher', 'capacity', 'registered_count']


class TimelineSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['data'] = {}
        if 'courses' in representation:
            courses_representation = representation.pop('courses')
            for sub_item in courses_representation:
                new_data = {}
                for sub_key in sub_item:
                    if sub_key == 'semester':
                        continue
                    if sub_key in new_data:
                        new_data[sub_key].append(sub_item[sub_key])
                    else:
                        new_data[sub_key] = sub_item[sub_key]
                if sub_item['semester'] in representation['data']:
                    representation['data'][sub_item['semester']].append(new_data)
                else:
                    representation['data'][sub_item['semester']] = [new_data]
        return representation

    courses = CourseTimeLineSerializer(many=True, read_only=True)

    class Meta:
        model = BaseCourse
        fields = ['course_number', 'name', 'courses']


class CourseGroupSerializer(serializers.ModelSerializer):
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = SimpleCourseTimePlaceSerializer(many=True, read_only=True)
    teacher = TeacherSerializer(read_only=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    group_number = serializers.CharField(source='class_gp', read_only=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name', 'base_course_id', 'group_number', 'capacity',
                  'registered_count', 'waiting_count', 'exam_times',
                  'course_times', 'teacher']


class StudentCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class AllCourseDepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='base_course.name', read_only=True)

    class Meta:
        model = BaseCourse
        fields = ['name']


class AllCourseDepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    course_times = SimpleCourseTimePlaceSerializer(many=True, read_only=True)
    teacher = TeacherSerializer(read_only=True)
    color_intensity_percentage = serializers.SerializerMethodField(read_only=True)
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)

    def get_color_intensity_percentage(self, obj):
        '''
        Color intensity percentage = ((Remaining capacity - Number of people on the waiting list) / (Total capacity + Number of people on the waiting list + (1.2 * Number of people who want to take the course))) * 100
        '''

        color_intensity_percentage = ((((obj.capacity - obj.registered_count) - obj.waiting_count) * 100) / (
                obj.capacity + obj.waiting_count + (1.2 * self.get_added_to_calendar_count(obj))))
        return (color_intensity_percentage // 10) * 10 + 10 if color_intensity_percentage < 95 else 100

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    def get_added_to_calendar_count(self, obj):
        base_course_id = self.get_complete_course_number(obj)
        course_id_major, group_number = base_course_id.split('_')
        courses = Course.objects.filter(base_course_id=course_id_major, class_gp=group_number)
        return courses.first().students.count()

    class Meta:
        model = Course
        fields = ('name', 'id', 'class_gp', 'capacity', 'complete_course_number',
                  'registered_count', 'waiting_count', 'guest_able', 'course_times', 'color_intensity_percentage',
                  'registration_limit', 'description', 'sex', 'presentation_type', 'base_course', 'teacher',
                  'exam_times')


class CourseGroupSerializer(serializers.ModelSerializer):
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = SimpleCourseTimePlaceSerializer(many=True, read_only=True)
    teacher = TeacherSerializer(read_only=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    group_number = serializers.CharField(source='class_gp', read_only=True)
    added_to_calendar_count = serializers.SerializerMethodField(read_only=True)
    color_intensity_percentage = serializers.SerializerMethodField(read_only=True)
    color_code = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'added_to_calendar_count', 'name', 'base_course_id', 'group_number',
                  'capacity',
                  'registered_count', 'waiting_count', 'exam_times',
                  'course_times', 'teacher', 'color_intensity_percentage', 'color_code']

    def get_color_intensity_percentage(self, obj):
        '''
        Color intensity percentage = ((Remaining capacity - Number of people on the waiting list) / (Total capacity + Number of people on the waiting list + (1.2 * Number of people who want to take the course))) * 100
        '''

        color_intensity_percentage = ((((obj.capacity - obj.registered_count) - obj.waiting_count) * 100) / (
                obj.capacity + obj.waiting_count + (1.2 * self.get_added_to_calendar_count(obj))))
        return (color_intensity_percentage // 10) * 10 + 10 if color_intensity_percentage < 95 else 100

    def get_added_to_calendar_count(self, obj):
        base_course_id = self.get_complete_course_number(obj)
        course_id_major, group_number = base_course_id.split('_')
        courses = Course.objects.filter(base_course_id=course_id_major, class_gp=group_number)
        return courses.first().students.count()

    def get_color_code(self, obj):
        return 'None'
