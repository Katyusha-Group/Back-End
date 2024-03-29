CURRENT_SEMESTER = 4022
GOLESTAN_EXCEL_FILE_NAME = 'golestan_courses'
GOLESTAN_EXCEL_COMPLETE_FILE_NAME = 'golestan_courses.xlsx'
NEW_GOLESTAN_EXCEL_FILE_NAME = 'new_golestan_courses'
ALL_GOLESTAN_EXCEL_FILE = 'all_golestan_courses.xlsx'
ALL_GOLESTAN_COURSES = 'all_golestan_courses'
NEW_GOLESTAN_EXCEL_FILE = 'new_golestan_courses.xlsx'
DATA_DIRECTORY_NAME = 'data'
DATA_DIRECTORY = './data/'
TEACHERS_EXCEL_FILE = 'teachers_info.xlsx'
TEACHERS_EXCEL_NAME = 'teachers_info'

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
WAITING_COUNT = 'تعداد لیست انتظار'
SEX = 'جنس'
TEACHER = 'نام استاد'
COURSE_TIME_PLACE = 'زمان و مکان ارائه'
EXAM_TIME_PLACE = 'زمان و مکان امتحان'
EXAM_TIME_PLACE_NOTIF = 'زمان امتحان'
REGISTRATION_LIMIT = 'محدودیت اخذ'
PRESENTATION_TYPE = 'نحوه ارائه درس'
EMERGENCY_DELETION = 'امکان حذف اضطراری'
GUEST_ABLE = 'امکان اخذ توسط مهمان'
DESCRIPTION = 'توضیحات'
ALLOWED_DEPARTMENTS = 'محدودیت دانشکده ها'

# Equivalent number for each column
SEMESTER_NUMBER = 0
DEPARTMENT_ID_NUMBER = 1
DEPARTMENT_NAME_NUMBER = 2
STUDYING_GROUP_ID_NUMBER = 3
STUDYING_GROUP_NAME_NUMBER = 4
COURSE_ID_NUMBER = 5
COURSE_NAME_NUMBER = 6
TOTAL_UNITS_NUMBER = 7
PRACTICAL_UNITS_NUMBER = 8
CAPACITY_NUMBER = 9
REGISTERED_COUNT_NUMBER = 10
WAITING_COUNT_NUMBER = 11
SEX_NUMBER = 12
TEACHER_NUMBER = 13
COURSE_TIME_PLACE_NUMBER = 14
EXAM_TIME_PLACE_NUMBER = 15
REGISTRATION_LIMIT_NUMBER = 16
PRESENTATION_TYPE_NUMBER = 19
EMERGENCY_DELETION_NUMBER = 21
GUEST_ABLE_NUMBER = 23
DESCRIPTION_NUMBER = 23

# notifications:
REGISTERED_COUNT_NOTIFICATION = 'تعداد ثبت نام شده'
WAITING_COUNT_NOTIFICATION = 'تعداد لیست انتظار'
TEACHER_NOTIFICATION = 'اساتید'
SEX_NOTIFICATION = 'جنسیت'

# notifications types 1 letter
TELEGRAM_NOTIFICATION_TYPE = 'T'
EMAIL_NOTIFICATION_TYPE = 'E'
SMS_NOTIFICATION_TYPE = 'S'

# population modes:
POPULATION_INITIAL = 'initial'
POPULATION_COURSE_CREATE = 'course_create'
POPULATION_COURSE_UPDATE = 'course_update'

# actions:
CREATE = 'C'
UPDATE = 'U'
DELETE = 'D'

# days:
SAT = 'شنبه'
SUN = 'یک شنبه'
MON = 'دوشنبه'
TUE = 'سه شنبه'
WED = 'چهارشنبه'

# sex choices:
MAN_FA = 'مرد'
WOMAN_FA = 'زن'
BOTH_SEX_FA = 'مختلط'
SEX_FA_TO_EN = {
    MAN_FA: 'M',
    WOMAN_FA: 'F',
    BOTH_SEX_FA: 'B',
}
SEX_EN_TO_FA = {
    'M': MAN_FA,
    'F': WOMAN_FA,
    'B': BOTH_SEX_FA
}

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

# Business Rules
INITIAL_WALLET_BALANCE = 20000
TAX = 0.09
EMAIL_PRICE = 1000
SMS_PRICE = 2000
TELEGRAM_PRICE = 1000
MAX_VERIFICATION_TRIES = 5

DOMAIN = 'http://84.32.10.112'

# General Departments
GENERAL_DEPARTMENTS_ID = [
    14,
    16,
    26,
    27,
    28,
    90,
]

ADDITIONAL_DEPARTMENTS_ID = [
    34,  # Pardis
    24,  # Amoozesh Electronic
    25,  # Damavand
]

TEACHERS_NAME_INCORRECT_TO_CORRECT = {
    'آموزشی اساتید گروه': 'اساتید گروه آموزشی',
}

TEACHERS_NAME_INCORRECT_SUBSTRING = [
    'اله',
    'الله',
    'الدین',
    'سا',
    'آ',
]

ADDITIONAL_TEACHERS_NAME = [
    '0 0',
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
    'sex': SEX_NOTIFICATION,
    'teachers': TEACHER_NOTIFICATION,
    'registration_limit': REGISTRATION_LIMIT,
    'presentation_type': PRESENTATION_TYPE,
    'guest_able': GUEST_ABLE,
    'description': DESCRIPTION,
    'allowed_departments': ALLOWED_DEPARTMENTS,
    'exam_time_place': EXAM_TIME_PLACE_NOTIF,
    'course_time_place': COURSE_TIME_PLACE,
}

day_mapper = {
    SAT_NUMBER: SAT,
    SUN_NUMBER: SUN,
    MON_NUMBER: MON,
    TUE_NUMBER: TUE,
    WED_NUMBER: WED,
}

start_time_mapper = {
    7: 0,
    9: 1,
    10: 2,
    13: 3,
    14: 4,
    16: 5,
    17: 6,
    19: 7,
}

action_mapper = {
    CREATE: 'اضافه شد',
    UPDATE: 'ویرایش شد',
    DELETE: 'حذف شد',
}
