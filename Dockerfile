FROM python:3.9.0-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies necessary for psycopg2
#RUN apt-get update && apt-get install -y libpq-dev gcc
#RUN apt-get update && apt-get install -y netcat
# Copy only the Pipfile and Pipfile.lock first to leverage Docker caching
COPY requirements.txt /app/


# Install project dependencies
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN python manage.py migrate
RUN python manage.py populate_university_database golestan_courses.xlsx
RUN python manage.py fix_teachers_name
RUN python manage.py delete_additional_departments
RUN python manage.py add_profile_to_existing_entities

# Copy the rest of the application's code
COPY . /app/

# Expose the necessary port(s)
EXPOSE 8000