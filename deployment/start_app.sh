#!/bin/bash
source /katyusha_env/bin/activate
cd /app

echo "----- Collect static files ------ "
python manage.py collectstatic --noinput

echo "-----------Apply migration--------- "
python manage.py makemigrations
python manage.py migrate


echo "-----------Run gunicorn--------- "
gunicorn -b :8000 core.wsgi:application