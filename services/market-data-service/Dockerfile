# Market Data Service Dockerfile
# Enterprise-grade Docker configuration

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create and set working directory
WORKDIR /app

# Copy project files
COPY ../../shared-libs ./shared-libs/
COPY . .

# Install Python dependencies
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --only main

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables for the service
ENV SERVICE_NAME=market-data-service \
    SERVICE_HOST=0.0.0.0 \
    SERVICE_PORT=8003 \
    SERVICE_DEBUG=false \
    LOG_LEVEL=INFO \
    LOG_DIR=/app/logs \
    TRADINGVIEW_SCREENER_VERSION=3.2.0 \
    TRADINGVIEW_POLL_INTERVAL=3 \
    ENABLE_WEBSOCKET=true \
    ENABLE_CACHE=true

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the service
CMD ["poetry", "run", "python", "main.py"]
