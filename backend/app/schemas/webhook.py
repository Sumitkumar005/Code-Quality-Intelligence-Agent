"""
Webhook schemas for API validation and serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class WebhookBase(BaseModel):
    """Base webhook schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Webhook name")
    url: str = Field(..., description="Webhook URL endpoint")
    description: Optional[str] = Field(None, max_length=500, description="Webhook description")
    events: List[str] = Field(default_factory=list, description="Events that trigger this webhook")
    is_active: bool = Field(default=True, description="Whether the webhook is active")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional headers to send")
    retry_policy: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Retry policy configuration")


class WebhookCreate(WebhookBase):
    """Schema for creating a new webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    secret: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    retry_policy: Optional[Dict[str, Any]] = None


class WebhookInDBBase(WebhookBase):
    """Base schema for webhook in database."""
    id: str = Field(..., description="Webhook unique identifier")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    organization_id: Optional[str] = Field(None, description="Associated organization ID")
    created_by: str = Field(..., description="User who created the webhook")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_triggered_at: Optional[datetime] = Field(None, description="Last time webhook was triggered")

    class Config:
        from_attributes = True


class Webhook(WebhookInDBBase):
    """Complete webhook schema."""
    pass


class WebhookWithStats(WebhookInDBBase):
    """Webhook schema with delivery statistics."""
    total_deliveries: int = Field(default=0, description="Total number of deliveries")
    successful_deliveries: int = Field(default=0, description="Number of successful deliveries")
    failed_deliveries: int = Field(default=0, description="Number of failed deliveries")
    average_response_time: Optional[float] = Field(None, description="Average response time in milliseconds")
    last_success_at: Optional[datetime] = Field(None, description="Last successful delivery")
    last_failure_at: Optional[datetime] = Field(None, description="Last failed delivery")


class WebhookDeliveryBase(BaseModel):
    """Base webhook delivery schema."""
    webhook_id: str = Field(..., description="Webhook that made the delivery")
    event_type: str = Field(..., description="Type of event that triggered delivery")
    payload: Dict[str, Any] = Field(..., description="Payload sent to webhook")
    response_status: Optional[int] = Field(None, description="HTTP response status code")
    response_body: Optional[str] = Field(None, description="HTTP response body")
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP response headers")
    duration_ms: Optional[int] = Field(None, description="Time taken for delivery in milliseconds")
    attempt_number: int = Field(default=1, description="Delivery attempt number")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")


class WebhookDeliveryCreate(WebhookDeliveryBase):
    """Schema for creating a webhook delivery record."""
    pass


class WebhookDeliveryInDBBase(WebhookDeliveryBase):
    """Base schema for webhook delivery in database."""
    id: str = Field(..., description="Delivery unique identifier")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    organization_id: Optional[str] = Field(None, description="Associated organization ID")
    delivered_at: datetime = Field(..., description="When the delivery was made")
    success: bool = Field(..., description="Whether the delivery was successful")

    class Config:
        from_attributes = True


class WebhookDelivery(WebhookDeliveryInDBBase):
    """Complete webhook delivery schema."""
    pass


class WebhookEventBase(BaseModel):
    """Base webhook event schema."""
    event_type: str = Field(..., description="Type of event")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: str = Field(..., description="ID of affected resource")
    action: str = Field(..., description="Action performed")
    data: Dict[str, Any] = Field(..., description="Event data")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")


class WebhookEvent(WebhookEventBase):
    """Complete webhook event schema."""
    id: str = Field(..., description="Event unique identifier")
    occurred_at: datetime = Field(..., description="When the event occurred")
    source: str = Field(..., description="Source of the event")


class WebhookSignature(BaseModel):
    """Webhook signature verification schema."""
    signature: str = Field(..., description="HMAC signature")
    algorithm: str = Field(default="sha256", description="Signature algorithm")
    timestamp: datetime = Field(..., description="Signature timestamp")


class WebhookRetryPolicy(BaseModel):
    """Webhook retry policy configuration."""
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum number of retry attempts")
    backoff_multiplier: float = Field(default=2.0, ge=1.0, description="Backoff multiplier for retries")
    initial_delay_seconds: int = Field(default=1, ge=0, description="Initial delay before first retry")
    max_delay_seconds: int = Field(default=60, ge=1, description="Maximum delay between retries")
    retryable_status_codes: List[int] = Field(
        default_factory=lambda: [429, 500, 502, 503, 504],
        description="HTTP status codes that should trigger retries"
    )


class WebhookFilter(BaseModel):
    """Webhook filtering configuration."""
    event_types: Optional[List[str]] = Field(None, description="Allowed event types")
    resource_types: Optional[List[str]] = Field(None, description="Allowed resource types")
    actions: Optional[List[str]] = Field(None, description="Allowed actions")
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filtering conditions")


class WebhookTemplateBase(BaseModel):
    """Base webhook template schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    event_type: str = Field(..., description="Event type this template handles")
    payload_template: str = Field(..., description="JSON template for webhook payload")
    headers_template: Optional[Dict[str, str]] = Field(default_factory=dict, description="Template for headers")
    is_active: bool = Field(default=True, description="Whether the template is active")


