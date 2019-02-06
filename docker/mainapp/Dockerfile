FROM python:3
RUN mkdir -p /srv/mainapp
WORKDIR /srv/mainapp
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN export ENV="prod"
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
