"""
User Models for Stock Market Dashboard
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from .base import BaseSchema, TimestampMixin


class UserRole(str, Enum):
    """User roles"""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserBase(BaseSchema):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(BaseSchema):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserUpdate(BaseSchema):
    """User update model"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class User(UserBase, TimestampMixin):
    """Complete user model"""
    id: str
    hashed_password: str
    last_login: Optional[datetime] = None
    email_verified: bool = False
    phone: Optional[str] = None
    preferences: Optional[dict] = {}


class UserPublic(BaseSchema):
    """Public user model (without sensitive data)"""
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None


class UserLogin(BaseSchema):
    """User login model"""
    username: str
    password: str


class UserLoginResponse(BaseSchema):
    """User login response"""
    user: UserPublic
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseSchema):
    """Refresh token request"""
    refresh_token: str
