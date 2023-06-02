from university.models import Course


def get_color_intensity_percentage(obj: Course):
    '''
    Color intensity percentage = ((Remaining capacity - Number of people on the waiting list) / (Total capacity + Number of people on the waiting list + (1.2 * Number of people who want to take the course))) * 100
    '''
    if obj.capacity == 0:
        return 100

    color_intensity_percentage = ((((obj.capacity - obj.registered_count) - obj.waiting_count) * 100) / (
            obj.capacity + obj.waiting_count + (1.2 * obj.students.count())))
    if color_intensity_percentage < 0:
        return 0
    return (color_intensity_percentage // 10) * 10 + 10 if color_intensity_percentage < 95 else 100
