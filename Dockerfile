FROM python:3.10.5-slim

ENV PYTHONBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install Flask gunicorn firebase_admin google-api-python-client google-auth-httplib2 google-auth-oauthlib

CMD exec gunicorn --bind :$PORT --workers 1 --threads 9 --timeout 0 website:app