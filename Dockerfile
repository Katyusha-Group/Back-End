FROM ubuntu:22.04


RUN apt-get update && apt-get install -y python3 python3-pip python3-venv supervisor

ARG USER=root
USER $USER
RUN python3 -m venv katyusha_env

WORKDIR /app

# install dependencies
COPY requirements.txt /app/
RUN /katyusha_env/bin/pip install -r requirements.txt

# Copy project
COPY . /app/

COPY deployment deployment

COPY deployment/gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf
COPY deployment/daphne.conf /etc/supervisor/conf.d/daphne.conf


RUN mkdir /logs
# Expose ports
EXPOSE 8000
EXPOSE 8001

RUN chmod +x /app/start.sh
RUN chmod +x /app/deployment/start_app.sh
RUN chmod +x /app/deployment/start_daphne.sh


ENTRYPOINT ["./start.sh"]
