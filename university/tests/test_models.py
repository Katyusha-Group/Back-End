import pytest
from django.db import models, IntegrityError
from model_bakery import baker
from django.core.exceptions import ValidationError

from core import settings
from university.models import Department, Semester, CourseStudyingGP, BaseCourse, Teacher, Course, ExamTimePlace, \
    AllowedDepartment

pytestmark = pytest.mark.django_db


class TestSemesterModel:
    def test_return_str(self):
        semester = baker.make(Semester, year=4021)

        assert str(semester) == '4021'


class TestDepartmentModel:
    def test_return_str(self):
        department = baker.make(Department, name='Department 1', department_number=1)

        assert str(department) == 'Department 1'

    def test_name_max_length(self):
        department = baker.make(Department, name='Department 1', department_number=1)

        max_length = department._meta.get_field('name').max_length

        assert max_length == 50

    def test_name_unique(self):
        department = baker.make(Department, name='Department 1', department_number=1)

        assert department._meta.get_field('name').unique is True

    def test_department_number_is_positive_small_integer_field(self):
        department = baker.make(Department, name='Department 1', department_number=1)

        assert department._meta.get_field('department_number').get_internal_type() == 'PositiveSmallIntegerField'


class TestCourseStudyingGPModel:
    def test_return_str(self):
        course_studying_gp = baker.make(CourseStudyingGP, gp_id=1, name='GP 1')

        assert str(course_studying_gp) == '1 --- GP 1'

    def test_name_max_length(self):
        course_studying_gp = baker.make(CourseStudyingGP, gp_id=1, name='GP 1')

        max_length = course_studying_gp._meta.get_field('name').max_length

        assert max_length == 50

    def test_name_unique(self):
        course_studying_gp = baker.make(CourseStudyingGP, gp_id=1, name='GP 1')

        assert course_studying_gp._meta.get_field('name').unique is True

    def test_gp_id_is_positive_small_integer_field(self):
        course_studying_gp = baker.make(CourseStudyingGP, gp_id=1, name='GP 1')

        assert course_studying_gp._meta.get_field('gp_id').get_internal_type() == 'PositiveSmallIntegerField'


