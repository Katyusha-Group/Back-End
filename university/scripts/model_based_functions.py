from core.settings import AUTH_USER_MODEL
from university.models import Course


def get_is_allowed(obj: Course, user: AUTH_USER_MODEL):
    return obj.allowed_departments.filter(department__department_number=user.department.department_number).exists()
