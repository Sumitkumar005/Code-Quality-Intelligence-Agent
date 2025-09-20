"""
Organization schemas for API validation and serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    description: Optional[str] = Field(None, max_length=500, description="Organization description")
    website: Optional[str] = Field(None, description="Organization website URL")
    contact_email: Optional[str] = Field(None, description="Primary contact email")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Organization settings")


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = None
    contact_email: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationInDBBase(OrganizationBase):
    """Base schema for organization in database."""
    id: str = Field(..., description="Organization unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(default=True, description="Organization active status")

    class Config:
        from_attributes = True


class Organization(OrganizationInDBBase):
    """Complete organization schema."""
    pass


class OrganizationWithStats(OrganizationInDBBase):
    """Organization schema with statistics."""
    total_projects: int = Field(default=0, description="Total number of projects")
    active_projects: int = Field(default=0, description="Number of active projects")
    total_analyses: int = Field(default=0, description="Total number of analyses")
    average_score: float = Field(default=0.0, description="Average code quality score")
    last_analysis_at: Optional[datetime] = Field(None, description="Last analysis timestamp")


class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    user_id: str = Field(..., description="User unique identifier")
    role: str = Field(..., description="Member role in organization")
    permissions: Optional[List[str]] = Field(default_factory=list, description="Member permissions")


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for creating an organization member."""
    pass


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating an organization member."""
    role: Optional[str] = None
    permissions: Optional[List[str]] = None


class OrganizationMemberInDBBase(OrganizationMemberBase):
    """Base schema for organization member in database."""
    id: str = Field(..., description="Member unique identifier")
    organization_id: str = Field(..., description="Organization unique identifier")
    joined_at: datetime = Field(..., description="Member join timestamp")
    invited_by: Optional[str] = Field(None, description="User who invited this member")

    class Config:
        from_attributes = True


class OrganizationMember(OrganizationMemberInDBBase):
    """Complete organization member schema."""
    user: Optional[Dict[str, Any]] = Field(None, description="User information")


class OrganizationInviteBase(BaseModel):
    """Base organization invite schema."""
    email: str = Field(..., description="Invitee email address")
    role: str = Field(default="member", description="Role to assign")
    permissions: Optional[List[str]] = Field(default_factory=list, description="Permissions to grant")
    message: Optional[str] = Field(None, max_length=500, description="Invite message")


class OrganizationInviteCreate(OrganizationInviteBase):
    """Schema for creating an organization invite."""
    pass


class OrganizationInviteInDBBase(OrganizationInviteBase):
    """Base schema for organization invite in database."""
    id: str = Field(..., description="Invite unique identifier")
    organization_id: str = Field(..., description="Organization unique identifier")
    invited_by: str = Field(..., description="User who sent the invite")
    token: str = Field(..., description="Invite token")
    expires_at: datetime = Field(..., description="Invite expiration timestamp")
    accepted_at: Optional[datetime] = Field(None, description="Accept timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class OrganizationInvite(OrganizationInviteInDBBase):
    """Complete organization invite schema."""
    pass


class OrganizationWebhookBase(BaseModel):
    """Base organization webhook schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Webhook name")
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(default_factory=list, description="Events to trigger webhook")
    is_active: bool = Field(default=True, description="Webhook active status")
    secret: Optional[str] = Field(None, description="Webhook secret for signature verification")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional headers")


class OrganizationWebhookCreate(OrganizationWebhookBase):
    """Schema for creating an organization webhook."""
    pass


