def get_color_intensity_percentage(obj):
    '''
    Color intensity percentage = ((Remaining capacity - Number of people on the waiting list) / (Total capacity + Number of people on the waiting list + (1.2 * Number of people who want to take the course))) * 100
    '''
    if obj.capacity == 0:
        return 100

    print(color_intensity_percentage)
    if color_intensity_percentage <= 0:
        return 0
    return (color_intensity_percentage // 10) * 10 + 10 if color_intensity_percentage < 95 else 100


class ccc:
    capacity = 100
    registered_count = 100
    waiting_count = 0
    students_count = 0

p = ccc

print(get_color_intensity_percentage(p))
