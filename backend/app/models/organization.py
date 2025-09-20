"""
Organization models for database entities.
"""

from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, DateTime  # Add DateTime to imports
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

from app.models.base import CQIA_Base


class Organization(CQIA_Base):
    """Organization model."""
    __tablename__ = "organizations"
    __table_args__ = {"extend_existing": True}

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="organization", cascade="all, delete-orphan"
    )
    webhooks: Mapped[List["OrganizationWebhook"]] = relationship(
        "OrganizationWebhook", back_populates="organization", cascade="all, delete-orphan"
    )
    invites: Mapped[List["OrganizationInvite"]] = relationship(
        "OrganizationInvite", back_populates="organization", cascade="all, delete-orphan"
    )
    webhook_deliveries: Mapped[List["OrganizationWebhookDelivery"]] = relationship(
        "OrganizationWebhookDelivery", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name})>"


class OrganizationMember(CQIA_Base):
    """Organization member model."""
    __tablename__ = "organization_members"
    __table_args__ = {"extend_existing": True}

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    permissions: Mapped[List] = mapped_column(JSON, default=list, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invited_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")

    def __repr__(self):
        return f"<OrganizationMember(id={self.id}, organization_id={self.organization_id}, user_id={self.user_id}, role={self.role})>"


class OrganizationInvite(CQIA_Base):
    """Organization invite model."""
    __tablename__ = "organization_invites"
    __table_args__ = {"extend_existing": True}

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    permissions: Mapped[List] = mapped_column(JSON, default=list, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    invited_by: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="invites")

    def __repr__(self):
        return f"<OrganizationInvite(id={self.id}, organization_id={self.organization_id}, email={self.email})>"


class OrganizationWebhook(CQIA_Base):
    """Organization webhook model."""
    __tablename__ = "organization_webhooks"
    __table_args__ = {"extend_existing": True}

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    events: Mapped[List] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    retry_policy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="webhooks")
    deliveries: Mapped[List["OrganizationWebhookDelivery"]] = relationship(
        "OrganizationWebhookDelivery", back_populates="webhook", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<OrganizationWebhook(id={self.id}, organization_id={self.organization_id}, name={self.name})>"


class OrganizationWebhookDelivery(CQIA_Base):
    """Organization webhook delivery model."""
    __tablename__ = "organization_webhook_deliveries"
    __table_args__ = {"extend_existing": True}

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    webhook_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organization_webhooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_headers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="webhook_deliveries")
    webhook: Mapped["OrganizationWebhook"] = relationship("OrganizationWebhook", back_populates="deliveries")

    def __repr__(self):
        return f"<OrganizationWebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, success={self.success})>"


# Indexes for better query performance
from sqlalchemy import Index

Index("ix_organization_members_org_user", "organization_members.organization_id", "organization_members.user_id", unique=True)
Index("ix_organization_invites_org_email", "organization_invites.organization_id", "organization_invites.email")
Index("ix_organization_invites_token", "organization_invites.token", unique=True)
Index("ix_organization_webhooks_org_active", "organization_webhooks.organization_id", "organization_webhooks.is_active")
Index("ix_organization_webhook_deliveries_webhook_event", "organization_webhook_deliveries.webhook_id", "organization_webhook_deliveries.event_type")
Index("ix_organization_webhook_deliveries_org_event", "organization_webhook_deliveries.organization_id", "organization_webhook_deliveries.event_type")