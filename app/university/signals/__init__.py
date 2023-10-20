from django.dispatch import Signal

course_teachers_changed = Signal()
# This signal provides following arguments:
# - course: The course that its teachers are changed
