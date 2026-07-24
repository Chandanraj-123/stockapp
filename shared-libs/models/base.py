"""
Base Models for Stock Market Dashboard
Enterprise-grade shared models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generic, TypeVar
from datetime import datetime
from enum import Enum


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


T = TypeVar('T')


class ResponseModel(BaseSchema, Generic[T]):
    """Standard response wrapper"""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper"""
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 1


class HealthCheckResponse(BaseSchema):
    """Health check response"""
    status: str = "healthy"
    service: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: dict = {}


class ErrorResponse(BaseSchema):
    """Error response model"""
    success: bool = False
    error: str
    code: int = 500
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
