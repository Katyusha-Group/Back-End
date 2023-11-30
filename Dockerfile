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
RUN timeout 300 pip install --upgrade pip

RUN timeout 300 pip install -r requirements.txt

# Copy the rest of the application's code
COPY . /app/

# Expose the necessary port(s)
EXPOSE 8000
