from . import clean_data
from ..models import BaseCourse, Teacher, Department, Semester, CourseStudyingGP, Course, ExamTimePlace, CourseTimePlace


def get_or_create_base_course(**kwargs):
    base_course = BaseCourse.objects.filter(course_number=kwargs['course_number']).first()
    if base_course:
        return base_course, True
    else:
        base_course = BaseCourse.objects.create(course_number=kwargs['course_number'],
                                                course_studying_gp=kwargs['course_studying_gp'],
                                                semester=kwargs['semester'],
                                                department=kwargs['department'],
                                                total_unit=kwargs['total_unit'],
                                                practical_unit=kwargs['practical_unit'],
                                                name=kwargs['name'],
                                                emergency_deletion=kwargs['emergency_deletion'])
        return base_course, False


def get_or_create_teacher(**kwargs):
    teacher = Teacher.objects.filter(name=kwargs['name']).first()
    if teacher:
        return teacher, True
    else:
        teacher = Teacher.objects.create(name=kwargs['name'])
        return teacher, False


def get_or_create_department(**kwargs):
    department = Department.objects.filter(department_number=kwargs['department_number']).first()
    if department:
        return department, True
    else:
        department = Department.objects.create(department_number=kwargs['department_number'],
                                               name=kwargs['name'])
        return department, False


def get_or_create_semester(**kwargs):
    semester = Semester.objects.filter(year=kwargs['year']).first()
    if semester:
        return semester, True
    else:
        semester = Semester.objects.create(year=kwargs['year'])
        return semester, False


def get_or_create_course_studying_gp(**kwargs):
    course_studying_gp = CourseStudyingGP.objects.filter(year=kwargs['year']).first()
    if course_studying_gp:
        return course_studying_gp, True
    else:
        course_studying_gp = CourseStudyingGP.objects.create(name=kwargs['name'],
                                                             gp_id=kwargs['gp_id'])
        return course_studying_gp, False


def get_or_create_course(**kwargs):
    course = Course.objects.filter(base_course=kwargs['base_course'], class_gp=kwargs['class_gp']).first()
    if course:
        return course, True
    else:
        course = Course.objects.create(base_course=kwargs['base_course'],
                                       registration_limit=kwargs['registration_limit'],
                                       capacity=kwargs['capacity'],
                                       guest_able=kwargs['guest_able'],
                                       description=kwargs['description'],
                                       waiting_count=kwargs['waiting_count'],
                                       class_gp=kwargs['class_gp'],
                                       registered_count=kwargs['registered_count'],
                                       teacher=kwargs['teacher'],
                                       presentation_type=kwargs['presentation_type'],
                                       sex=kwargs['sex'])
        return course, False


def create_course_time_place(**kwargs):
    for presentation_detail in kwargs['data']:
        day, start_time, end_time, place = clean_data.find_presentation_detail(presentation_detail.split())
        CourseTimePlace.objects.create(day=day, start_time=start_time, end_time=end_time,
                                       place=place, course=kwargs['course'])


def create_exam_time(**kwargs):
    exam_data = kwargs['entry'].split()
    date = str.join('-', exam_data[1].split('/'))
    exam_start_time, exam_end_time = clean_data.get_time(exam_data[3])
    ExamTimePlace.objects.create(course=kwargs['course'], start_time=exam_start_time,
                                 end_time=exam_end_time, date=date)
