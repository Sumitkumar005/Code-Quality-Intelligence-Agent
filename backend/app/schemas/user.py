"""
Pydantic schemas for user-related operations.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field, EmailStr

from .base import CQIA_BaseModel, CQIA_BaseCreate, CQIA_BaseUpdate, CQIA_BaseResponse


class UserBase(CQIA_BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    full_name: Optional[str] = Field(None, description="Full display name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User biography")


class UserCreate(UserBase, CQIA_BaseCreate):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(CQIA_BaseUpdate):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, description="Unique username")
    full_name: Optional[str] = Field(None, description="Full display name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User biography")
    is_active: Optional[bool] = Field(None, description="Account active status")
    is_verified: Optional[bool] = Field(None, description="Email verification status")


class UserResponse(UserBase, CQIA_BaseResponse):
    """Schema for user response data."""

    is_active: bool = Field(..., description="Account active status")
    is_superuser: bool = Field(..., description="Superuser privileges")
    is_verified: bool = Field(..., description="Email verification status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(..., description="Total login count")
    preferences: dict = Field(default_factory=dict, description="User preferences")
    settings: dict = Field(default_factory=dict, description="User settings")

    # Computed properties
    is_admin: bool = Field(..., description="User has admin role in any organization")
    is_owner: bool = Field(..., description="User has owner role in any organization")


class UserLogin(CQIA_BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class UserPasswordChange(CQIA_BaseModel):
    """Schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class UserPasswordResetRequest(CQIA_BaseModel):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User email address")


class UserPasswordReset(CQIA_BaseModel):
    """Schema for password reset."""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class OrganizationBase(CQIA_BaseModel):
    """Base organization schema."""

    name: str = Field(..., description="Organization name")
    slug: str = Field(..., description="Unique organization slug")
    description: Optional[str] = Field(None, description="Organization description")


class OrganizationCreate(OrganizationBase, CQIA_BaseCreate):
    """Schema for creating a new organization."""

    pass


class OrganizationUpdate(CQIA_BaseUpdate):
    """Schema for updating organization information."""

    name: Optional[str] = Field(None, description="Organization name")
    slug: Optional[str] = Field(None, description="Unique organization slug")
    description: Optional[str] = Field(None, description="Organization description")
    plan: Optional[str] = Field(None, description="Billing plan")
    max_users: Optional[int] = Field(None, description="Maximum number of users")
    max_projects: Optional[int] = Field(None, description="Maximum number of projects")
    is_active: Optional[bool] = Field(None, description="Organization active status")


class OrganizationResponse(OrganizationBase, CQIA_BaseResponse):
    """Schema for organization response data."""

    plan: str = Field(..., description="Billing plan")
    max_users: int = Field(..., description="Maximum number of users")
    max_projects: int = Field(..., description="Maximum number of projects")
    is_active: bool = Field(..., description="Organization active status")
    settings: dict = Field(default_factory=dict, description="Organization settings")
    features: dict = Field(default_factory=dict, description="Organization features")

    # Computed properties
    member_count: int = Field(..., description="Current member count")
    project_count: int = Field(..., description="Current project count")


class OrganizationMemberBase(CQIA_BaseModel):
    """Base organization member schema."""

    user_id: str = Field(..., description="User ID")
    role: str = Field(..., description="Member role")


class OrganizationMemberCreate(OrganizationMemberBase, CQIA_BaseCreate):
    """Schema for adding a member to organization."""

    pass


class OrganizationMemberUpdate(CQIA_BaseUpdate):
    """Schema for updating organization member."""

    role: Optional[str] = Field(None, description="Member role")
    permissions: Optional[dict] = Field(None, description="Custom permissions")


class OrganizationMemberResponse(OrganizationMemberBase, CQIA_BaseResponse):
    """Schema for organization member response data."""

    organization_id: str = Field(..., description="Organization ID")
    joined_at: datetime = Field(..., description="Join timestamp")
    permissions: dict = Field(default_factory=dict, description="Member permissions")

    # Nested user data
    user: UserResponse = Field(..., description="User information")


class UserWithOrganizations(UserResponse):
    """User response with organization information."""

    organizations: List[OrganizationMemberResponse] = Field(
        default_factory=list, description="User's organizations"
    )
