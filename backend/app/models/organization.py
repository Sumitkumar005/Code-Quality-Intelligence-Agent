"""
Organization models for database entities.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import Base


class Organization(Base):
    """Organization model."""
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    settings = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    webhooks = relationship("OrganizationWebhook", back_populates="organization", cascade="all, delete-orphan")
    invites = relationship("OrganizationInvite", back_populates="organization", cascade="all, delete-orphan")
    webhook_deliveries = relationship("OrganizationWebhookDelivery", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name})>"


class OrganizationMember(Base):
    """Organization member model."""
    __tablename__ = "organization_members"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="member")
    permissions = Column(JSON, default=list, nullable=False)

    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invited_by = Column(String(36), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="members")

    def __repr__(self):
        return f"<OrganizationMember(id={self.id}, organization_id={self.organization_id}, user_id={self.user_id}, role={self.role})>"


class OrganizationInvite(Base):
    """Organization invite model."""
    __tablename__ = "organization_invites"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="member")
    permissions = Column(JSON, default=list, nullable=False)
    message = Column(Text, nullable=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invited_by = Column(String(36), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="invites")

    def __repr__(self):
        return f"<OrganizationInvite(id={self.id}, organization_id={self.organization_id}, email={self.email})>"


class OrganizationWebhook(Base):
    """Organization webhook model."""
    __tablename__ = "organization_webhooks"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    events = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    secret = Column(String(255), nullable=True)
    headers = Column(JSON, default=dict, nullable=False)
    retry_policy = Column(JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(36), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="webhooks")
    deliveries = relationship("OrganizationWebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OrganizationWebhook(id={self.id}, organization_id={self.organization_id}, name={self.name})>"


class OrganizationWebhookDelivery(Base):
    """Organization webhook delivery model."""
    __tablename__ = "organization_webhook_deliveries"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    webhook_id = Column(String(36), ForeignKey("organization_webhooks.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_headers = Column(JSON, default=dict, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)

    # Timestamps
    delivered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="webhook_deliveries")
    webhook = relationship("OrganizationWebhook", back_populates="deliveries")

    def __repr__(self):
        return f"<OrganizationWebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, success={self.success})>"


# Indexes for better query performance
from sqlalchemy import Index

Index("ix_organization_members_org_user", OrganizationMember.organization_id, OrganizationMember.user_id, unique=True)
Index("ix_organization_invites_org_email", OrganizationInvite.organization_id, OrganizationInvite.email)
Index("ix_organization_invites_token", OrganizationInvite.token, unique=True)
Index("ix_organization_webhooks_org_active", OrganizationWebhook.organization_id, OrganizationWebhook.is_active)
Index("ix_organization_webhook_deliveries_webhook_event", OrganizationWebhookDelivery.webhook_id, OrganizationWebhookDelivery.event_type)
Index("ix_organization_webhook_deliveries_org_event", OrganizationWebhookDelivery.organization_id, OrganizationWebhookDelivery.event_type)
