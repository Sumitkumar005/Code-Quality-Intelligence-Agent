"""
Report model and related database entities.
"""

from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import CQIA_Base


class Report(CQIA_Base):
    """Report model for generated analysis reports."""

    __tablename__ = "reports"

    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    generated_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Report metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), default="analysis", nullable=False)
    format: Mapped[str] = mapped_column(String(20), default="html", nullable=False)

    # Content
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # File storage
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    download_url: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="reports")
    generated_by_user: Mapped["User"] = relationship("User", back_populates="reports")

    @property
    def is_downloadable(self) -> bool:
        """Check if report can be downloaded."""
        return self.file_path is not None and not self.is_archived

    def get_download_url(self) -> Optional[str]:
        """Get download URL for the report."""
        if self.download_url:
            return self.download_url
        elif self.file_path:
            # Generate download URL based on file path
            return f"/api/v1/reports/{self.id}/download"
        return None


class ReportTemplate(CQIA_Base):
    """Report template model for customizable report formats."""

    __tablename__ = "report_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Template content
    template_content: Mapped[str] = mapped_column(Text, nullable=False)
    template_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Metadata
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
