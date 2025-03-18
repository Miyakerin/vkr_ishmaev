FROM python:3.12.4-alpine3.19

RUN pip install poetry==2.1.1

ENV POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN poetry config virtualenvs.create false && poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY shared ./shared
COPY services/ai_service ./services/ai_service

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENTRYPOINT ["python", "services/ai_service/app.py"]
