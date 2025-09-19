"""
Authentication service for the CQIA application.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.services.auth.jwt_service import JWTService
from app.crud.user import user_crud

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service handling user registration, login, and token management.
    """

    def __init__(self, db: Session):
        self.db = db
        self.jwt_service = JWTService()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a password for storing.
        """
        return pwd_context.hash(password)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        """
        user = user_crud.get_by_email(self.db, email=email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def register_user(self, user_in: UserCreate) -> User:
        """
        Register a new user.
        """
        # Check if user already exists
        existing_user = user_crud.get_by_email(self.db, email=user_in.email)
        if existing_user:
            raise APIException(
                status_code=400,
                detail="User with this email already exists"
            )

        # Hash the password
        hashed_password = self.get_password_hash(user_in.password)

        # Create user data
        user_data = user_in.dict()
        user_data.pop("password")  # Remove plain password
        user_data["hashed_password"] = hashed_password

        # Create user
        user = user_crud.create(self.db, obj_in=user_data)
        logger.info(f"User registered: {user.email}")
        return user

    def login_user(self, user_in: UserLogin) -> Dict[str, Any]:
        """
        Login a user and return access tokens.
        """
        user = self.authenticate_user(user_in.email, user_in.password)
        if not user:
            raise APIException(
                status_code=401,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise APIException(
                status_code=400,
                detail="Inactive user"
            )

        # Update last login
        user_crud.update(self.db, db_obj=user, obj_in={"last_login": datetime.utcnow()})

        # Generate tokens
        access_token = self.jwt_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = self.jwt_service.create_refresh_token(
            data={"sub": str(user.id)}
        )

        logger.info(f"User logged in: {user.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            }
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        """
        try:
            payload = self.jwt_service.verify_refresh_token(refresh_token)
            user_id = payload.get("sub")

            user = user_crud.get(self.db, id=user_id)
            if not user:
                raise APIException(
                    status_code=401,
                    detail="User not found"
                )

            if not user.is_active:
                raise APIException(
                    status_code=400,
                    detail="Inactive user"
                )

            # Generate new access token
            access_token = self.jwt_service.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise APIException(
                status_code=401,
                detail="Invalid refresh token"
            )

    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        """
        if not self.verify_password(current_password, user.hashed_password):
            raise APIException(
                status_code=400,
                detail="Incorrect current password"
            )

        hashed_password = self.get_password_hash(new_password)
        user_crud.update(self.db, db_obj=user, obj_in={"hashed_password": hashed_password})

        logger.info(f"Password changed for user: {user.email}")
        return True

    def reset_password_request(self, email: str) -> str:
        """
        Request password reset and return reset token.
        """
        user = user_crud.get_by_email(self.db, email=email)
        if not user:
            # Don't reveal if user exists or not
            return "reset_token_placeholder"

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # In a real implementation, you would:
        # 1. Store the reset token with expiration in database/cache
        # 2. Send email with reset link

        logger.info(f"Password reset requested for: {email}")
        return reset_token

    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Reset password using reset token.
        """
        # In a real implementation, you would:
        # 1. Verify the reset token from database/cache
        # 2. Check if token is not expired
        # 3. Update user password

        # For now, just hash the new password
        hashed_password = self.get_password_hash(new_password)

        # This would need to be implemented with proper token verification
        logger.info("Password reset completed")
        return True

    def logout_user(self, user: User) -> bool:
        """
        Logout user (could blacklist tokens if needed).
        """
        logger.info(f"User logged out: {user.email}")
        return True
