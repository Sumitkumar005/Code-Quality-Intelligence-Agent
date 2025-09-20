"""
Webhook models for database entities.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import Base


class Webhook(Base):
    """Webhook model."""
    __tablename__ = "webhooks"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    events = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    secret = Column(String(255), nullable=True)
    headers = Column(JSON, default=dict, nullable=False)
    retry_policy = Column(JSON, default=dict, nullable=False)

    # Foreign keys
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = Column(String(36), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="webhooks")
    organization = relationship("Organization", back_populates="webhooks")
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")
    logs = relationship("WebhookLogEntry", back_populates="webhook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Webhook(id={self.id}, name={self.name}, project_id={self.project_id})>"


class WebhookDelivery(Base):
    """Webhook delivery model."""
    __tablename__ = "webhook_deliveries"

    id = Column(String(36), primary_key=True, index=True)
    webhook_id = Column(String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_headers = Column(JSON, default=dict, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)

    # Foreign keys
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)

    # Timestamps
    delivered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")
    project = relationship("Project", back_populates="webhook_deliveries")
    organization = relationship("Organization", back_populates="webhook_deliveries")

    def __repr__(self):
        return f"<WebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, success={self.success})>"


class WebhookEvent(Base):
    """Webhook event model."""
    __tablename__ = "webhook_events"

    id = Column(String(36), primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(36), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    metadata = Column(JSON, default=dict, nullable=False)

    # Foreign keys
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)

    # Timestamps
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False, default="system")

    # Relationships
    project = relationship("Project", back_populates="webhook_events")
    organization = relationship("Organization", back_populates="webhook_events")

    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_type={self.event_type}, resource_type={self.resource_type})>"


class WebhookTemplate(Base):
    """Webhook template model."""
    __tablename__ = "webhook_templates"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload_template = Column(Text, nullable=False)
    headers_template = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Foreign keys
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = Column(String(36), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="webhook_templates")
    organization = relationship("Organization", back_populates="webhook_templates")

    def __repr__(self):
        return f"<WebhookTemplate(id={self.id}, name={self.name}, event_type={self.event_type})>"


class WebhookLogEntry(Base):
    """Webhook log entry model."""
    __tablename__ = "webhook_logs"

    id = Column(String(36), primary_key=True, index=True)
    webhook_id = Column(String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    event_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(36), nullable=True, index=True)
    metadata = Column(JSON, default=dict, nullable=False)

    # Foreign keys
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    webhook = relationship("Webhook", back_populates="logs")
    project = relationship("Project", back_populates="webhook_logs")
    organization = relationship("Organization", back_populates="webhook_logs")

    def __repr__(self):
        return f"<WebhookLogEntry(id={self.id}, webhook_id={self.webhook_id}, level={self.level})>"


class WebhookSignature(Base):
    """Webhook signature model for verification."""
    __tablename__ = "webhook_signatures"

    id = Column(String(36), primary_key=True, index=True)
    webhook_id = Column(String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True)
    signature = Column(String(255), nullable=False)
    algorithm = Column(String(20), nullable=False, default="sha256")
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Foreign keys
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)

    # Relationships
    webhook = relationship("Webhook", back_populates="signatures")
    project = relationship("Project", back_populates="webhook_signatures")
    organization = relationship("Organization", back_populates="webhook_signatures")

    def __repr__(self):
        return f"<WebhookSignature(id={self.id}, webhook_id={self.webhook_id}, algorithm={self.algorithm})>"


# Indexes for better query performance
from sqlalchemy import Index

Index("ix_webhooks_project_active", Webhook.project_id, Webhook.is_active)
Index("ix_webhooks_org_active", Webhook.organization_id, Webhook.is_active)
Index("ix_webhook_deliveries_webhook_success", WebhookDelivery.webhook_id, WebhookDelivery.success)
Index("ix_webhook_deliveries_event_success", WebhookDelivery.event_type, WebhookDelivery.success)
Index("ix_webhook_events_resource_action", WebhookEvent.resource_type, WebhookEvent.resource_id, WebhookEvent.action)
Index("ix_webhook_events_occurred_at", WebhookEvent.occurred_at)
Index("ix_webhook_logs_webhook_level", WebhookLogEntry.webhook_id, WebhookLogEntry.level)
Index("ix_webhook_logs_created_at", WebhookLogEntry.created_at)
Index("ix_webhook_templates_event_active", WebhookTemplate.event_type, WebhookTemplate.is_active)
Index("ix_webhook_signatures_webhook_timestamp", WebhookSignature.webhook_id, WebhookSignature.timestamp)
