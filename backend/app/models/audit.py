"""
Audit log model for tracking system activities and changes.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import CQIA_Base


class AuditLog(CQIA_Base):
    """Audit log model for tracking system activities."""

    __tablename__ = "audit_logs"

    # Actor information
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="SET NULL")
    )

    # Activity information
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36))

    # Change details
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    changes: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Context information
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    session_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Additional metadata
    audit_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="audit_logs")

    @property
    def action_description(self) -> str:
        """Get human-readable action description."""
        return f"{self.action.replace('_', ' ').title()} {self.resource_type}"

    @property
    def has_changes(self) -> bool:
        """Check if this log entry represents actual changes."""
        return self.changes is not None and len(self.changes) > 0

    def get_change_summary(self) -> dict:
        """Get summary of changes made."""
        if not self.changes:
            return {}

        summary = {
            "fields_changed": list(self.changes.keys()),
            "change_count": len(self.changes)
        }

        # Add details for common field types
        if "is_active" in self.changes:
            summary["status_change"] = "activated" if self.changes["is_active"]["new"] else "deactivated"

        return summary


class AuditLogArchive(CQIA_Base):
    """Archived audit logs for long-term storage."""

    __tablename__ = "audit_logs_archive"

    # Original log data (compressed JSON)
    log_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Archive metadata
    archive_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    archive_reason: Mapped[str] = mapped_column(String(100), default="age", nullable=False)

    # Compression info
    original_size: Mapped[int] = mapped_column(Integer, nullable=False)
    compressed_size: Mapped[int] = mapped_column(Integer, nullable=False)


# Audit log categories and actions
AUDIT_ACTIONS = {
    # User actions
    "user_login": "User authentication",
    "user_logout": "User logout",
    "user_created": "User account creation",
    "user_updated": "User profile update",
    "user_deleted": "User account deletion",
    "user_password_changed": "Password change",

    # Organization actions
    "organization_created": "Organization creation",
    "organization_updated": "Organization update",
    "organization_deleted": "Organization deletion",
    "organization_member_added": "Member added to organization",
    "organization_member_removed": "Member removed from organization",
    "organization_member_role_changed": "Member role changed",

    # Project actions
    "project_created": "Project creation",
    "project_updated": "Project update",
    "project_deleted": "Project deletion",
    "project_analyzed": "Project analysis triggered",

    # Analysis actions
    "analysis_started": "Analysis started",
    "analysis_completed": "Analysis completed",
    "analysis_failed": "Analysis failed",
    "analysis_cancelled": "Analysis cancelled",

    # Report actions
    "report_generated": "Report generation",
    "report_downloaded": "Report download",

    # Conversation actions
    "conversation_created": "Conversation started",
    "conversation_message_sent": "Message sent in conversation",

    # System actions
    "system_backup": "System backup",
    "system_restore": "System restore",
    "system_config_changed": "System configuration change",
}

RESOURCE_TYPES = [
    "user",
    "organization",
    "project",
    "analysis",
    "report",
    "conversation",
    "webhook",
    "api_key",
    "system",
]


def create_audit_log(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    changes: Optional[dict] = None,
    metadata: Optional[dict] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[str] = None,
) -> AuditLog:
    """Create a new audit log entry."""
    return AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        organization_id=organization_id,
        old_values=old_values,
        new_values=new_values,
        changes=changes,
        metadata=metadata or {},
        success=success,
        error_message=error_message,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
    )


def log_user_action(
    action: str,
    user_id: str,
    resource_type: str = "user",
    resource_id: Optional[str] = None,
    **kwargs
) -> AuditLog:
    """Log a user-related action."""
    return create_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        **kwargs
    )


def log_organization_action(
    action: str,
    organization_id: str,
    user_id: Optional[str] = None,
    resource_type: str = "organization",
    resource_id: Optional[str] = None,
    **kwargs
) -> AuditLog:
    """Log an organization-related action."""
    return create_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        organization_id=organization_id,
        **kwargs
    )


def log_project_action(
    action: str,
    project_id: str,
    user_id: str,
    organization_id: str,
    resource_type: str = "project",
    **kwargs
) -> AuditLog:
    """Log a project-related action."""
    return create_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=project_id,
        user_id=user_id,
        organization_id=organization_id,
        **kwargs
    )
