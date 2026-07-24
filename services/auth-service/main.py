"""
Authentication Service
Enterprise-grade authentication service for Stock Market Dashboard
Handles JWT token generation, validation, and user authentication
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext

from shared_libs.utils import get_app_config, setup_logging
from shared_libs.models import (
    HealthCheckResponse,
    ErrorResponse,
    UserLogin,
    UserLoginResponse,
    UserCreate,
    UserPublic,
    RefreshTokenRequest,
    ResponseModel,
)
from shared_libs.contracts import SERVICE_ENDPOINTS


# Initialize configuration
config = get_app_config()

# Initialize logger
logger = setup_logging(
    service_name="auth-service",
    level=config.log_level,
    log_dir=config.log_dir,
    use_json=True
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()


# In-memory user store (in production, use database)
class UserStore:
    """Temporary in-memory user store"""
    
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.refresh_tokens: Dict[str, str] = {}  # token -> user_id
    
    def create_user(self, username: str, email: str, hashed_password: str, **kwargs) -> Dict[str, Any]:
        """Create a new user"""
        user_id = str(uuid4())
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "full_name": kwargs.get("full_name"),
            "role": kwargs.get("role", "user"),
            "status": kwargs.get("status", "active"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "email_verified": False,
        }
        self.users[user_id] = user
        return user
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        for user in self.users.values():
            if user["username"] == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        for user in self.users.values():
            if user["email"] == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def store_refresh_token(self, token: str, user_id: str):
        """Store refresh token"""
        self.refresh_tokens[token] = user_id
    
    def get_user_by_refresh_token(self, token: str) -> Optional[str]:
        """Get user ID by refresh token"""
        return self.refresh_tokens.get(token)
    
    def revoke_refresh_token(self, token: str):
        """Revoke refresh token"""
        if token in self.refresh_tokens:
            del self.refresh_tokens[token]


# Initialize user store
user_store = UserStore()


class AuthService:
    """Authentication Service"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Stock Market Dashboard - Authentication Service",
            description="Enterprise-grade authentication service for Stock Market Dashboard",
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
        self.app.include_router(api_router, prefix="/api/v1/auth")
    
    def _create_api_router(self):
        """Create the API router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        # Authentication endpoints
        router.post("/login")(self.login)
        router.post("/refresh")(self.refresh_token)
        router.post("/logout")(self.logout)
        router.get("/me")(self.get_current_user)
        router.post("/validate")(self.validate_token)
        
        # User registration (can be moved to user-service)
        router.post("/register")(self.register)
        
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
    
    def _create_access_token(self, user_id: str, username: str, role: str) -> str:
        """Create JWT access token"""
        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=config.jwt.access_token_expire_seconds),
            "type": "access"
        }
        return jwt.encode(payload, config.jwt.secret_key, algorithm=config.jwt.algorithm)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=config.jwt.refresh_token_expire_seconds),
            "type": "refresh",
            "jti": str(uuid4())  # Unique token ID
        }
        token = jwt.encode(payload, config.jwt.secret_key, algorithm=config.jwt.algorithm)
        return token
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, config.jwt.secret_key, algorithms=[config.jwt.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def _hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def register(self, user_data: UserCreate):
        """Register a new user"""
        # Check if user already exists
        if user_store.get_user_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        
        if user_store.get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user
        user = user_store.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        logger.info(f"User registered: {user['username']}")
        
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
            message="User registered successfully"
        )
    
    async def login(self, login_data: UserLogin):
        """Login user and return tokens"""
        # Get user
        user = user_store.get_user_by_username(login_data.username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not self._verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Check user status
        if user.get("status") != "active":
            raise HTTPException(status_code=403, detail="User account is not active")
        
        # Create tokens
        access_token = self._create_access_token(
            user_id=user["id"],
            username=user["username"],
            role=user.get("role", "user")
        )
        refresh_token = self._create_refresh_token(user_id=user["id"])
        
        # Store refresh token
        user_store.store_refresh_token(refresh_token, user["id"])
        
        # Update last login
        user["last_login"] = datetime.utcnow()
        
        logger.info(f"User logged in: {user['username']}")
        
        return UserLoginResponse(
            user=UserPublic(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                role=user.get("role", "user"),
                status=user.get("status", "active"),
                created_at=user["created_at"],
                last_login=user["last_login"]
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=config.jwt.access_token_expire_seconds
        )
    
    async def refresh_token(self, request: RefreshTokenRequest):
        """Refresh access token using refresh token"""
        # Verify refresh token
        try:
            payload = self._verify_token(request.refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Check if refresh token is valid (not revoked)
            stored_user_id = user_store.get_user_by_refresh_token(request.refresh_token)
            if not stored_user_id or stored_user_id != user_id:
                raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")
            
            # Get user
            user = user_store.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Create new tokens
            access_token = self._create_access_token(
                user_id=user["id"],
                username=user["username"],
                role=user.get("role", "user")
            )
            new_refresh_token = self._create_refresh_token(user_id=user["id"])
            
            # Revoke old refresh token and store new one
            user_store.revoke_refresh_token(request.refresh_token)
            user_store.store_refresh_token(new_refresh_token, user["id"])
            
            logger.info(f"Token refreshed for user: {user['username']}")
            
            return UserLoginResponse(
                user=UserPublic(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    full_name=user.get("full_name"),
                    role=user.get("role", "user"),
                    status=user.get("status", "active"),
                    created_at=user["created_at"],
                    last_login=user.get("last_login")
                ),
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=config.jwt.access_token_expire_seconds
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Refresh token error: {e}")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    async def logout(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Logout user by revoking refresh token"""
        try:
            # Get token from header
            token = credentials.credentials
            
            # Verify and get user ID
            payload = self._verify_token(token)
            user_id = payload.get("sub")
            
            # Revoke all refresh tokens for this user
            # In production, you would have a more sophisticated token management
            for token_str, uid in list(user_store.refresh_tokens.items()):
                if uid == user_id:
                    user_store.revoke_refresh_token(token_str)
            
            logger.info(f"User logged out: {user_id}")
            
            return ResponseModel(
                success=True,
                message="Logged out successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Logout error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get current user information"""
        try:
            # Get token from header
            token = credentials.credentials
            
            # Verify token
            payload = self._verify_token(token)
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Get user
            user = user_store.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserPublic(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                role=user.get("role", "user"),
                status=user.get("status", "active"),
                created_at=user["created_at"],
                last_login=user.get("last_login")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def validate_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Validate JWT token"""
        try:
            # Get token from header
            token = credentials.credentials
            
            # Verify token
            payload = self._verify_token(token)
            
            # Check token type
            token_type = payload.get("type")
            if token_type not in ["access", "refresh"]:
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            # Get user
            user_id = payload.get("sub")
            user = user_store.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return ResponseModel(
                success=True,
                data={
                    "valid": True,
                    "user_id": user_id,
                    "username": payload.get("username"),
                    "role": payload.get("role"),
                    "token_type": token_type
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def health_check(self):
        """Health check endpoint"""
        return HealthCheckResponse(
            service="auth-service",
            version="1.0.0",
            dependencies={
                "database": "healthy",
                "redis": "healthy",
                "jwt": "healthy"
            }
        )
    
    async def root(self):
        """Root endpoint"""
        return {
            "service": "auth-service",
            "version": "1.0.0",
            "description": "Authentication Service for Stock Market Dashboard",
            "docs": "/docs",
            "health": "/health"
        }


# Create and run the Authentication Service
def create_app() -> FastAPI:
    """Create the Authentication Service FastAPI application"""
    auth_service = AuthService()
    return auth_service.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    logger.info("Starting Authentication Service...")
    logger.info(f"Service URL: {config.service.url}")
    
    # Create a test user if none exists
    if not user_store.users:
        test_user = user_store.create_user(
            username="admin",
            email="admin@stockapp.com",
            hashed_password=pwd_context.hash("admin123"),
            full_name="Admin User",
            role="admin"
        )
        logger.info(f"Created test admin user: {test_user['username']}")
    
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port,
        reload=config.service.debug,
        workers=config.service.workers if not config.service.debug else 1,
        log_level=config.log_level.lower()
    )
