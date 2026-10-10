FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


FROM base AS test

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["pytest"]


FROM base AS runtime

RUN useradd --create-home --uid 1000 app

COPY app ./app

USER app

EXPOSE 8000

# Um único worker: cache e limitador vivem na memória do processo.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
