def get_user_department(user):
    # Assuming the user has a department attribute in their profile
    return user.department


def sort_departments_by_user_department(departments, user_department):
    return sorted(departments, key=lambda dept: dept != user_department)
