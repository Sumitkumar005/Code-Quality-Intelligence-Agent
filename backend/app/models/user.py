"""
User model and related database entities.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, String, Text, ForeignKey, Integer, UniqueConstraint, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import CQIA_Base


class User(CQIA_Base):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    # Authentication fields
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Status fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Metadata
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Settings and preferences
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    organizations: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="user", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="created_by_user", foreign_keys="Project.created_by"
    )
    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis", back_populates="triggered_by_user"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="generated_by_user"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )

    @property
    def is_admin(self) -> bool:
        """Check if user is admin in any organization."""
        return any(member.role == "admin" for member in self.organizations)

    @property
    def is_owner(self) -> bool:
        """Check if user is owner in any organization."""
        return any(member.role == "owner" for member in self.organizations)

    def get_organizations(self) -> List["Organization"]:
        """Get all organizations user belongs to."""
        return [member.organization for member in self.organizations]

    def get_permissions(self, organization_id: Optional[str] = None) -> List[str]:
        """Get user permissions, optionally filtered by organization."""
        from app.core.security import get_role_permissions

        permissions = set()

        for member in self.organizations:
            if organization_id and member.organization_id != organization_id:
                continue

            role_permissions = get_role_permissions(member.role)
            permissions.update(role_permissions)

        # Superuser gets all permissions
        if self.is_superuser:
            from app.core.security import PERMISSIONS
            permissions.update(PERMISSIONS.keys())

        return list(permissions)

    def can_access_project(self, project_id: str) -> bool:
        """Check if user can access a specific project."""
        # Superuser can access all projects
        if self.is_superuser:
            return True

        # Check if user belongs to the project's organization
        for member in self.organizations:
            if member.organization_id == project.organization_id:
                return True

        return False

    def can_manage_project(self, project_id: str) -> bool:
        """Check if user can manage (edit/delete) a project."""
        if self.is_superuser:
            return True

        for member in self.organizations:
            if member.organization_id == project.organization_id and member.role in ["admin", "owner"]:
                return True

        return False


class Organization(CQIA_Base):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Settings
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    features: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Billing and limits
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_projects: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="organization", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="organization"
    )

    @property
    def member_count(self) -> int:
        """Get current member count."""
        return len(self.members)

    @property
    def project_count(self) -> int:
        """Get current project count."""
        return len(self.projects)

    def can_add_user(self) -> bool:
        """Check if organization can add more users."""
        return self.member_count < self.max_users

    def can_add_project(self) -> bool:
        """Check if organization can add more projects."""
        return self.project_count < self.max_projects


class OrganizationMember(CQIA_Base):
    """Organization membership model."""

    __tablename__ = "organization_members"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="organizations")

    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', name='unique_org_user'),
    )
