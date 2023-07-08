from university.models import Semester


def add_all_semesters_to_timeline(queryset, serializer):
    semesters = Semester.objects.all().reverse()[:10]
    data = []
    for sem in semesters:
        if not queryset.filter(courses__semester=sem).exists():
            data.append({sem.year: None})
    for sem in serializer.data[0]['data']:
        data.append({sem: serializer.data[0]['data'][sem]})
    data.sort(key=lambda x: list(x.keys())[0])
    serializer.data[0]['data'] = data
    return serializer
