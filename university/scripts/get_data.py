import pandas as pd

from university.models import CourseTimePlace, ExamTimePlace
from university.scripts import get_or_create, clean_data


def get_data_from_course_time(data):
    if data.empty:
        return
    df = pd.DataFrame(data=data, columns=['زمان و مكان ارائه', 'شماره و گروه درس'])
    class_times = []
    for row in df.values:
        course = get_or_create.get_course(course_code=row[1])
        try:
            prep_data = clean_data.prepare_data_for_course_time_place(row[0])
            for pres in prep_data:
                day, start_time, end_time, place = clean_data.find_presentation_detail(pres.split())
                class_times.append(CourseTimePlace(day=day, start_time=start_time, end_time=end_time,
                                                   place=place, course=course))
        except:
            pass
    return class_times


def get_data_from_exam_time(data):
    if data.empty:
        return
    df = pd.DataFrame(data=data, columns=['زمان و مكان امتحان', 'شماره و گروه درس'])
    exams = []
    for row in df.values:
        course = get_or_create.get_course(course_code=row[1])
        try:
            exam_data = row[0].split()
            date = str.join('-', exam_data[1].split('/'))
            exam_start_time, exam_end_time = clean_data.get_time(exam_data[3])
            exams.append(ExamTimePlace(course=course, start_time=exam_start_time,
                                       end_time=exam_end_time, date=date))
        except:
            pass
    return exams
