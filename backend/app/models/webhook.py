"""
Webhook models for database entities.
"""

from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

from app.models.base import CQIA_Base  # Changed from Base to CQIA_Base


class Webhook(CQIA_Base):
    """Webhook model."""
    __tablename__ = "webhooks"
    __table_args__ = {"extend_existing": True}

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    events: Mapped[List] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    retry_policy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="webhooks")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="webhooks")
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan"
    )
    logs: Mapped[List["WebhookLogEntry"]] = relationship(
        "WebhookLogEntry", back_populates="webhook", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Webhook(id={self.id}, name={self.name}, project_id={self.project_id})>"


class WebhookDelivery(CQIA_Base):
    """Webhook delivery model."""
    __tablename__ = "webhook_deliveries"
    __table_args__ = {"extend_existing": True}

    webhook_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True
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
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="deliveries")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="webhook_deliveries")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="webhook_deliveries")

    def __repr__(self):
        return f"<WebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, success={self.success})>"


class WebhookEvent(CQIA_Base):
    """Webhook event model."""
    __tablename__ = "webhook_events"
    __table_args__ = {"extend_existing": True}

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Renamed from metadata
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="system")

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="webhook_events")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="webhook_events")

    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_type={self.event_type}, resource_type={self.resource_type})>"


class WebhookTemplate(CQIA_Base):
    """Webhook template model."""
    __tablename__ = "webhook_templates"
    __table_args__ = {"extend_existing": True}

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_template: Mapped[str] = mapped_column(Text, nullable=False)
    headers_template: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="webhook_templates")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="webhook_templates")

    def __repr__(self):
        return f"<WebhookTemplate(id={self.id}, name={self.name}, event_type={self.event_type})>"


class WebhookLogEntry(CQIA_Base):
    """Webhook log entry model."""
    __tablename__ = "webhook_logs"
    __table_args__ = {"extend_existing": True}

    webhook_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    log_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Renamed from metadata
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="logs")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="webhook_logs")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="webhook_logs")

    def __repr__(self):
        return f"<WebhookLogEntry(id={self.id}, webhook_id={self.webhook_id}, level={self.level})>"


class WebhookSignature(CQIA_Base):
    """Webhook signature model for verification."""
    __tablename__ = "webhook_signatures"
    __table_args__ = {"extend_existing": True}

    webhook_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    signature: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(20), nullable=False, default="sha256")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="signatures")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="webhook_signatures")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="webhook_signatures")

    def __repr__(self):
        return f"<WebhookSignature(id={self.id}, webhook_id={self.webhook_id}, algorithm={self.algorithm})>"


# Indexes for better query performance
from sqlalchemy import Index

Index("ix_webhooks_project_active", "webhooks.project_id", "webhooks.is_active")
Index("ix_webhooks_org_active", "webhooks.organization_id", "webhooks.is_active")
Index("ix_webhook_deliveries_webhook_success", "webhook_deliveries.webhook_id", "webhook_deliveries.success")
Index("ix_webhook_deliveries_event_success", "webhook_deliveries.event_type", "webhook_deliveries.success")
Index("ix_webhook_events_resource_action", "webhook_events.resource_type", "webhook_events.resource_id", "webhook_events.action")
Index("ix_webhook_events_occurred_at", "webhook_events.occurred_at")
Index("ix_webhook_logs_webhook_level", "webhook_logs.webhook_id", "webhook_logs.level")
Index("ix_webhook_logs_created_at", "webhook_logs.created_at")
Index("ix_webhook_templates_event_active", "webhook_templates.event_type", "webhook_templates.is_active")
Index("ix_webhook_signatures_webhook_timestamp", "webhook_signatures.webhook_id", "webhook_signatures.timestamp")