class OrganizationWebhookUpdate(BaseModel):
    """Schema for updating an organization webhook."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    secret: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


class OrganizationWebhookInDBBase(OrganizationWebhookBase):
    """Base schema for organization webhook in database."""
    id: str = Field(..., description="Webhook unique identifier")
    organization_id: str = Field(..., description="Organization unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_triggered_at: Optional[datetime] = Field(None, description="Last trigger timestamp")

    class Config:
        from_attributes = True


class OrganizationWebhook(OrganizationWebhookInDBBase):
    """Complete organization webhook schema."""
    pass


class OrganizationWebhookDeliveryBase(BaseModel):
    """Base organization webhook delivery schema."""
    webhook_id: str = Field(..., description="Webhook unique identifier")
    event_type: str = Field(..., description="Event type that triggered delivery")
    payload: Dict[str, Any] = Field(..., description="Delivery payload")
    response_status: Optional[int] = Field(None, description="HTTP response status")
    response_body: Optional[str] = Field(None, description="HTTP response body")
    duration_ms: Optional[int] = Field(None, description="Delivery duration in milliseconds")


class OrganizationWebhookDeliveryInDBBase(OrganizationWebhookDeliveryBase):
    """Base schema for organization webhook delivery in database."""
    id: str = Field(..., description="Delivery unique identifier")
    organization_id: str = Field(..., description="Organization unique identifier")
    delivered_at: datetime = Field(..., description="Delivery timestamp")
    success: bool = Field(..., description="Delivery success status")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")

    class Config:
        from_attributes = True


class OrganizationWebhookDelivery(OrganizationWebhookDeliveryInDBBase):
    """Complete organization webhook delivery schema."""
    pass


class OrganizationSettings(BaseModel):
    """Organization settings schema."""
    analysis: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis settings")
    notifications: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Notification settings")
    integrations: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Integration settings")
    security: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Security settings")
    limits: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Usage limits")


class OrganizationUsage(BaseModel):
    """Organization usage statistics schema."""
    projects_count: int = Field(default=0, description="Number of projects")
    analyses_count: int = Field(default=0, description="Number of analyses")
    storage_used_bytes: int = Field(default=0, description="Storage used in bytes")
    api_calls_count: int = Field(default=0, description="Number of API calls")
    period_start: datetime = Field(..., description="Usage period start")
    period_end: datetime = Field(..., description="Usage period end")


class OrganizationBilling(BaseModel):
    """Organization billing information schema."""
    plan: str = Field(..., description="Current billing plan")
    status: str = Field(..., description="Billing status")
    current_period_start: Optional[datetime] = Field(None, description="Current billing period start")
    current_period_end: Optional[datetime] = Field(None, description="Current billing period end")
    usage: Optional[OrganizationUsage] = Field(None, description="Current usage")
    limits: Optional[Dict[str, Any]] = Field(None, description="Plan limits")


# Response schemas
class OrganizationListResponse(BaseModel):
    """Response schema for listing organizations."""
    organizations: List[Organization] = Field(..., description="List of organizations")
    total: int = Field(..., description="Total number of organizations")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class OrganizationDetailResponse(BaseModel):
    """Response schema for organization details."""
    organization: Organization = Field(..., description="Organization information")
    members: List[OrganizationMember] = Field(default_factory=list, description="Organization members")
    webhooks: List[OrganizationWebhook] = Field(default_factory=list, description="Organization webhooks")
    settings: OrganizationSettings = Field(..., description="Organization settings")
    billing: Optional[OrganizationBilling] = Field(None, description="Billing information")


class OrganizationStatsResponse(BaseModel):
    """Response schema for organization statistics."""
    stats: OrganizationWithStats = Field(..., description="Organization statistics")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activity")
    top_projects: List[Dict[str, Any]] = Field(default_factory=list, description="Top performing projects")


class OrganizationMemberListResponse(BaseModel):
    """Response schema for listing organization members."""
    members: List[OrganizationMember] = Field(..., description="List of organization members")
    total: int = Field(..., description="Total number of members")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class OrganizationWebhookListResponse(BaseModel):
    """Response schema for listing organization webhooks."""
    webhooks: List[OrganizationWebhook] = Field(..., description="List of organization webhooks")
    total: int = Field(..., description="Total number of webhooks")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class OrganizationWebhookDeliveryListResponse(BaseModel):
    """Response schema for listing webhook deliveries."""
    deliveries: List[OrganizationWebhookDelivery] = Field(..., description="List of webhook deliveries")
    total: int = Field(..., description="Total number of deliveries")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
