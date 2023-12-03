FROM python:3.10.5-alpine3.16

WORKDIR /api/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN apk update && apk add --no-cache libmagic && \
    apk update && apk add git && \
    apk update && apk add --no-cache make && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

COPY .env.template .env

COPY . .

ENTRYPOINT ["python", "manage.py", "runserver", "127.0.0.1:8000"]
