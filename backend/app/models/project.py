"""
Project model and related database entities.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Boolean, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import CQIA_Base


class Project(CQIA_Base):
    """Project model for code analysis projects."""

    __tablename__ = "projects"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Basic project info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    repository_url: Mapped[Optional[str]] = mapped_column(Text)
    repository_type: Mapped[str] = mapped_column(String(20), default="git", nullable=False)

    # Repository settings
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    languages: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    frameworks: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Project settings
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    analysis_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Status and metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_analysis_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    analysis_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Quality metrics (cached)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    issue_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coverage_percentage: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="projects")
    created_by_user: Mapped["User"] = relationship("User", back_populates="projects", foreign_keys=[created_by])
    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis", back_populates="project", cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="project", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def repository_name(self) -> Optional[str]:
        """Extract repository name from URL."""
        if not self.repository_url:
            return None

        # Handle GitHub/GitLab URLs
        if "github.com" in self.repository_url or "gitlab.com" in self.repository_url:
            parts = self.repository_url.rstrip("/").split("/")
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"

        return self.repository_url.split("/")[-1] if "/" in self.repository_url else self.repository_url

    @property
    def primary_language(self) -> Optional[str]:
        """Get the primary programming language."""
        return self.languages[0] if self.languages else None

    def get_recent_analyses(self, limit: int = 5) -> List["Analysis"]:
        """Get recent analyses for this project."""
        return sorted(
            self.analyses,
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]

    def get_quality_trend(self) -> dict:
        """Calculate quality trend over time."""
        analyses = sorted(self.analyses, key=lambda x: x.created_at)
        if not analyses:
            return {"trend": "stable", "change": 0.0}

        recent_scores = [a.quality_score for a in analyses[-10:] if a.quality_score is not None]
        if len(recent_scores) < 2:
            return {"trend": "stable", "change": 0.0}

        change = recent_scores[-1] - recent_scores[0]
        if change > 5:
            trend = "improving"
        elif change < -5:
            trend = "declining"
        else:
            trend = "stable"

        return {"trend": trend, "change": round(change, 2)}

    def update_quality_metrics(self):
        """Update cached quality metrics from recent analyses."""
        if not self.analyses:
            return

        # Get latest analysis
        latest_analysis = max(self.analyses, key=lambda x: x.created_at)

        # Update metrics
        self.quality_score = latest_analysis.quality_score
        self.issue_count = sum(len(analysis.issues) for analysis in self.analyses)
        self.coverage_percentage = latest_analysis.coverage_percentage
        self.last_analysis_at = latest_analysis.created_at
        self.analysis_count = len(self.analyses)


class ProjectWebhook(CQIA_Base):
    """Webhook configuration for projects."""

    __tablename__ = "project_webhooks"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Webhook configuration
    url: Mapped[str] = mapped_column(Text, nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    events: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project")

    def should_trigger_for_event(self, event_type: str) -> bool:
        """Check if webhook should trigger for given event."""
        return event_type in self.events or "all" in self.events

    def record_trigger(self, success: bool = True):
        """Record webhook trigger attempt."""
        self.last_triggered_at = datetime.utcnow()
        if not success:
            self.failure_count += 1
        else:
            self.failure_count = 0  # Reset on success
