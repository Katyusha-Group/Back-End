FROM python:3.10.0-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Install system dependencies necessary for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy only the Pipfile and Pipfile.lock first to leverage Docker caching
COPY Pipfile Pipfile.lock /app/

# Install project dependencies
RUN pipenv install --system --deploy

# Copy the rest of the application's code
COPY . /app/

# Expose the necessary port(s)
EXPOSE 8000

# Run the application
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
