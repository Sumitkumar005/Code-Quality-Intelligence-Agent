"""
Project schemas for API v1.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProjectResponse(BaseModel):
    """Project response schema."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    repository_type: str = Field(default="git", description="Repository type")
    default_branch: str = Field(default="main", description="Default branch")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project settings")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created the project")


class ProjectCreate(BaseModel):
    """Project creation schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    repository_type: str = Field(default="git", description="Repository type")
    default_branch: str = Field(default="main", description="Default branch")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project settings")


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    repository_type: Optional[str] = Field(None, description="Repository type")
    default_branch: Optional[str] = Field(None, description="Default branch")
    languages: Optional[List[str]] = Field(None, description="Programming languages")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")


class ProjectListResponse(BaseModel):
    """Project list response schema."""
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ProjectWithStats(ProjectResponse):
    """Project with statistics schema."""
    analysis_count: int = Field(default=0, description="Number of analyses")
    last_analysis: Optional[datetime] = Field(None, description="Last analysis timestamp")
    total_issues: int = Field(default=0, description="Total number of issues")
    critical_issues: int = Field(default=0, description="Number of critical issues")
    quality_score: Optional[float] = Field(None, description="Overall quality score")
