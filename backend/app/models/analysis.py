"""
Analysis model and related database entities.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Boolean, Float, Integer, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum as PyEnum

from .base import CQIA_Base


class AnalysisStatus(str, PyEnum):
    """Analysis status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisType(str, PyEnum):
    """Analysis type enumeration."""
    FULL = "full"
    INCREMENTAL = "incremental"
    SECURITY = "security"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    DEPENDENCY = "dependency"


class Analysis(CQIA_Base):
    """Analysis model for code analysis results."""

    __tablename__ = "analyses"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    triggered_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Analysis metadata
    commit_hash: Mapped[Optional[str]] = mapped_column(String(40))
    branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    analysis_type: Mapped[AnalysisType] = mapped_column(
        Enum(AnalysisType), default=AnalysisType.FULL, nullable=False
    )

    # Status and timing
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    coverage_percentage: Mapped[Optional[float]] = mapped_column(Float)
    lines_of_code: Mapped[Optional[int]] = mapped_column(Integer)
    files_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Issue counts
    total_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Analysis results
    results: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Error information
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="analyses")
    triggered_by_user: Mapped["User"] = relationship("User", back_populates="analyses")
    issues: Mapped[List["Issue"]] = relationship(
        "Issue", back_populates="analysis", cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="analysis", cascade="all, delete-orphan"
    )

    @property
    def is_completed(self) -> bool:
        """Check if analysis is completed."""
        return self.status == AnalysisStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if analysis failed."""
        return self.status == AnalysisStatus.FAILED

    @property
    def is_running(self) -> bool:
        """Check if analysis is currently running."""
        return self.status == AnalysisStatus.RUNNING

    def mark_started(self):
        """Mark analysis as started."""
        self.status = AnalysisStatus.RUNNING
        self.started_at = datetime.utcnow()

    def mark_completed(self, quality_score: Optional[float] = None):
        """Mark analysis as completed."""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        if quality_score is not None:
            self.quality_score = quality_score

    def mark_failed(self, error_message: str, error_details: Optional[dict] = None):
        """Mark analysis as failed."""
        self.status = AnalysisStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if error_details:
            self.error_details = error_details
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

    def update_issue_counts(self):
        """Update issue counts from related issues."""
        self.total_issues = len(self.issues)
        self.critical_issues = sum(1 for issue in self.issues if issue.severity == "critical")
        self.high_issues = sum(1 for issue in self.issues if issue.severity == "high")
        self.medium_issues = sum(1 for issue in self.issues if issue.severity == "medium")
        self.low_issues = sum(1 for issue in self.issues if issue.severity == "low")

    def get_issue_summary(self) -> dict:
        """Get summary of issues by category and severity."""
        summary = {
            "total": self.total_issues,
            "by_severity": {
                "critical": self.critical_issues,
                "high": self.high_issues,
                "medium": self.medium_issues,
                "low": self.low_issues,
            },
            "by_category": {}
        }

        for issue in self.issues:
            category = issue.category or "other"
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1

        return summary


class Issue(CQIA_Base):
    """Issue model for individual code analysis findings."""

    __tablename__ = "issues"

    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )

    # Issue details
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)

    # Location information
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[Optional[int]] = mapped_column(Integer)
    column_number: Mapped[Optional[int]] = mapped_column(Integer)
    function_name: Mapped[Optional[str]] = mapped_column(String(255))

    # Issue content
    message: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    code_snippet: Mapped[Optional[str]] = mapped_column(Text)

    # Additional metadata
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    effort_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    tags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Status
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_by: Mapped[Optional[str]] = mapped_column(String(36))

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="issues")

    @property
    def location_string(self) -> str:
        """Get formatted location string."""
        location = self.file_path
        if self.line_number:
            location += f":{self.line_number}"
            if self.column_number:
                location += f":{self.column_number}"
        return location

    def mark_resolved(self, resolved_by: str):
        """Mark issue as resolved."""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by = resolved_by


class AnalysisArtifact(CQIA_Base):
    """Analysis artifact model for storing generated files."""

    __tablename__ = "analysis_artifacts"

    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )

    # Artifact metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Content (for small artifacts)
    content: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis")
