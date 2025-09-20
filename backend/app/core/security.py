"""
Security utilities for authentication, authorization, and encryption.
Includes JWT token handling, password hashing, and permission checking.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import string
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token schemes
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# OAuth2 scheme for token authentication
security = HTTPBearer(auto_error=False)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def get_token_payload(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
    """Extract and verify token payload from HTTP credentials."""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    """Get current user ID from token."""
    payload = get_token_payload(credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
        )
    return user_id


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def get_password_hash(password: str) -> str:
    """Get password hash (alias for hash_password)."""
    return hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"cqia_{generate_secure_token(32)}"


def verify_api_key(api_key: str) -> bool:
    """Verify API key format (basic validation)."""
    return api_key.startswith("cqia_") and len(api_key) == 37


# Permission constants
PERMISSIONS = {
    "read:projects": "Read projects",
    "write:projects": "Create and modify projects",
    "delete:projects": "Delete projects",
    "read:analyses": "Read analyses",
    "write:analyses": "Create and run analyses",
    "delete:analyses": "Delete analyses",
    "read:reports": "Read reports",
    "write:reports": "Generate reports",
    "read:users": "Read user information",
    "write:users": "Modify users",
    "admin:users": "Full user administration",
    "admin:system": "System administration",
}


def check_permission(user_permissions: list, required_permission: str) -> bool:
    """Check if user has required permission."""
    return required_permission in user_permissions


def require_permission(required_permission: str):
    """Decorator to require specific permission for endpoint."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependencies
            # For now, just return the function
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Role-based access control
ROLES = {
    "viewer": [
        "read:projects",
        "read:analyses",
        "read:reports",
    ],
    "developer": [
        "read:projects",
        "write:projects",
        "read:analyses",
        "write:analyses",
        "read:reports",
        "write:reports",
    ],
    "admin": [
        "read:projects",
        "write:projects",
        "delete:projects",
        "read:analyses",
        "write:analyses",
        "delete:analyses",
        "read:reports",
        "write:reports",
        "read:users",
        "write:users",
        "admin:users",
        "admin:system",
    ],
    "owner": [
        "read:projects",
        "write:projects",
        "delete:projects",
        "read:analyses",
        "write:analyses",
        "delete:analyses",
        "read:reports",
        "write:reports",
        "read:users",
        "write:users",
        "admin:users",
        "admin:system",
    ],
}


def get_role_permissions(role: str) -> list:
    """Get permissions for a specific role."""
    return ROLES.get(role, [])


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, "Password is strong"
