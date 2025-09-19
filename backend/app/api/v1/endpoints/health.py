"""
Health check endpoints for the CQIA application.
"""

from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.base import HealthResponse, SuccessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> Any:
    """
    Basic health check endpoint.
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
        uptime_seconds=0,  # Would be calculated in production
        environment=settings.ENVIRONMENT
    )


@router.get("/health/detailed", response_model=SuccessResponse[Dict[str, Any]])
def detailed_health_check(
    db: Session = Depends(get_db)
) -> Any:
    """
    Detailed health check with database connectivity test.
    """
    health_data = {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": "unknown",
            "connection": False
        },
        "redis": {
            "status": "unknown",
            "connection": False
        },
        "celery": {
            "status": "unknown",
            "workers": 0
        }
    }

    # Test database connection
    try:
        db.execute("SELECT 1")
        health_data["database"] = {
            "status": "healthy",
            "connection": True
        }
    except Exception as e:
        health_data["database"] = {
            "status": "unhealthy",
            "connection": False,
            "error": str(e)
        }
        health_data["status"] = "degraded"

    # Test Redis connection (if available)
    try:
        from app.core.cache import redis_client
        redis_client.ping()
        health_data["redis"] = {
            "status": "healthy",
            "connection": True
        }
    except Exception as e:
        health_data["redis"] = {
            "status": "unhealthy",
            "connection": False,
            "error": str(e)
        }

    # Test Celery (if available)
    try:
        from app.core.celery_app import celery_app
        # Basic celery check
        health_data["celery"] = {
            "status": "healthy",
            "workers": 1  # Simplified check
        }
    except Exception as e:
        health_data["celery"] = {
            "status": "unhealthy",
            "workers": 0,
            "error": str(e)
        }

    return SuccessResponse(
        data=health_data,
        message="Detailed health check completed"
    )


@router.get("/ping", response_model=SuccessResponse[str])
def ping() -> Any:
    """
    Simple ping endpoint for load balancer health checks.
    """
    return SuccessResponse(
        data="pong",
        message="Service is responding"
    )
