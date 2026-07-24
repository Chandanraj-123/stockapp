"""
Configuration Management for Stock Market Dashboard
Enterprise-grade configuration with environment variables
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import json
from functools import lru_cache


class DatabaseConfig(BaseModel):
    """Database configuration"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="postgres", env="DB_USERNAME")
    password: str = Field(default="postgres", env="DB_PASSWORD")
    database: str = Field(default="stockapp", env="DB_DATABASE")
    schema: str = Field(default="public", env="DB_SCHEMA")
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    @property
    def url(self) -> str:
        """Get database URL"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def sync_url(self) -> str:
        """Get synchronous database URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    """Redis configuration"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=100, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: int = Field(default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    
    @property
    def url(self) -> str:
        """Get Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class JWTConfig(BaseModel):
    """JWT configuration"""
    secret_key: str = Field(default="change-me-in-production", env="JWT_SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    @property
    def access_token_expire_seconds(self) -> int:
        return self.access_token_expire_minutes * 60
    
    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.refresh_token_expire_days * 24 * 60 * 60


class ServiceConfig(BaseModel):
    """Service configuration"""
    name: str = Field(default="stockapp", env="SERVICE_NAME")
    host: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    port: int = Field(default=8000, env="SERVICE_PORT")
    debug: bool = Field(default=False, env="SERVICE_DEBUG")
    workers: int = Field(default=4, env="SERVICE_WORKERS")
    timeout: int = Field(default=30, env="SERVICE_TIMEOUT")
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class CeleryConfig(BaseModel):
    """Celery configuration"""
    broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")


class TradingViewConfig(BaseModel):
    """TradingView configuration"""
    screener_version: str = Field(default="3.2.0", env="TRADINGVIEW_SCREENER_VERSION")
    poll_interval: int = Field(default=3, env="TRADINGVIEW_POLL_INTERVAL")
    max_symbols_per_request: int = Field(default=100, env="TRADINGVIEW_MAX_SYMBOLS")


class MarketDataConfig(BaseModel):
    """Market data configuration"""
    cache_ttl: int = Field(default=30, env="MARKET_DATA_CACHE_TTL")
    max_history_days: int = Field(default=365, env="MARKET_DATA_MAX_HISTORY_DAYS")
    default_timeframes: List[str] = Field(
        default=["1D", "1W", "1M", "3M", "6M", "1Y", "5Y"],
        env="MARKET_DATA_DEFAULT_TIMEFRAMES"
    )


class AppConfig(BaseModel):
    """Main application configuration"""
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_dir: str = Field(default="/workspace/Chandanraj-123__stockapp/logs", env="LOG_DIR")
    
    # Service configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    tradingview: TradingViewConfig = Field(default_factory=TradingViewConfig)
    market_data: MarketDataConfig = Field(default_factory=MarketDataConfig)
    
    # Feature flags
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_config() -> AppConfig:
    """
    Get configuration from environment variables
    
    Returns:
        AppConfig instance with all settings
    """
    return AppConfig()


def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        file_path: Path to configuration file
    
    Returns:
        Dictionary with configuration
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_config_to_file(config: Dict[str, Any], file_path: str) -> None:
    """
    Save configuration to JSON file
    
    Args:
        config: Configuration dictionary
        file_path: Path to save configuration
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(config, f, indent=2)


# Global config instance
config = None


def get_app_config() -> AppConfig:
    """Get the global app configuration"""
    global config
    if config is None:
        config = get_config()
    return config
