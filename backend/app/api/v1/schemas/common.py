"""
Common schemas for API v1.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters schema."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response schema."""
    data: List[Any] = Field(..., description="Response data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = Field(default=False, description="Success status")
    error: "ErrorDetail" = Field(..., description="Error details")


class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: str = Field(..., description="Request ID")


class SuccessResponse(BaseModel):
    """Success response schema."""
    success: bool = Field(default=True, description="Success status")
    data: Any = Field(..., description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    services: Dict[str, Any] = Field(..., description="Service health details")


class StatusResponse(BaseModel):
    """Status response schema."""
    status: str = Field(..., description="Status")
    message: Optional[str] = Field(None, description="Status message")
    timestamp: datetime = Field(..., description="Status timestamp")
