from django.db.models import Count, Q
from rest_framework import serializers

from .models import Department, Semester, Course, ExamTimePlace, CourseTimePlace, Teacher, BaseCourse, AllowedDepartment
from utils import project_variables
from .scripts import model_based_functions
from .scripts.get_or_create import get_course


class SimpleBaseCourseSerializer(serializers.Serializer):
    course_number = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    group_count = serializers.IntegerField(read_only=True)
    allowed_count = serializers.IntegerField(read_only=True)


class SimpleDepartmentSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source='department_number', read_only=True)
    label = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Department
        fields = ['label', 'value']


class DepartmentCourseBasedSerializer(serializers.ModelSerializer):
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
            .annotate(allowed_count=Count('courses__allowed_departments__department'))
            .values('course_number', 'name', 'allowed_count')
            .annotate(group_count=Count('course_number'))
            .order_by('name'))
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
    teacher_image = serializers.SerializerMethodField(read_only=True)

    def get_teacher_image(self, obj: Teacher):
        return project_variables.DOMAIN + obj.teacher_image.url if obj.teacher_image else None

    class Meta:
        model = Teacher
        fields = ['id', 'name', 'teacher_image']


class SimpleExamTimePlaceSerializer(serializers.ModelSerializer):
    exam_start_time = serializers.CharField(source='start_time')
    exam_end_time = serializers.CharField(source='end_time')

    class Meta:
        model = ExamTimePlace
        fields = ['date', 'exam_start_time', 'exam_end_time']


class BaseCourseTimePlaceSerializer(serializers.ModelSerializer):
    course_day = serializers.CharField(source='day')
    course_start_time = serializers.CharField(source='start_time')
    course_end_time = serializers.CharField(source='end_time')

    class Meta:
        model = CourseTimePlace
        fields = ['course_day', 'course_start_time', 'course_end_time', 'place']


class SimpleCourseTimePlaceSerializer(BaseCourseTimePlaceSerializer):
    pass


class CourseTimeSerializerDayRepresentation(BaseCourseTimePlaceSerializer):
    course_time_representation = serializers.SerializerMethodField(read_only=True)

    def get_course_time_representation(self, obj: CourseTimePlace):
        start = int((str(obj.start_time))[:2])
        if start in project_variables.start_time_mapper:
            return project_variables.start_time_mapper[start]
        else:
            return 7

    class Meta:
        model = BaseCourseTimePlaceSerializer.Meta.model
        fields = BaseCourseTimePlaceSerializer.Meta.fields + ['course_time_representation']


class SimpleCourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name',
                  'registered_count', 'capacity']


class ShoppingCourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    teachers = TeacherSerializer(read_only=True, many=True)

    def get_complete_course_number(self, obj: Course):
        return str(obj.base_course.course_number) + '_' + str(obj.class_gp)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name',
                  'registered_count', 'capacity', 'teachers']


class CourseSerializer(serializers.ModelSerializer):
    total_unit = serializers.IntegerField(source='base_course.total_unit', read_only=True)
    practical_unit = serializers.IntegerField(source='base_course.practical_unit', read_only=True)
    emergency_deletion = serializers.BooleanField(source='base_course.emergency_deletion', read_only=True)
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = CourseTimeSerializerDayRepresentation(many=True, read_only=True)
    teachers = TeacherSerializer(read_only=True, many=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    is_allowed = serializers.SerializerMethodField(read_only=True)

    def get_is_allowed(self, obj: Course):
        return model_based_functions.get_is_allowed(obj, self.context['user'])

    def get_complete_course_number(self, obj: Course):
        return model_based_functions.get_complete_course_number(obj)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name', 'class_gp', 'total_unit',
                  'practical_unit', 'capacity', 'registered_count',
                  'waiting_count', 'sex', 'emergency_deletion',
                  'registration_limit', 'description', 'presentation_type',
                  'teachers', 'exam_times', 'course_times', 'is_allowed']


