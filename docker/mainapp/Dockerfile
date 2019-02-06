FROM python:3
RUN mkdir -p /srv/mainapp
WORKDIR /srv/mainapp
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN /bin/bash -c "export ENV=prod; gunicorn --bind 0.0.0.0:8000 wsgi:app"