class WebhookTemplateCreate(WebhookTemplateBase):
    """Schema for creating a webhook template."""
    pass


class WebhookTemplateUpdate(BaseModel):
    """Schema for updating a webhook template."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    payload_template: Optional[str] = None
    headers_template: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


class WebhookTemplateInDBBase(WebhookTemplateBase):
    """Base schema for webhook template in database."""
    id: str = Field(..., description="Template unique identifier")
    created_by: str = Field(..., description="User who created the template")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    usage_count: int = Field(default=0, description="Number of times template has been used")

    class Config:
        from_attributes = True


class WebhookTemplate(WebhookTemplateInDBBase):
    """Complete webhook template schema."""
    pass


class WebhookLogEntryBase(BaseModel):
    """Base webhook log entry schema."""
    webhook_id: str = Field(..., description="Webhook that generated this log entry")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    event_type: Optional[str] = Field(None, description="Related event type")
    resource_id: Optional[str] = Field(None, description="Related resource ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional log metadata")


class WebhookLogEntryInDBBase(WebhookLogEntryBase):
    """Base schema for webhook log entry in database."""
    id: str = Field(..., description="Log entry unique identifier")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    organization_id: Optional[str] = Field(None, description="Associated organization ID")
    created_at: datetime = Field(..., description="Log entry timestamp")

    class Config:
        from_attributes = True


class WebhookLogEntry(WebhookLogEntryInDBBase):
    """Complete webhook log entry schema."""
    pass


# Response schemas
class WebhookListResponse(BaseModel):
    """Response schema for listing webhooks."""
    webhooks: List[Webhook] = Field(..., description="List of webhooks")
    total: int = Field(..., description="Total number of webhooks")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class WebhookDetailResponse(BaseModel):
    """Response schema for webhook details."""
    webhook: Webhook = Field(..., description="Webhook information")
    recent_deliveries: List[WebhookDelivery] = Field(default_factory=list, description="Recent deliveries")
    statistics: Optional[Dict[str, Any]] = Field(None, description="Webhook statistics")


class WebhookDeliveryListResponse(BaseModel):
    """Response schema for listing webhook deliveries."""
    deliveries: List[WebhookDelivery] = Field(..., description="List of deliveries")
    total: int = Field(..., description="Total number of deliveries")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class WebhookTemplateListResponse(BaseModel):
    """Response schema for listing webhook templates."""
    templates: List[WebhookTemplate] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class WebhookLogListResponse(BaseModel):
    """Response schema for listing webhook logs."""
    logs: List[WebhookLogEntry] = Field(..., description="List of log entries")
    total: int = Field(..., description="Total number of log entries")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


# Event type definitions
WEBHOOK_EVENT_TYPES = [
    "analysis.started",
    "analysis.completed",
    "analysis.failed",
    "project.created",
    "project.updated",
    "project.deleted",
    "report.generated",
    "security.issue_found",
    "quality.improved",
    "quality.degraded",
    "user.mentioned",
    "review.requested",
    "review.completed"
]

# Resource type definitions
WEBHOOK_RESOURCE_TYPES = [
    "project",
    "analysis",
    "report",
    "user",
    "organization",
    "webhook"
]

# Action type definitions
WEBHOOK_ACTIONS = [
    "create",
    "update",
    "delete",
    "start",
    "complete",
    "fail",
    "approve",
    "reject"
]
