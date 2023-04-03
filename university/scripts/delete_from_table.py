from get_data import get_data_from_course_time, get_data_from_exam_time


def delete_from_course_time(data):
    class_times = get_data_from_course_time(data=data)
    if class_times:
        class_times._raw_delete(class_times.db)


def delete_from_exam_time(data):
    exams = get_data_from_exam_time(data=data)
    if exams:
        exams._raw_delete(exams.db)
