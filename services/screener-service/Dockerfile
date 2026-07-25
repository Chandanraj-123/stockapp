# Screener Service Dockerfile
FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY ../../shared-libs ./shared-libs/
COPY . .
RUN poetry config virtualenvs.in-project true && poetry install --no-interaction --no-ansi --only main

RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

ENV SERVICE_NAME=screener-service SERVICE_HOST=0.0.0.0 SERVICE_PORT=8005 SERVICE_DEBUG=false LOG_LEVEL=INFO LOG_DIR=/app/logs

EXPOSE 8005
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8005/health || exit 1
CMD ["poetry", "run", "python", "main.py"]
