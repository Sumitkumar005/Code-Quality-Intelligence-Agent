"""
JWT service for token management.
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging import get_logger

logger = get_logger(__name__)


class JWTService:
    """
    JWT token creation and verification service.
    """

    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """
        Create an access token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create a refresh token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise APIException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise APIException(
                status_code=401,
                detail="Invalid token"
            )

    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """
        Verify an access token.
        """
        payload = JWTService.verify_token(token)
        if payload.get("type") != "access":
            raise APIException(
                status_code=401,
                detail="Invalid token type"
            )
        return payload

    @staticmethod
    def verify_refresh_token(token: str) -> Dict[str, Any]:
        """
        Verify a refresh token.
        """
        payload = JWTService.verify_token(token)
        if payload.get("type") != "refresh":
            raise APIException(
                status_code=401,
                detail="Invalid token type"
            )
        return payload

    @staticmethod
    def get_token_expiration(token: str) -> Optional[datetime]:
        """
        Get token expiration time without verification.
        """
        try:
            # Decode without verification to get expiration
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})

            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
        except Exception as e:
            logger.error(f"Error getting token expiration: {e}")

        return None

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Check if a token is expired.
        """
        expiration = JWTService.get_token_expiration(token)
        if expiration:
            return datetime.utcnow() > expiration
        return True

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Extract user ID from token without full verification.
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("sub")
        except Exception:
            return None

    @staticmethod
    def create_password_reset_token(email: str) -> str:
        """
        Create a password reset token.
        """
        to_encode = {
            "email": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[str]:
        """
        Verify a password reset token and return email.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get("type") != "password_reset":
                return None

            return payload.get("email")

        except jwt.ExpiredSignatureError:
            raise APIException(
                status_code=400,
                detail="Password reset token has expired"
            )
        except jwt.JWTError:
            raise APIException(
                status_code=400,
                detail="Invalid password reset token"
            )
