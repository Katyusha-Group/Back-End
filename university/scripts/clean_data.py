from utils import project_variables


def determine_presentation_type(presentation_type):
    if presentation_type == project_variables.NORMAL:
        return 'N'
    elif presentation_type == project_variables.ELECTRONIC:
        return 'E'
    elif presentation_type == project_variables.ARCHIVE:
        return 'A'
    return 'B'


def determine_sex(sex):
    if sex == project_variables.BOTH_SEX:
        return 'B'
    elif sex == project_variables.MAN:
        return 'M'
    return 'F'


def get_time(presentation_time_detail):
    presentation_time = presentation_time_detail.split('-')
    return presentation_time[0], presentation_time[1]


def find_presentation_detail(presentation_detail):
    if presentation_detail[2] == project_variables.SAT:
        if presentation_detail[1] == project_variables.PERSIAN_ONE:
            day = 1
        else:
            day = 3
        start_time, end_time = get_time(presentation_detail[3])
        place = str.join(' ', presentation_detail[5:])
    else:
        if presentation_detail[1] == project_variables.SAT:
            day = 0
        elif presentation_detail[1] == project_variables.MON:
            day = 2
        else:
            day = 4
        start_time, end_time = get_time(presentation_detail[2])
        place = str.join(' ', presentation_detail[4:])
    return day, start_time, end_time, place


def get_course_code(entry):
    course_number = entry.split('_')[0]
    course_gp = entry.split('_')[1]
    return course_number, course_gp


def determine_true_false(entry):
    return True if entry == project_variables.YES else False


def prepare_data_for_course_time_place(entry):
    return entry.split('،')
