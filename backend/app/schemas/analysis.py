"""
Pydantic schemas for analysis-related operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import CQIA_BaseModel, CQIA_BaseCreate, CQIA_BaseUpdate, CQIA_BaseResponse


class IssueBase(CQIA_BaseModel):
    """Base issue schema."""

    rule_id: str = Field(..., description="Rule identifier")
    rule_name: str = Field(..., description="Rule name")
    category: str = Field(..., description="Issue category")
    severity: str = Field(..., description="Issue severity")
    file_path: str = Field(..., description="File path where issue was found")
    line_number: Optional[int] = Field(None, description="Line number")
    column_number: Optional[int] = Field(None, description="Column number")
    function_name: Optional[str] = Field(None, description="Function name")
    message: str = Field(..., description="Issue message")
    description: Optional[str] = Field(None, description="Detailed description")
    code_snippet: Optional[str] = Field(None, description="Code snippet")
    confidence: Optional[float] = Field(None, description="Confidence score")
    effort_minutes: Optional[int] = Field(None, description="Effort estimate in minutes")
    tags: List[str] = Field(default_factory=list, description="Issue tags")


class IssueCreate(IssueBase, CQIA_BaseCreate):
    """Schema for creating an issue."""

    analysis_id: str = Field(..., description="Analysis ID")


class IssueUpdate(CQIA_BaseUpdate):
    """Schema for updating an issue."""

    is_resolved: Optional[bool] = Field(None, description="Resolution status")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by: Optional[str] = Field(None, description="User who resolved")


class IssueResponse(IssueBase, CQIA_BaseResponse):
    """Schema for issue response data."""

    analysis_id: str = Field(..., description="Analysis ID")
    is_resolved: bool = Field(..., description="Resolution status")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by: Optional[str] = Field(None, description="User who resolved")

    # Computed properties
    location_string: str = Field(..., description="Formatted location string")


class AnalysisArtifactBase(CQIA_BaseModel):
    """Base analysis artifact schema."""

    name: str = Field(..., description="Artifact name")
    artifact_type: str = Field(..., description="Artifact type")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size in bytes")


class AnalysisArtifactCreate(AnalysisArtifactBase, CQIA_BaseCreate):
    """Schema for creating an analysis artifact."""

    analysis_id: str = Field(..., description="Analysis ID")
    content: Optional[str] = Field(None, description="Artifact content")


class AnalysisArtifactResponse(AnalysisArtifactBase, CQIA_BaseResponse):
    """Schema for analysis artifact response data."""

    analysis_id: str = Field(..., description="Analysis ID")
    content: Optional[str] = Field(None, description="Artifact content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Artifact metadata")


class AnalysisBase(CQIA_BaseModel):
    """Base analysis schema."""

    project_id: str = Field(..., description="Project ID")
    triggered_by: str = Field(..., description="User who triggered analysis")
    commit_hash: Optional[str] = Field(None, description="Commit hash")
    branch: str = Field("main", description="Branch name")
    analysis_type: str = Field("full", description="Analysis type")


class AnalysisCreate(AnalysisBase, CQIA_BaseCreate):
    """Schema for creating an analysis."""

    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis configuration")


class AnalysisUpdate(CQIA_BaseUpdate):
    """Schema for updating an analysis."""

    status: Optional[str] = Field(None, description="Analysis status")
    error_message: Optional[str] = Field(None, description="Error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class AnalysisResponse(AnalysisBase, CQIA_BaseResponse):
    """Schema for analysis response data."""

    status: str = Field(..., description="Analysis status")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")

    # Quality metrics
    quality_score: Optional[float] = Field(None, description="Quality score")
    coverage_percentage: Optional[float] = Field(None, description="Coverage percentage")
    lines_of_code: Optional[int] = Field(None, description="Lines of code")
    files_analyzed: int = Field(..., description="Files analyzed")

    # Issue counts
    total_issues: int = Field(..., description="Total issues")
    critical_issues: int = Field(..., description="Critical issues")
    high_issues: int = Field(..., description="High severity issues")
    medium_issues: int = Field(..., description="Medium severity issues")
    low_issues: int = Field(..., description="Low severity issues")

    # Results and config
    results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    config: Dict[str, Any] = Field(default_factory=dict, description="Analysis configuration")

    # Error information
    error_message: Optional[str] = Field(None, description="Error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")

    # Computed properties
    is_completed: bool = Field(..., description="Completion status")
    is_failed: bool = Field(..., description="Failure status")
    is_running: bool = Field(..., description="Running status")


class AnalysisWithDetails(AnalysisResponse):
    """Analysis response with related data."""

    issues: List[IssueResponse] = Field(default_factory=list, description="Analysis issues")
    artifacts: List[AnalysisArtifactResponse] = Field(default_factory=list, description="Analysis artifacts")
    reports: List[Dict[str, Any]] = Field(default_factory=list, description="Related reports")

    # Issue summary
    issue_summary: Dict[str, Any] = Field(..., description="Issue summary by category and severity")


class AnalysisTrigger(CQIA_BaseModel):
    """Schema for triggering an analysis."""

    analysis_type: str = Field("full", description="Type of analysis")
    branch: Optional[str] = Field(None, description="Branch to analyze")
    commit_hash: Optional[str] = Field(None, description="Specific commit")
    config: Optional[Dict[str, Any]] = Field(None, description="Analysis configuration")


class AnalysisMetrics(CQIA_BaseModel):
    """Schema for analysis metrics."""

    metric_type: str = Field(..., description="Metric type")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    file_path: Optional[str] = Field(None, description="File path")
    function_name: Optional[str] = Field(None, description="Function name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metric metadata")
    measured_at: datetime = Field(..., description="Measurement timestamp")


class AnalysisProgress(CQIA_BaseModel):
    """Schema for analysis progress updates."""

    analysis_id: str = Field(..., description="Analysis ID")
    status: str = Field(..., description="Current status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current processing step")
    message: Optional[str] = Field(None, description="Progress message")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated time remaining in seconds")


class CodeAnalysisRequest(CQIA_BaseModel):
    """Schema for code analysis requests."""

    code: str = Field(..., description="Code to analyze")
    language: str = Field(..., description="Programming language")
    file_path: Optional[str] = Field(None, description="File path")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis configuration")


class CodeAnalysisResponse(CQIA_BaseModel):
    """Schema for code analysis responses."""

    issues: List[IssueResponse] = Field(default_factory=list, description="Found issues")
    metrics: List[AnalysisMetrics] = Field(default_factory=list, description="Code metrics")
    suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Improvement suggestions")
    quality_score: Optional[float] = Field(None, description="Overall quality score")
