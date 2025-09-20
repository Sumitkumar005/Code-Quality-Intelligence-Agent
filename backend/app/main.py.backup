"""
Main FastAPI application for the CQIA (Code Quality Intelligence Agent) system.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.exceptions import APIException
from app.core.logging import setup_logging

# Setup logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    logger.info("Starting CQIA application...")

    # Startup tasks
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")

        # Initialize cache, background tasks, etc.
        logger.info("Application startup completed")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    yield

    # Shutdown tasks
    logger.info("Shutting down CQIA application...")
    # Cleanup resources, close connections, etc.
    logger.info("Application shutdown completed")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Code Quality Intelligence Agent - Advanced code analysis and quality management platform",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Global exception handlers
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": exc.error_code,
                "data": exc.data
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            },
        )

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to CQIA - Code Quality Intelligence Agent",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/api/v1/health",
            "status": "running"
        }

    # Health check endpoint (simple)
    @app.get("/health", tags=["health"])
    async def health_check():
        """Simple health check endpoint."""
        return {"status": "healthy", "version": settings.VERSION}

    return app


# Create the FastAPI application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
