FROM python:3.7-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY Pipfile* /app/
COPY docker-entrypoint.sh /

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add build-base \
    && apk add postgresql \
    && apk add postgresql-dev \
    && apk del build-deps \
    && apk add jpeg-dev \
    && apk add libjpeg \
    && apk add zlib-dev \
    && apk add libpng-dev

RUN pip install -U pip pipenv \
  && pipenv requirements > requirements.txt \
  && pip install -r requirements.txt

ENTRYPOINT ["/bin/sh", "-c"]
