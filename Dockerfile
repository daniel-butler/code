FROM python:3.8-alpine

RUN apk add --no-cache --virtual .build-deps gcc postgresql-dev musl-dev python3-dev
RUN apk add libpq

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN apk del --no-cache .build-deps

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /src
ENV DJANGO_SETTINGS_MODULE=djangoproject.django_project.settings
CMD python /tests/wait_for_postgres.py && \
    python /src/djangoproject/manage.py migrate && \
    python /src/djangoproject/manage.py runserver 0.0.0.0:80
