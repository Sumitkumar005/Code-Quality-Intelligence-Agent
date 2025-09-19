"""
Pydantic schemas for project-related operations.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from .base import CQIA_BaseModel, CQIA_BaseCreate, CQIA_BaseUpdate, CQIA_BaseResponse


class ProjectBase(CQIA_BaseModel):
    """Base project schema."""

    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    repository_type: str = Field("git", description="Repository type")
    default_branch: str = Field("main", description="Default branch")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks used")


class ProjectCreate(ProjectBase, CQIA_BaseCreate):
    """Schema for creating a new project."""

    organization_id: str = Field(..., description="Organization ID")


class ProjectUpdate(CQIA_BaseUpdate):
    """Schema for updating project information."""

    name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    repository_type: Optional[str] = Field(None, description="Repository type")
    default_branch: Optional[str] = Field(None, description="Default branch")
    languages: Optional[List[str]] = Field(None, description="Programming languages")
    frameworks: Optional[List[str]] = Field(None, description="Frameworks used")
    settings: Optional[dict] = Field(None, description="Project settings")
    analysis_config: Optional[dict] = Field(None, description="Analysis configuration")
    is_active: Optional[bool] = Field(None, description="Project active status")
    is_public: Optional[bool] = Field(None, description="Public visibility")


class ProjectResponse(ProjectBase, CQIA_BaseResponse):
    """Schema for project response data."""

    organization_id: str = Field(..., description="Organization ID")
    created_by: str = Field(..., description="Creator user ID")
    settings: dict = Field(default_factory=dict, description="Project settings")
    analysis_config: dict = Field(default_factory=dict, description="Analysis configuration")
    is_active: bool = Field(..., description="Project active status")
    is_public: bool = Field(..., description="Public visibility")
    last_analysis_at: Optional[datetime] = Field(None, description="Last analysis timestamp")
    analysis_count: int = Field(..., description="Total analysis count")

    # Quality metrics
    quality_score: Optional[float] = Field(None, description="Current quality score")
    issue_count: int = Field(..., description="Total issue count")
    coverage_percentage: Optional[float] = Field(None, description="Code coverage percentage")

    # Computed properties
    repository_name: Optional[str] = Field(None, description="Extracted repository name")
    primary_language: Optional[str] = Field(None, description="Primary programming language")


class ProjectSummary(ProjectResponse):
    """Project summary with trend information."""

    quality_trend: dict = Field(..., description="Quality trend information")


class ProjectWebhookBase(CQIA_BaseModel):
    """Base project webhook schema."""

    url: str = Field(..., description="Webhook URL")
    secret: str = Field(..., description="Webhook secret")
    events: List[str] = Field(default_factory=list, description="Events to trigger on")


class ProjectWebhookCreate(ProjectWebhookBase, CQIA_BaseCreate):
    """Schema for creating a project webhook."""

    project_id: str = Field(..., description="Project ID")


class ProjectWebhookUpdate(CQIA_BaseUpdate):
    """Schema for updating project webhook."""

    url: Optional[str] = Field(None, description="Webhook URL")
    secret: Optional[str] = Field(None, description="Webhook secret")
    events: Optional[List[str]] = Field(None, description="Events to trigger on")
    is_active: Optional[bool] = Field(None, description="Webhook active status")


class ProjectWebhookResponse(ProjectWebhookBase, CQIA_BaseResponse):
    """Schema for project webhook response data."""

    project_id: str = Field(..., description="Project ID")
    is_active: bool = Field(..., description="Webhook active status")
    last_triggered_at: Optional[datetime] = Field(None, description="Last trigger timestamp")
    failure_count: int = Field(..., description="Failure count")


class ProjectWithDetails(ProjectResponse):
    """Project response with related data."""

    organization: Optional[dict] = Field(None, description="Organization information")
    created_by_user: Optional[dict] = Field(None, description="Creator information")
    recent_analyses: List[dict] = Field(default_factory=list, description="Recent analyses")
    webhooks: List[ProjectWebhookResponse] = Field(default_factory=list, description="Project webhooks")


class ProjectAnalysisTrigger(CQIA_BaseModel):
    """Schema for triggering project analysis."""

    analysis_type: str = Field("full", description="Type of analysis to run")
    branch: Optional[str] = Field(None, description="Branch to analyze")
    commit_hash: Optional[str] = Field(None, description="Specific commit to analyze")
    config: Optional[dict] = Field(None, description="Analysis configuration override")


class ProjectQualityMetrics(CQIA_BaseModel):
    """Schema for project quality metrics."""

    quality_score: Optional[float] = Field(None, description="Overall quality score")
    coverage_percentage: Optional[float] = Field(None, description="Code coverage percentage")
    issue_count: int = Field(..., description="Total issue count")
    critical_issues: int = Field(..., description="Critical issue count")
    high_issues: int = Field(..., description="High severity issue count")
    medium_issues: int = Field(..., description="Medium severity issue count")
    low_issues: int = Field(..., description="Low severity issue count")
    lines_of_code: Optional[int] = Field(None, description="Lines of code")
    files_analyzed: int = Field(..., description="Files analyzed")
    last_updated: datetime = Field(..., description="Last metrics update")
