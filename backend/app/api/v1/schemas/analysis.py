"""
Analysis schemas for API v1.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Analysis request schema."""
    project_id: str = Field(..., description="Project ID to analyze")
    commit_sha: Optional[str] = Field(None, description="Specific commit SHA")
    branch: Optional[str] = Field(None, description="Branch to analyze")
    analysis_type: str = Field(default="full", description="Type of analysis")
    config: Dict[str, Any] = Field(default_factory=dict, description="Analysis configuration")
    include_files: Optional[List[str]] = Field(None, description="Files to include")
    exclude_files: Optional[List[str]] = Field(None, description="Files to exclude")


class AnalysisResponse(BaseModel):
    """Analysis response schema."""
    id: str = Field(..., description="Analysis ID")
    project_id: str = Field(..., description="Project ID")
    status: str = Field(..., description="Analysis status")
    progress: int = Field(default=0, description="Analysis progress (0-100)")
    analysis_type: str = Field(..., description="Type of analysis")
    commit_sha: Optional[str] = Field(None, description="Analyzed commit SHA")
    branch: Optional[str] = Field(None, description="Analyzed branch")
    started_at: datetime = Field(..., description="Analysis start time")
    completed_at: Optional[datetime] = Field(None, description="Analysis completion time")
    config: Dict[str, Any] = Field(default_factory=dict, description="Analysis configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")


class AnalysisStatusResponse(BaseModel):
    """Analysis status response schema."""
    id: str = Field(..., description="Analysis ID")
    status: str = Field(..., description="Current status")
    progress: int = Field(..., description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class IssueResponse(BaseModel):
    """Issue response schema."""
    id: str = Field(..., description="Issue ID")
    analysis_id: str = Field(..., description="Analysis ID")
    type: str = Field(..., description="Issue type")
    severity: str = Field(..., description="Issue severity")
    category: str = Field(..., description="Issue category")
    title: str = Field(..., description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    file_path: str = Field(..., description="File path")
    line_start: Optional[int] = Field(None, description="Start line number")
    line_end: Optional[int] = Field(None, description="End line number")
    column_start: Optional[int] = Field(None, description="Start column")
    column_end: Optional[int] = Field(None, description="End column")
    code_snippet: Optional[str] = Field(None, description="Code snippet")
    suggestion: Optional[str] = Field(None, description="Fix suggestion")
    confidence: float = Field(default=1.0, description="Confidence score")
    effort_estimate: Optional[int] = Field(None, description="Effort estimate (minutes)")
    impact_score: Optional[float] = Field(None, description="Impact score")
    priority_score: Optional[float] = Field(None, description="Priority score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MetricResponse(BaseModel):
    """Metric response schema."""
    id: str = Field(..., description="Metric ID")
    analysis_id: str = Field(..., description="Analysis ID")
    metric_type: str = Field(..., description="Metric type")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    file_path: Optional[str] = Field(None, description="File path")
    function_name: Optional[str] = Field(None, description="Function name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AnalysisListResponse(BaseModel):
    """Analysis list response schema."""
    analyses: List[AnalysisResponse] = Field(..., description="List of analyses")
    total: int = Field(..., description="Total number of analyses")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