class MyCourseSerializer(serializers.ModelSerializer):
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = CourseTimeSerializerDayRepresentation(many=True, read_only=True)
    teachers = TeacherSerializer(read_only=True, many=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return model_based_functions.get_complete_course_number(obj)

    class Meta:
        model = Course
        fields = ['complete_course_number', 'name', 'capacity',
                  'registered_count', 'waiting_count', 'exam_times',
                  'course_times', 'teachers']


class ModifyMyCourseSerializer(serializers.Serializer):
    complete_course_number = serializers.CharField()

    def validate(self, attrs):
        course_number, class_gp = attrs['complete_course_number'].split('_')
        courses = Course.objects.filter(class_gp=class_gp, base_course_id=course_number)
        if not courses.exists():
            raise serializers.ValidationError(
                detail='No course with the given course number was found.'
            )
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
        return model_based_functions.get_complete_course_number(obj.course)

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


class SimpleTeacherTimeLineSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Teacher
        fields = ['teacher_name']


class CourseWithTeacherTimeLineSerializer(serializers.ModelSerializer):
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    teachers = SimpleTeacherTimeLineSerializer(read_only=True, many=True)

    def get_complete_course_number(self, obj: Course):
        course_number_str = str(obj.base_course.course_number)
        return course_number_str[:2] + '-' + course_number_str[2:4] + '-' + course_number_str[4:7] + '-' + obj.class_gp

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        if 'teachers' in representation:
            teacher_representation = representation.pop('teachers')
            representation['teachers'] = []
            for item in teacher_representation:
                representation['teachers'].append(item['teacher_name'])
        return representation

    class Meta:
        model = Course
        fields = ['semester', 'teachers', 'capacity', 'registered_count', 'complete_course_number']


class CourseWithoutTeacherTimeLineSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='base_course.name', read_only=True)

    def get_complete_course_number(self, obj: Course):
        course_number_str = str(obj.base_course.course_number)
        return course_number_str[:2] + '-' + course_number_str[2:4] + '-' + course_number_str[4:7] + '-' + obj.class_gp

    class Meta:
        model = Course
        fields = ['semester', 'capacity', 'course_name', 'registered_count', ]


class BaseCourseTimeLineSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        print(representation)
        representation['data'] = {}
        if 'courses' in representation:
            courses_representation = representation.pop('courses')
            for sub_item in courses_representation:
                new_data = {}
                for sub_key in sub_item:
                    if sub_key == 'semester' or sub_key == 'teachers':
                        continue
                    if sub_key in new_data:
                        new_data[sub_key].append(sub_item[sub_key])
                    else:
                        new_data[sub_key] = sub_item[sub_key]
                if sub_item['semester'] not in representation['data']:
                    representation['data'][sub_item['semester']] = {}
                for teacher in sub_item['teachers']:
                    if teacher not in representation['data'][sub_item['semester']]:
                        representation['data'][sub_item['semester']][teacher] = {}
                        representation['data'][sub_item['semester']][teacher]['courses'] = []
                    if teacher in representation['data'][sub_item['semester']]:
                        representation['data'][sub_item['semester']][teacher]['courses'].append(new_data)
        DATA_KEY = 'data'
        for semester in representation[DATA_KEY]:
            for teacher in representation[DATA_KEY][semester]:
                representation[DATA_KEY][semester][teacher]['total_capacity'] = sum(
                    [item['capacity'] for item in representation[DATA_KEY][semester][teacher]['courses']]
                )
                representation[DATA_KEY][semester][teacher]['total_registered_count'] = sum(
                    [item['registered_count'] for item in representation[DATA_KEY][semester][teacher]['courses']]
                )
                representation[DATA_KEY][semester][teacher]['popularity'] = \
                    (representation[DATA_KEY][semester][teacher]['total_registered_count'] /
                     representation[DATA_KEY][semester][teacher]['total_capacity'] * 100) // 1
                representation[DATA_KEY][semester][teacher]['total_classes'] = len(
                    representation[DATA_KEY][semester][teacher]['courses'])
        return representation

    courses = CourseWithTeacherTimeLineSerializer(many=True, read_only=True)

    class Meta:
        model = BaseCourse
        fields = ['course_number', 'name', 'courses']


class TeacherTimeLineSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['data'] = {}
        if 'courses' in representation:
            courses_representation = representation.pop('courses')
            for sub_item in courses_representation:
                new_data = {}
                for sub_key in sub_item:
                    if sub_key == 'semester' or sub_key == 'course_name':
                        continue
                    if sub_key in new_data:
                        new_data[sub_key].append(sub_item[sub_key])
                    else:
                        new_data[sub_key] = sub_item[sub_key]
                if sub_item['semester'] not in representation['data']:
                    representation['data'][sub_item['semester']] = {}
                    representation['data'][sub_item['semester']]['courses'] = {}
                if sub_item['course_name'] not in representation['data'][sub_item['semester']]['courses']:
                    representation['data'][sub_item['semester']]['courses'][sub_item['course_name']] = {}
                    representation['data'][sub_item['semester']]['courses'][sub_item['course_name']]['detail'] = []
                representation['data'][sub_item['semester']]['courses'][sub_item['course_name']]['detail'].append(
                    new_data)
        DATA_KEY = 'data'
        for semester in representation[DATA_KEY]:
            for course in representation[DATA_KEY][semester]['courses']:
                representation[DATA_KEY][semester]['courses'][course]['course_total_capacity'] = sum(
                    [item['capacity'] for item in representation[DATA_KEY][semester]['courses'][course]['detail']]
                )
                representation[DATA_KEY][semester]['courses'][course]['course_total_registered_count'] = sum(
                    [item['registered_count'] for item in
                     representation[DATA_KEY][semester]['courses'][course]['detail']]
                )
                representation[DATA_KEY][semester]['courses'][course]['course_popularity'] = \
                    (representation[DATA_KEY][semester]['courses'][course]['course_total_registered_count'] /
                     representation[DATA_KEY][semester]['courses'][course]['course_total_capacity'] * 100) // 1
                representation[DATA_KEY][semester]['courses'][course]['course_total_classes'] = len(
                    representation[DATA_KEY][semester]['courses'][course])
        return representation

    courses = CourseWithoutTeacherTimeLineSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['name', 'courses']


class StudentCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class SimpleAllowedDepartmentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = AllowedDepartment
        fields = ['department_name']


class AllCourseDepartmentSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        if 'allowed_departments' in representation:
            allowed_departments = representation.pop('allowed_departments')
            representation['allowed_departments'] = []
            for key in allowed_departments:
                representation['allowed_departments'].append(key['department_name'])
        return representation

    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    course_times = CourseTimeSerializerDayRepresentation(many=True, read_only=True)
    teachers = TeacherSerializer(read_only=True, many=True)
    color_intensity_percentage = serializers.SerializerMethodField(read_only=True)
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    is_allowed = serializers.SerializerMethodField(read_only=True)
    allowed_departments = SimpleAllowedDepartmentSerializer(many=True, read_only=True)

    def get_is_allowed(self, obj: Course):
        return model_based_functions.get_is_allowed(obj, self.context['user'])

    def get_color_intensity_percentage(self, obj: Course):
        return model_based_functions.get_color_intensity_percentage(obj)

    def get_complete_course_number(self, obj: Course):
        return model_based_functions.get_complete_course_number(obj)

    class Meta:
        model = Course
        fields = ('name', 'id', 'is_allowed', 'class_gp', 'capacity', 'complete_course_number',
                  'registered_count', 'waiting_count', 'guest_able', 'course_times', 'color_intensity_percentage',
                  'registration_limit', 'description', 'sex', 'presentation_type', 'base_course', 'teachers',
                  'exam_times', 'allowed_departments')


class CourseGroupSerializer(serializers.ModelSerializer):
    total_unit = serializers.IntegerField(source='base_course.total_unit', read_only=True)
    practical_unit = serializers.IntegerField(source='base_course.practical_unit', read_only=True)
    exam_times = SimpleExamTimePlaceSerializer(many=True, read_only=True)
    course_times = CourseTimeSerializerDayRepresentation(many=True, read_only=True)
    teachers = TeacherSerializer(read_only=True, many=True)
    name = serializers.CharField(source='base_course.name', read_only=True)
    complete_course_number = serializers.SerializerMethodField(read_only=True)
    group_number = serializers.CharField(source='class_gp', read_only=True)
    added_to_calendar_count = serializers.SerializerMethodField(read_only=True)
    color_intensity_percentage = serializers.SerializerMethodField(read_only=True)
    color_code = serializers.SerializerMethodField(read_only=True)

    def get_complete_course_number(self, obj: Course):
        return model_based_functions.get_complete_course_number(obj)

    def get_color_intensity_percentage(self, obj):
        return model_based_functions.get_color_intensity_percentage(obj)

    def get_added_to_calendar_count(self, obj: Course):
        return obj.students.count()

    def get_color_code(self, obj):
        return 'None'

    class Meta:
        model = Course
        fields = ['complete_course_number', 'added_to_calendar_count', 'name', 'base_course_id', 'group_number',
                  'capacity', 'registered_count', 'waiting_count', 'exam_times',
                  'course_times', 'teachers', 'color_intensity_percentage', 'color_code',
                  'total_unit', 'practical_unit', 'sex']
