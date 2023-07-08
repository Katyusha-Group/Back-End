from django.dispatch import Signal

course_teachers_changed = Signal(providing_args=['course'])
