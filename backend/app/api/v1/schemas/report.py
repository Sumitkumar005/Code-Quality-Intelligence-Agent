"""
Report schemas for API v1.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Report generation request schema."""
    project_id: str = Field(..., description="Project ID")
    analysis_id: Optional[str] = Field(None, description="Analysis ID to base report on")
    report_type: str = Field(..., description="Type of report")
    format: str = Field(default="pdf", description="Report format")
    config: Dict[str, Any] = Field(default_factory=dict, description="Report configuration")
    include_sections: Optional[List[str]] = Field(None, description="Sections to include")
    exclude_sections: Optional[List[str]] = Field(None, description="Sections to exclude")


class ReportResponse(BaseModel):
    """Report response schema."""
    id: str = Field(..., description="Report ID")
    project_id: str = Field(..., description="Project ID")
    analysis_id: Optional[str] = Field(None, description="Analysis ID")
    title: str = Field(..., description="Report title")
    report_type: str = Field(..., description="Report type")
    format: str = Field(..., description="Report format")
    status: str = Field(..., description="Report generation status")
    file_url: Optional[str] = Field(None, description="Report file URL")
    config: Dict[str, Any] = Field(default_factory=dict, description="Report configuration")
    generated_at: Optional[datetime] = Field(None, description="Generation timestamp")
    generated_by: Optional[str] = Field(None, description="User who generated the report")


class ReportListResponse(BaseModel):
    """Report list response schema."""
    reports: List[ReportResponse] = Field(..., description="List of reports")
    total: int = Field(..., description="Total number of reports")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ReportExportRequest(BaseModel):
    """Report export request schema."""
    report_id: str = Field(..., description="Report ID to export")
    format: str = Field(..., description="Export format")
    config: Dict[str, Any] = Field(default_factory=dict, description="Export configuration")


class ReportExportResponse(BaseModel):
    """Report export response schema."""
    export_id: str = Field(..., description="Export ID")
    report_id: str = Field(..., description="Report ID")
    format: str = Field(..., description="Export format")
    status: str = Field(..., description="Export status")
    file_url: Optional[str] = Field(None, description="Export file URL")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
