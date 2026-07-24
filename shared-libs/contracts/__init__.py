# API Contracts
# OpenAPI specifications and API contracts for inter-service communication

from .api_specs import (
    API_GATEWAY_ROUTES,
    SERVICE_ENDPOINTS,
    REDIS_CHANNELS,
    CELERY_QUEUES,
    DATABASE_SCHEMAS,
)

__all__ = [
    "API_GATEWAY_ROUTES",
    "SERVICE_ENDPOINTS", 
    "REDIS_CHANNELS",
    "CELERY_QUEUES",
    "DATABASE_SCHEMAS",
]
