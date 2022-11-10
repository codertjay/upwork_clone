FROM python:3.9.7-slim

#  this copy all to folder to app
COPY . /app
#  change workdir to app which is cd /app
WORKDIR /app

#  create virtual environment inside the /opt/venv if no docker
RUN python3 -m venv /opt/venv


# note: this location  /opt/venv/bin/pip is almost like 
# you are using the virtual environment 
# and also we just install the requirements.txt file
# and change the entrypoints.sh files to be able to run command
#  which are currently gunicorn_entrypoint and daphne_entrypoint

RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt  && chmod +x /app/migrate.sh \
     && chmod +x  /app/runserver.sh
