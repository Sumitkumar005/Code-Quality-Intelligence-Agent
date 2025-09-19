"""
Custom exceptions for CQIA application.
Provides structured error handling throughout the application.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class CQIAException(Exception):
    """Base exception class for CQIA application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(CQIAException):
    """Authentication-related errors."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(CQIAException):
    """Authorization-related errors."""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class ValidationError(CQIAException):
    """Data validation errors."""

    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class NotFoundError(CQIAException):
    """Resource not found errors."""

    def __init__(self, resource: str = "Resource", **kwargs):
        message = f"{resource} not found"
        super().__init__(message, status_code=404, **kwargs)


class ConflictError(CQIAException):
    """Resource conflict errors."""

    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(message, status_code=409, **kwargs)


class RateLimitError(CQIAException):
    """Rate limiting errors."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, status_code=429, **kwargs)


class ExternalServiceError(CQIAException):
    """External service integration errors."""

    def __init__(self, service: str, message: str = "External service error", **kwargs):
        message = f"{service}: {message}"
        super().__init__(message, status_code=502, **kwargs)


class AnalysisError(CQIAException):
    """Code analysis related errors."""

    def __init__(self, message: str = "Analysis failed", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class AIError(CQIAException):
    """AI/LLM related errors."""

    def __init__(self, message: str = "AI service error", **kwargs):
        super().__init__(message, status_code=503, **kwargs)


class DatabaseError(CQIAException):
    """Database operation errors."""

    def __init__(self, message: str = "Database error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class CacheError(CQIAException):
    """Cache operation errors."""

    def __init__(self, message: str = "Cache error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class FileStorageError(CQIAException):
    """File storage operation errors."""

    def __init__(self, message: str = "File storage error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


# Exception handlers for FastAPI
def create_http_exception(exception: CQIAException) -> HTTPException:
    """Convert CQIA exception to FastAPI HTTPException."""
    return HTTPException(
        status_code=exception.status_code,
        detail={
            "error": {
                "code": exception.error_code,
                "message": exception.message,
                "details": exception.details
            }
        }
    )


# Error response models
def format_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format error response for API."""
    return {
        "success": False,
        "error": {
            "code": error_code or "INTERNAL_ERROR",
            "message": message,
            "status_code": status_code,
            "details": details or {},
            "timestamp": None,  # Will be set by middleware
            "request_id": None,  # Will be set by middleware
        }
    }


# Exception mapping for common errors
EXCEPTION_STATUS_MAP = {
    AuthenticationError: 401,
    AuthorizationError: 403,
    ValidationError: 400,
    NotFoundError: 404,
    ConflictError: 409,
    RateLimitError: 429,
    ExternalServiceError: 502,
    AnalysisError: 500,
    AIError: 503,
    DatabaseError: 500,
    CacheError: 500,
    FileStorageError: 500,
}


def get_exception_status_code(exception: Exception) -> int:
    """Get HTTP status code for exception."""
    return EXCEPTION_STATUS_MAP.get(type(exception), 500)


# Logging utilities
def log_exception(exception: CQIAException, extra: Optional[Dict[str, Any]] = None):
    """Log exception with appropriate level."""
    log_data = {
        "error_code": exception.error_code,
        "status_code": exception.status_code,
        "details": exception.details,
        **(extra or {})
    }

    if exception.status_code >= 500:
        logger.error(f"Server error: {exception.message}", extra=log_data)
    elif exception.status_code >= 400:
        logger.warning(f"Client error: {exception.message}", extra=log_data)
    else:
        logger.info(f"Application error: {exception.message}", extra=log_data)


# Validation helpers
def validate_required(value: Any, field_name: str):
    """Validate required field."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required")


def validate_length(value: str, field_name: str, min_length: int = None, max_length: int = None):
    """Validate string length."""
    if min_length and len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")
    if max_length and len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters")


def validate_range(value: int, field_name: str, min_value: int = None, max_value: int = None):
    """Validate numeric range."""
    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")
    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")
