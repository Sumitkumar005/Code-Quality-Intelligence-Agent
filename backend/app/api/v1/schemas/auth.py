"""
Authentication schemas for API v1.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse" = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """User response schema."""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    is_active: bool = Field(default=True, description="Is user active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TokenData(BaseModel):
    """Token data schema."""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    exp: Optional[datetime] = Field(None, description="Token expiration")


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, description="Full name")


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = Field(None, description="User email")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    is_active: Optional[bool] = Field(None, description="Is user active")
