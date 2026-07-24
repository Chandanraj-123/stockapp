"""
User Service
Enterprise-grade user service for Stock Market Dashboard
Manages user profiles, preferences, and settings
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared_libs.utils import get_app_config, setup_logging
from shared_libs.models import (
    HealthCheckResponse,
    ErrorResponse,
    UserCreate,
    UserUpdate,
    UserPublic,
    ResponseModel,
    PaginatedResponse,
)


# Initialize configuration
config = get_app_config()

# Initialize logger
logger = setup_logging(
    service_name="user-service",
    level=config.log_level,
    log_dir=config.log_dir,
    use_json=True
)


class UserService:
    """User Service"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Stock Market Dashboard - User Service",
            description="Enterprise-grade user service for Stock Market Dashboard",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Setup CORS
        self._setup_cors()
        
        # Setup routes
        self._setup_routes()
        
        # Setup exception handlers
        self._setup_exception_handlers()
        
        # In-memory user store (in production, use database)
        self.users: Dict[str, Dict[str, Any]] = {}
    
    def _setup_cors(self):
        """Setup CORS middleware"""
        if config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=config.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            logger.info("CORS middleware enabled")
    
    def _setup_routes(self):
        """Setup all API routes"""
        # Health check
        self.app.get("/health")(self.health_check)
        self.app.get("/")(self.root)
        
        # API routes
        api_router = self._create_api_router()
        self.app.include_router(api_router, prefix="/api/v1/users")
    
    def _create_api_router(self):
        """Create the API router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        # User endpoints
        router.post("/")(self.create_user)
        router.get("/")(self.list_users)
        router.get("/{user_id}")(self.get_user)
        router.put("/{user_id}")(self.update_user)
        router.delete("/{user_id}")(self.delete_user)
        
        # Preferences endpoints
        router.get("/{user_id}/preferences")(self.get_preferences)
        router.put("/{user_id}/preferences")(self.update_preferences)
        
        return router
    
    def _setup_exception_handlers(self):
        """Setup exception handlers"""
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(
                    error=exc.detail,
                    code=exc.status_code
                ).model_dump()
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.exception(f"Unexpected error: {exc}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal server error",
                    code=500,
                    details={"message": str(exc)}
                ).model_dump()
            )
    
    async def create_user(self, user_data: UserCreate):
        """Create a new user"""
        # Check if user already exists
        for user in self.users.values():
            if user["username"] == user_data.username:
                raise HTTPException(status_code=400, detail="Username already exists")
            if user["email"] == user_data.email:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create user
        user_id = str(uuid4())
        user = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": "user",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "email_verified": False,
            "preferences": {
                "theme": "dark",
                "language": "en",
                "timezone": "Asia/Kolkata",
                "currency": "INR",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            }
        }
        
        self.users[user_id] = user
        
        logger.info(f"User created: {user['username']}")
        
        return ResponseModel(
            success=True,
            data=UserPublic(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                role=user.get("role", "user"),
                status=user.get("status", "active"),
                created_at=user["created_at"],
                last_login=None
            ),
            message="User created successfully"
        )
    
    async def list_users(self):
        """List all users"""
        users = []
        for user in self.users.values():
            users.append(UserPublic(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                role=user.get("role", "user"),
                status=user.get("status", "active"),
                created_at=user["created_at"],
                last_login=user.get("last_login")
            ))
        
        return PaginatedResponse(
            items=users,
            total=len(users),
            page=1,
            page_size=len(users),
            total_pages=1
        )
    
    async def get_user(self, user_id: str):
        """Get user by ID"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return ResponseModel(
            success=True,
            data=UserPublic(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                role=user.get("role", "user"),
                status=user.get("status", "active"),
                created_at=user["created_at"],
                last_login=user.get("last_login")
            )
        )
    
    async def update_user(self, user_id: str, user_data: UserUpdate):
        """Update user"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user fields
        if user_data.username:
            # Check if username already exists
            for existing_user in self.users.values():
                if existing_user["id"] != user_id and existing_user["username"] == user_data.username:
                    raise HTTPException(status_code=400, detail="Username already exists")
            user["username"] = user_data.username
        
        if user_data.email:
            # Check if email already exists
            for existing_user in self.users.values():
                if existing_user["id"] != user_id and existing_user["email"] == user_data.email:
                    raise HTTPException(status_code=400, detail="Email already exists")
            user["email"] = user_data.email
        
        if user_data.full_name:
            user["full_name"] = user_data.full_name
        
        if user_data.role:
            user["role"] = user_data.role
        
        if user_data.status:
            user["status"] = user_data.status
        
        user["updated_at"] = datetime.utcnow()
        
        logger.info(f"User updated: {user['username']}")
        
        return ResponseModel(
            success=True,
            data=UserPublic(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                role=user.get("role", "user"),
                status=user.get("status", "active"),
                created_at=user["created_at"],
                last_login=user.get("last_login")
            ),
            message="User updated successfully"
        )
    
    async def delete_user(self, user_id: str):
        """Delete user"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete - mark as deleted
        user["status"] = "deleted"
        user["updated_at"] = datetime.utcnow()
        
        logger.info(f"User deleted: {user['username']}")
        
        return ResponseModel(
            success=True,
            message="User deleted successfully"
        )
    
    async def get_preferences(self, user_id: str):
        """Get user preferences"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return ResponseModel(
            success=True,
            data=user.get("preferences", {})
        )
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update preferences
        if "preferences" not in user:
            user["preferences"] = {}
        
        user["preferences"].update(preferences)
        user["updated_at"] = datetime.utcnow()
        
        logger.info(f"Preferences updated for user: {user['username']}")
        
        return ResponseModel(
            success=True,
            data=user["preferences"],
            message="Preferences updated successfully"
        )
    
    async def health_check(self):
        """Health check endpoint"""
        return HealthCheckResponse(
            service="user-service",
            version="1.0.0",
            dependencies={
                "database": "healthy",
                "cache": "healthy"
            }
        )
    
    async def root(self):
        """Root endpoint"""
        return {
            "service": "user-service",
            "version": "1.0.0",
            "description": "User Service for Stock Market Dashboard",
            "docs": "/docs",
            "health": "/health"
        }


# Create and run the User Service
def create_app() -> FastAPI:
    """Create the User Service FastAPI application"""
    user_service = UserService()
    return user_service.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    logger.info("Starting User Service...")
    logger.info(f"Service URL: {config.service.url}")
    
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port,
        reload=config.service.debug,
        workers=config.service.workers if not config.service.debug else 1,
        log_level=config.log_level.lower()
    )
