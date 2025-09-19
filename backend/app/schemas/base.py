"""
Base Pydantic schemas for the CQIA application.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CQIA_BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        },
    )


class CQIA_BaseCreate(CQIA_BaseModel):
    """Base create schema."""

    pass


class CQIA_BaseUpdate(CQIA_BaseModel):
    """Base update schema."""

    pass


class CQIA_BaseResponse(CQIA_BaseModel):
    """Base response schema with common fields."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginatedResponse(CQIA_BaseModel):
    """Paginated response wrapper."""

    items: list[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class ErrorResponse(CQIA_BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(CQIA_BaseModel):
    """Success response schema."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class HealthResponse(CQIA_BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    services: Dict[str, str] = Field(default_factory=dict, description="Service health status")