class TestBaseCourseModel:
    def test_return_str(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert str(base_course) == '1234567 --- Base Course 1'

    def test_name_max_length(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        max_length = base_course._meta.get_field('name').max_length

        assert max_length == 50

    def test_course_number_is_integer_field(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course._meta.get_field('course_number').get_internal_type() == 'IntegerField'

    def test_course_number_is_7_digit(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course._meta.get_field('course_number').validators[0].limit_value == 1000000
        assert base_course._meta.get_field('course_number').validators[1].limit_value == 9999999

    def test_course_number_is_primary_key(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course._meta.get_field('course_number').primary_key is True

    def test_course_number_is_db_index(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course._meta.get_field('course_number').db_index is True

    def test_get_default_profile_name(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course.get_default_profile_name() == 'Base Course 1'

    def test_get_default_profile_username(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course.get_default_profile_username() == 'C_1234567'

    def test_get_default_profile_image(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course.get_default_profile_image() == 'images/profile_pics/course_default.png'

    def test_total_unit_is_float_field(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        assert base_course._meta.get_field('total_unit').get_internal_type() == 'FloatField'

    def test_total_unit_is_positive(self):
        # should raise validation error if negative
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0)

        with pytest.raises(ValidationError):
            base_course.total_unit = -1.5
            base_course.full_clean()

    def test_practical_unit_is_float_field(self):
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', practical_unit=1.5)

        assert base_course._meta.get_field('practical_unit').get_internal_type() == 'FloatField'

    def test_practical_unit_is_positive(self):
        # should raise validation error if negative
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', practical_unit=-1.5)

        with pytest.raises(ValidationError):
            base_course.practical_unit = -1.5
            base_course.full_clean()

    def test_department_relation_is_cascade(self):
        department = baker.make(Department, name='Department 1', department_number=1)
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0,
                                 department=department)

        assert base_course._meta.get_field('department').remote_field.on_delete == models.CASCADE

    def test_course_studying_gp_relation_is_cascade(self):
        course_studying_gp = baker.make(CourseStudyingGP, gp_id=1, name='GP 1')
        base_course = baker.make(BaseCourse, course_number=1234567, name='Base Course 1', total_unit=3.0,
                                 course_studying_gp=course_studying_gp)

        assert base_course._meta.get_field('course_studying_gp').remote_field.on_delete == models.CASCADE


class TestTeacherModel:
    def test_return_str(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert str(teacher) == 'Teacher 1'

    def test_name_max_length(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        max_length = teacher._meta.get_field('name').max_length

        assert max_length == 50

    def test_name_unique(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher._meta.get_field('name').unique is True

    def test_lms_id_is_positive_integer_field(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher._meta.get_field('lms_id').get_internal_type() == 'PositiveIntegerField'

    def test_teacher_image_upload_to(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher._meta.get_field('teacher_image').upload_to == 'images/teachers_image/'

    def test_teacher_image_default(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher._meta.get_field('teacher_image').default == 'images/teachers_image/default.png'

    def test_get_default_profile_name(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher.get_default_profile_name() == 'Teacher 1'

    def test_get_default_profile_username(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher.get_default_profile_username() == 'T_' + str(teacher.id)

    def test_get_default_profile_image(self):
        teacher = baker.make(Teacher, name='Teacher 1')

        assert teacher.get_default_profile_image() == teacher.teacher_image


class TestCourseModel:
    def test_return_str(self, current_semester, base_course_instance):
        course = baker.make(Course, class_gp='01', base_course=base_course_instance, semester=current_semester)

        assert str(course) == '1234567_01'

    def test_class_gp_max_length(self, current_semester, base_course_instance):
        course = baker.make(Course, class_gp='01', semester=current_semester, base_course=base_course_instance)

        max_length = course._meta.get_field('class_gp').max_length

        assert max_length == 2

    def test_capacity_is_positive_small_integer_field(self, current_semester, base_course_instance):
        course = baker.make(Course, capacity=10, semester=current_semester, base_course=base_course_instance)

        assert course._meta.get_field('capacity').get_internal_type() == 'SmallIntegerField'
        assert course.capacity >= 0
        assert course._meta.get_field('capacity').validators[0].limit_value == 0

    def test_registered_count_is_positive_small_integer_field(self, current_semester, base_course_instance):
        course = baker.make(Course, registered_count=5, semester=current_semester, base_course=base_course_instance)

        assert course._meta.get_field('registered_count').get_internal_type() == 'SmallIntegerField'
        assert course.registered_count >= 0
        assert course._meta.get_field('capacity').validators[0].limit_value == 0

    def test_waiting_count_is_positive_small_integer_field(self, current_semester, base_course_instance):
        course = baker.make(Course, waiting_count=3, semester=current_semester, base_course=base_course_instance)

        assert course._meta.get_field('waiting_count').get_internal_type() == 'SmallIntegerField'
        assert course.waiting_count >= 0
        assert course._meta.get_field('capacity').validators[0].limit_value == 0

    def test_guest_able_is_boolean_field(self, current_semester, base_course_instance):
        course = baker.make(Course, guest_able=True, base_course=base_course_instance, semester=current_semester)

        assert course._meta.get_field('guest_able').get_internal_type() == 'BooleanField'

    def test_registration_limit_max_length(self, current_semester, base_course_instance):
        course = baker.make(Course, registration_limit='This is a test registration limit',
                            base_course=base_course_instance, semester=current_semester)

        max_length = course._meta.get_field('registration_limit').max_length

        assert max_length == 2000

    def test_description_max_length(self, current_semester, base_course_instance):
        course = baker.make(Course, description='This is a test description', base_course=base_course_instance,
                            semester=current_semester)

        max_length = course._meta.get_field('description').max_length

        assert max_length == 400

    def test_sex_choices(self, current_semester, base_course_instance):
        course = baker.make(Course, sex='M', base_course=base_course_instance, semester=current_semester)

        assert course._meta.get_field('sex').choices == (('M', 'مرد'), ('F', 'زن'), ('B', 'مختلط'))

    def test_presentation_type_choices(self, current_semester, base_course_instance):
        course = baker.make(Course, presentation_type='N', base_course=base_course_instance, semester=current_semester)

        assert course._meta.get_field('presentation_type').choices == (('N', 'عادی'), ('E', 'الکترونیکی'),
                                                                       ('B', 'عادی-نوری'), ('A', 'آرشیو'))

    def test_base_course_relation_is_cascade(self, current_semester, base_course_instance):
        course = baker.make(Course, base_course=base_course_instance, semester=current_semester)

        assert course._meta.get_field('base_course').remote_field.on_delete == models.CASCADE

    def test_teachers_relation(self, current_semester, base_course_instance):
        teacher1 = baker.make(Teacher, name='Teacher 1')
        teacher2 = baker.make(Teacher, name='Teacher 2')
        course = baker.make(Course, base_course=base_course_instance, semester=current_semester)
        course.teachers.add(teacher1, teacher2)

        assert course.teachers.count() == 2

    def test_students_relation(self, current_semester, base_course_instance):
        course = baker.make(Course, semester=current_semester, base_course=base_course_instance)
        user1 = baker.make(settings.AUTH_USER_MODEL)
        user2 = baker.make(settings.AUTH_USER_MODEL)
        course.students.add(user1, user2)

        assert course.students.count() == 2

    def test_semester_relation_is_cascade(self, current_semester, base_course_instance):
        semester = baker.make(Semester, year=4021)
        course = baker.make(Course, semester=semester, base_course=base_course_instance)

        assert course._meta.get_field('semester').remote_field.on_delete == models.CASCADE

    def test_class_gp_and_base_course_unique_together(self, current_semester, base_course_instance):
        baker.make(Course, class_gp='01', base_course=base_course_instance, semester=current_semester)
        with pytest.raises(IntegrityError):
            baker.make(Course, class_gp='01', base_course=base_course_instance, semester=current_semester)

    def test_capacity_cannot_be_negative(self, current_semester, base_course_instance):
        with pytest.raises(ValidationError):
            baker.make(Course, capacity=-1, semester=current_semester, base_course=base_course_instance).full_clean()

    def test_registered_count_cannot_be_negative(self, current_semester, base_course_instance):
        with pytest.raises(ValidationError):
            baker.make(Course, registered_count=-1, semester=current_semester,
                       base_course=base_course_instance).full_clean()

    def test_waiting_count_cannot_be_negative(self, current_semester, base_course_instance):
        with pytest.raises(ValidationError):
            baker.make(Course, waiting_count=-1, semester=current_semester,
                       base_course=base_course_instance).full_clean()


class TestAllowedDepartment:
    def test_department_is_foreign_key(self, allowed_department_instance):
        assert allowed_department_instance._meta.get_field('department').get_internal_type() == 'ForeignKey'

    def test_department_relation_is_cascade(self, allowed_department_instance):
        assert allowed_department_instance._meta.get_field('department').remote_field.on_delete == models.CASCADE

    def test_course_is_foreign_key(self, allowed_department_instance):
        assert allowed_department_instance._meta.get_field('course').get_internal_type() == 'ForeignKey'

    def test_course_relation_is_cascade(self, allowed_department_instance):
        assert allowed_department_instance._meta.get_field('course').remote_field.on_delete == models.CASCADE

    def test_allowed_department_str(self, allowed_department_instance):
        assert str(allowed_department_instance) == allowed_department_instance.department.name
