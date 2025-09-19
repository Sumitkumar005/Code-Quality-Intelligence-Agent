"""
Pydantic schemas for report-related operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import CQIA_BaseModel, CQIA_BaseCreate, CQIA_BaseUpdate, CQIA_BaseResponse


class ReportTemplateBase(CQIA_BaseModel):
    """Base report template schema."""

    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    template_type: str = Field(..., description="Template type")
    template_content: str = Field(..., description="Template content")
    template_config: Dict[str, Any] = Field(default_factory=dict, description="Template configuration")


class ReportTemplateCreate(ReportTemplateBase, CQIA_BaseCreate):
    """Schema for creating a report template."""

    pass


class ReportTemplateUpdate(CQIA_BaseUpdate):
    """Schema for updating a report template."""

    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    template_content: Optional[str] = Field(None, description="Template content")
    template_config: Optional[Dict[str, Any]] = Field(None, description="Template configuration")
    is_active: Optional[bool] = Field(None, description="Active status")


class ReportTemplateResponse(ReportTemplateBase, CQIA_BaseResponse):
    """Schema for report template response data."""

    is_default: bool = Field(..., description="Default template")
    is_active: bool = Field(..., description="Active status")
    usage_count: int = Field(..., description="Usage count")


class ReportBase(CQIA_BaseModel):
    """Base report schema."""

    analysis_id: str = Field(..., description="Analysis ID")
    generated_by: str = Field(..., description="User who generated report")
    title: str = Field(..., description="Report title")
    report_type: str = Field("analysis", description="Report type")
    format: str = Field("html", description="Report format")


class ReportCreate(ReportBase, CQIA_BaseCreate):
    """Schema for creating a report."""

    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Report configuration")


class ReportUpdate(CQIA_BaseUpdate):
    """Schema for updating a report."""

    title: Optional[str] = Field(None, description="Report title")
    is_public: Optional[bool] = Field(None, description="Public visibility")
    is_archived: Optional[bool] = Field(None, description="Archive status")


class ReportResponse(ReportBase, CQIA_BaseResponse):
    """Schema for report response data."""

    content: Optional[str] = Field(None, description="Report content")
    summary: Optional[str] = Field(None, description="Report summary")
    file_path: Optional[str] = Field(None, description="File path")
    file_size: Optional[int] = Field(None, description="File size")
    download_url: Optional[str] = Field(None, description="Download URL")
    is_public: bool = Field(..., description="Public visibility")
    is_archived: bool = Field(..., description="Archive status")
    config: Dict[str, Any] = Field(default_factory=dict, description="Report configuration")

    # Computed properties
    is_downloadable: bool = Field(..., description="Download availability")


class ReportWithDetails(ReportResponse):
    """Report response with related data."""

    analysis: Optional[Dict[str, Any]] = Field(None, description="Related analysis")
    generated_by_user: Optional[Dict[str, Any]] = Field(None, description="Generator user info")


class ReportGenerationRequest(CQIA_BaseModel):
    """Schema for report generation requests."""

    analysis_id: str = Field(..., description="Analysis ID")
    template_id: Optional[str] = Field(None, description="Template ID")
    title: Optional[str] = Field(None, description="Report title")
    format: str = Field("html", description="Report format")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Generation configuration")
    include_sections: Optional[List[str]] = Field(None, description="Sections to include")


class ReportGenerationResponse(CQIA_BaseModel):
    """Schema for report generation responses."""

    report_id: str = Field(..., description="Generated report ID")
    status: str = Field(..., description="Generation status")
    download_url: Optional[str] = Field(None, description="Download URL")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class ReportExportRequest(CQIA_BaseModel):
    """Schema for report export requests."""

    report_id: str = Field(..., description="Report ID")
    format: str = Field("pdf", description="Export format")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Export options")


class DashboardData(CQIA_BaseModel):
    """Schema for dashboard data."""

    total_projects: int = Field(..., description="Total projects")
    total_analyses: int = Field(..., description="Total analyses")
    total_issues: int = Field(..., description="Total issues")
    average_quality_score: Optional[float] = Field(None, description="Average quality score")
    recent_analyses: List[Dict[str, Any]] = Field(default_factory=list, description="Recent analyses")
    quality_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Quality trends")
    top_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Top issues")


class AnalyticsData(CQIA_BaseModel):
    """Schema for analytics data."""

    timeframe: str = Field(..., description="Timeframe")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Analytics metrics")
    trends: List[Dict[str, Any]] = Field(default_factory=list, description="Trend data")
    comparisons: Dict[str, Any] = Field(default_factory=dict, description="Comparison data")


class ReportMetrics(CQIA_BaseModel):
    """Schema for report metrics."""

    report_id: str = Field(..., description="Report ID")
    views: int = Field(..., description="View count")
    downloads: int = Field(..., description="Download count")
    shares: int = Field(..., description="Share count")
    average_rating: Optional[float] = Field(None, description="Average rating")
    feedback_count: int = Field(..., description="Feedback count")


class ReportFeedback(CQIA_BaseModel):
    """Schema for report feedback."""

    report_id: str = Field(..., description="Report ID")
    user_id: str = Field(..., description="User ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    comment: Optional[str] = Field(None, description="Feedback comment")
    categories: List[str] = Field(default_factory=list, description="Feedback categories")
