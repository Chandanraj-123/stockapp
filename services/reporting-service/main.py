"""
Reporting Service
Enterprise-grade reporting service for Stock Market Dashboard
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared_libs.utils import get_app_config, setup_logging
from shared_libs.models import HealthCheckResponse, ErrorResponse

config = get_app_config()
logger = setup_logging(service_name="reporting-service", level=config.log_level, log_dir=config.log_dir, use_json=True)

app = FastAPI(
    title="Stock Market Dashboard - Reporting Service",
    description="Enterprise-grade reporting service for Stock Market Dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

if config.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health_check():
    return HealthCheckResponse(service="reporting-service", version="1.0.0")

@app.get("/")
async def root():
    return {"service": "reporting-service", "version": "1.0.0", "docs": "/docs", "health": "/health"}

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception(f"Error: {exc}")
    return JSONResponse(status_code=500, content=ErrorResponse(error=str(exc), code=500).model_dump())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.service.host, port=8012, reload=config.service.debug, log_level=config.log_level.lower())
