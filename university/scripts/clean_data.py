def determine_presentation_type(presentation_type):
    if presentation_type == 'عادي':
        return 'N'
    elif presentation_type == 'الکترونيکي':
        return 'E'
    return 'B'


def determine_sex(sex):
    if sex == 'مختلط':
        return 'B'
    elif sex == 'مرد':
        return 'M'
    return 'F'


def get_time(presentation_time_detail):
    presentation_time = presentation_time_detail.split('-')
    return presentation_time[0], presentation_time[1]


def find_presentation_detail(presentation_detail):
    if presentation_detail[2] == 'شنبه':
        if presentation_detail[1] == 'یک':
            day = 2
        else:
            day = 4
        start_time, end_time = get_time(presentation_detail[3])
        place = str.join(' ', presentation_detail[5:])
    else:
        if presentation_detail[1] == 'شنبه':
            day = 1
        elif presentation_detail[1] == 'دوشنبه':
            day = 3
        else:
            day = 5
        start_time, end_time = get_time(presentation_detail[2])
        place = str.join(' ', presentation_detail[4:])
    return day, start_time, end_time, place


def get_course_code(entry):
    course_number = entry.split('_')[0]
    course_gp = entry.split('_')[1]
    return course_number, course_gp


def determine_guest_able(entry):
    return True if entry == 'بله' else False


def prepare_data_for_course_time_place(entry):
    return entry.split('،')
