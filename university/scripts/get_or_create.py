from university.scripts import clean_data
from university.models import BaseCourse, Teacher, Department, Semester, CourseStudyingGP, Course, ExamTimePlace, \
    CourseTimePlace


def get_base_course(**kwargs):
    return BaseCourse.objects.filter(course_number=kwargs['course_number'], semester=kwargs['semester']).first()


def get_department(**kwargs):
    return Department.objects.filter(department_number=kwargs['department_number']).first()


def get_semester(**kwargs):
    return Semester.objects.filter(year=kwargs['year']).first()


def get_course_studying_gp(**kwargs):
    return CourseStudyingGP.objects.filter(year=kwargs['name']).first()


def get_course(**kwargs):
    course_number, class_gp = clean_data.get_course_code(entry=kwargs['course_code'])
    return Course.objects.filter(base_course_id=course_number, class_gp=class_gp,
                                   semester_id=kwargs['semester']).first()
# def create_base_course(**kwargs):
#     course_number = clean_data.get_course_code(kwargs['course_code'])[0]
#     emergency_deletion = clean_data.determine_true_false(kwargs['emergency_deletion'])
#     course_studying_gp = get_course_studying_gp(name=kwargs['course_studying_name'])
#     return BaseCourse.objects.create(course_number=course_number, course_studying_gp_id=course_studying_gp,
#                                      emergency_deletion=emergency_deletion, total_unit=kwargs['total_unit'],
#                                      practical_unit=kwargs['practical_unit'], semester_id=kwargs['semester_id'],
#                                      name=kwargs['name'], department_id=kwargs['department_id'])
#
#
# def create_course(**kwargs):
#     guest_able = clean_data.determine_true_false(kwargs['guest_able'])
#     course_number, class_gp = clean_data.get_course_code(kwargs['course_code'])
#     sex = clean_data.determine_sex(kwargs['sex'])
#     presentation_type = clean_data.determine_presentation_type(kwargs['presentation_type'])
#     teacher = get_or_create_teacher(name=kwargs['name'])
#     return Course.objects.create(base_course_id=course_number, presentation_type=presentation_type,
#                                  teacher=teacher, sex=sex, class_gp=class_gp, guest_able=guest_able,
#                                  capacity=kwargs['capacity'], waiting_count=kwargs['waiting_count'],
#                                  description=kwargs['description'], registered_count=kwargs['registered_count'],
#                                  registration_limit=kwargs['registration_limit'])
#
#
# def create_course_time_place(**kwargs):
#     for presentation_detail in kwargs['data']:
#         day, start_time, end_time, place = clean_data.find_presentation_detail(presentation_detail.split())
#         CourseTimePlace.objects.create(day=day, start_time=start_time, end_time=end_time,
#                                        place=place, course=kwargs['course'])
#
#
# def create_exam_time(**kwargs):
#     exam_data = kwargs['entry'].split()
#     date = str.join('-', exam_data[1].split('/'))
#     exam_start_time, exam_end_time = clean_data.get_time(exam_data[3])
#     ExamTimePlace.objects.create(course=kwargs['course'], start_time=exam_start_time,
#                                  end_time=exam_end_time, date=date)
