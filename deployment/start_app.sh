#!/bin/bash
source /katyusha_env/bin/activate
cd /app

echo "----- Collect static files ------ "
python manage.py collectstatic --noinput

echo "-----------Apply migration--------- "
python manage.py makemigrations
python manage.py migrate

echo "------ Run initial commands ------"
python manage.py populate_university_database golestan_courses.xlsx
python manage.py fix_teachers_name
python manage.py delete_additional_departments
python manage.py add_profile_to_existing_entities
python manage.py add_initial_tweets

echo "-----------Run gunicorn--------- "
gunicorn -b :8000 core.wsgi:application