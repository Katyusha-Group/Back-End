CURRENT_SEMESTER = 4012
GOLESTAN_EXCEL_FILE_NAME = 'golestan_courses'
NEW_GOLESTAN_EXCEL_FILE_NAME = 'new_golestan_courses'
ALL_GOLESTAN_EXCEL_FILE = 'all_golestan_courses.xlsx'
ALL_GOLESTAN_COURSES = 'all_golestan_courses'
NEW_GOLESTAN_EXCEL_FILE = 'new_golestan_courses.xlsx'
DATA_DIRECTORY_NAME = 'data'
DATA_DIRECTORY = './data/'
TEACHERS_EXCEL_FILE = 'teachers_info.xlsx'

# columns:
SEMESTER = 'ترم ارائه درس'
DEPARTMENT_ID = 'کد دانشکده درس'
DEPARTMENT_NAME = 'دانشکده درس'
STUDYING_GROUP_ID = 'کد گروه آموزشی درس'
STUDYING_GROUP_NAME = 'گروه آموزشی درس'
COURSE_ID = 'شماره و گروه درس'
COURSE_NAME = 'نام درس'
TOTAL_UNITS = 'کل'
PRACTICAL_UNITS = 'ع'
CAPACITY = 'ظر فیت'
REGISTERED_COUNT = 'ثبت نام شده'
WAITING_COUNT = 'تعداد ليست انتظار'
SEX = 'جنس'
TEACHER = 'نام استاد'
COURSE_TIME_PLACE = 'زمان و مکان ارائه'
EXAM_TIME_PLACE = 'زمان و مکان امتحان'
REGISTRATION_LIMIT = 'محدودیت اخذ'
PRESENTATION_TYPE = 'نحوه ارائه درس'
EMERGENCY_DELETION = 'امکان حذف اضطراری'
GUEST_ABLE = 'امکان اخذ توسط مهمان'
DESCRIPTION = 'توضیحات'
ALLOWED_DEPARTMENTS = 'محدودیت دانشکده ها'
REGISTERED_COUNT_NOTIFICATION = 'تعداد ثبت نام شده'
WAITING_COUNT_NOTIFICATION = 'تعداد لیست انتظار'
TEACHER_NOTIFICATION = 'استاد'

# days:
SAT = 'شنبه'
SUN = 'یک شنبه'
MON = 'دوشنبه'
TUE = 'سه شنبه'
WED = 'چهارشنبه'

# sex choices:
MAN = 'مرد'
WOMAN = 'زن'
BOTH_SEX = 'مختلط'

# presentation type choices:
NORMAL = 'عادی'
ELECTRONIC = 'الکترونیکی'
BOTH_PRESENTATION_TYPE = 'عادی-نوری'
ARCHIVE = 'آرشیو'

# yes no
YES = 'بله'
NO = 'خیر'

# persian numbers
PERSIAN_ONE = 'یک'

# related number of each day
SAT_NUMBER = 0
SUN_NUMBER = 1
MON_NUMBER = 2
TUE_NUMBER = 3
WED_NUMBER = 4

# General Departments
GENERAL_DEPARTMENTS = [
    14,
    16,
    26,
    27,
    28,
    90,
]

course_field_mapper_fa_to_en = {
    CAPACITY: 'capacity',
    REGISTERED_COUNT: 'registered_count',
    WAITING_COUNT: 'waiting_count',
    SEX: 'sex',
    TEACHER: 'teacher_id',
    REGISTRATION_LIMIT: 'registration_limit',
    PRESENTATION_TYPE: 'presentation_type',
    GUEST_ABLE: 'guest_able',
    DESCRIPTION: 'description',
    ALLOWED_DEPARTMENTS: 'AllowedDepartment',
    EXAM_TIME_PLACE: 'ExamTimePlace',
    COURSE_TIME_PLACE: 'CourseTimePlace',
}

course_field_mapper_en_to_fa_notification = {
    'capacity': CAPACITY,
    'registered_count': REGISTERED_COUNT_NOTIFICATION,
    'waiting_count': WAITING_COUNT_NOTIFICATION,
    'sex': SEX,
    'teacher_id': TEACHER_NOTIFICATION,
    'registration_limit': REGISTRATION_LIMIT,
    'presentation_type': PRESENTATION_TYPE,
    'guest_able': GUEST_ABLE,
    'description': DESCRIPTION,
    'AllowedDepartment': ALLOWED_DEPARTMENTS,
    'ExamTimePlace': EXAM_TIME_PLACE,
    'CourseTimePlace': COURSE_TIME_PLACE,
}

day_mapper = {
    SAT_NUMBER: SAT,
    SUN_NUMBER: SUN,
    MON_NUMBER: MON,
    TUE_NUMBER: TUE,
    WED_NUMBER: WED,
}
