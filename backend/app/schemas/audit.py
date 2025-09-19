"""
Pydantic schemas for audit-related operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import CQIA_BaseModel, CQIA_BaseCreate, CQIA_BaseUpdate, CQIA_BaseResponse


class AuditLogBase(CQIA_BaseModel):
    """Base audit log schema."""

    user_id: Optional[str] = Field(None, description="User ID")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Old values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    changes: Optional[Dict[str, Any]] = Field(None, description="Changes made")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    session_id: Optional[str] = Field(None, description="Session ID")
    success: bool = Field(True, description="Success status")
    error_message: Optional[str] = Field(None, description="Error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AuditLogCreate(AuditLogBase, CQIA_BaseCreate):
    """Schema for creating an audit log."""

    pass


class AuditLogResponse(AuditLogBase, CQIA_BaseResponse):
    """Schema for audit log response data."""

    # Computed properties
    action_description: str = Field(..., description="Human-readable action description")
    has_changes: bool = Field(..., description="Has changes")
    change_summary: Dict[str, Any] = Field(..., description="Change summary")


class AuditLogArchiveBase(CQIA_BaseModel):
    """Base audit log archive schema."""

    log_data: Dict[str, Any] = Field(..., description="Archived log data")
    archive_date: datetime = Field(..., description="Archive date")
    archive_reason: str = Field("age", description="Archive reason")
    original_size: int = Field(..., description="Original size")
    compressed_size: int = Field(..., description="Compressed size")


class AuditLogArchiveResponse(AuditLogArchiveBase, CQIA_BaseResponse):
    """Schema for audit log archive response data."""

    pass


class AuditLogFilter(CQIA_BaseModel):
    """Schema for audit log filtering."""

    user_id: Optional[str] = Field(None, description="Filter by user ID")
    organization_id: Optional[str] = Field(None, description="Filter by organization ID")
    action: Optional[str] = Field(None, description="Filter by action")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    resource_id: Optional[str] = Field(None, description="Filter by resource ID")
    success: Optional[bool] = Field(None, description="Filter by success status")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    ip_address: Optional[str] = Field(None, description="Filter by IP address")


class AuditLogSummary(CQIA_BaseModel):
    """Schema for audit log summary statistics."""

    total_logs: int = Field(..., description="Total audit logs")
    logs_today: int = Field(..., description="Logs from today")
    logs_this_week: int = Field(..., description="Logs from this week")
    logs_this_month: int = Field(..., description="Logs from this month")
    failed_actions: int = Field(..., description="Failed actions count")
    top_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Top actions")
    top_users: List[Dict[str, Any]] = Field(default_factory=list, description="Top users")
    top_resources: List[Dict[str, Any]] = Field(default_factory=list, description="Top resources")


class AuditLogExportRequest(CQIA_BaseModel):
    """Schema for audit log export requests."""

    format: str = Field("csv", description="Export format")
    filters: Optional[AuditLogFilter] = Field(None, description="Export filters")
    include_fields: Optional[List[str]] = Field(None, description="Fields to include")


class AuditLogExportResponse(CQIA_BaseModel):
    """Schema for audit log export responses."""

    export_id: str = Field(..., description="Export ID")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL")
    file_size: Optional[int] = Field(None, description="File size")
    record_count: int = Field(..., description="Record count")


class AuditLogRetentionPolicy(CQIA_BaseModel):
    """Schema for audit log retention policy."""

    retention_days: int = Field(..., description="Retention period in days")
    archive_after_days: int = Field(..., description="Archive after days")
    delete_after_days: int = Field(..., description="Delete after days")
    compression_enabled: bool = Field(True, description="Enable compression")
    encryption_enabled: bool = Field(True, description="Enable encryption")


class AuditLogRetentionUpdate(CQIA_BaseUpdate):
    """Schema for updating audit log retention policy."""

    retention_days: Optional[int] = Field(None, description="Retention period in days")
    archive_after_days: Optional[int] = Field(None, description="Archive after days")
    delete_after_days: Optional[int] = Field(None, description="Delete after days")
    compression_enabled: Optional[bool] = Field(None, description="Enable compression")
    encryption_enabled: Optional[bool] = Field(None, description="Enable encryption")


class AuditLogAlertRule(CQIA_BaseModel):
    """Schema for audit log alert rules."""

    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    conditions: Dict[str, Any] = Field(..., description="Alert conditions")
    severity: str = Field("medium", description="Alert severity")
    enabled: bool = Field(True, description="Rule enabled")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    cooldown_minutes: int = Field(60, description="Cooldown period in minutes")


class AuditLogAlertRuleCreate(AuditLogAlertRule, CQIA_BaseCreate):
    """Schema for creating audit log alert rules."""

    pass


class AuditLogAlertRuleUpdate(CQIA_BaseUpdate):
    """Schema for updating audit log alert rules."""

    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Alert conditions")
    severity: Optional[str] = Field(None, description="Alert severity")
    enabled: Optional[bool] = Field(None, description="Rule enabled")
    notification_channels: Optional[List[str]] = Field(None, description="Notification channels")
    cooldown_minutes: Optional[int] = Field(None, description="Cooldown period in minutes")


class AuditLogAlertRuleResponse(AuditLogAlertRule, CQIA_BaseResponse):
    """Schema for audit log alert rule response data."""

    last_triggered: Optional[datetime] = Field(None, description="Last triggered timestamp")
    trigger_count: int = Field(..., description="Trigger count")


class AuditLogAlert(CQIA_BaseModel):
    """Schema for audit log alerts."""

    rule_id: str = Field(..., description="Alert rule ID")
    rule_name: str = Field(..., description="Rule name")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Alert details")
    triggered_at: datetime = Field(..., description="Triggered timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolved timestamp")
    resolved_by: Optional[str] = Field(None, description="Resolved by user")
    status: str = Field("active", description="Alert status")
