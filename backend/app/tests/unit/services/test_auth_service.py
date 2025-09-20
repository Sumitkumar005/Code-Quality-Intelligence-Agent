"""
Unit tests for authentication service.
Tests auth service functionality in isolation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from backend.app.services.auth.auth_service import AuthService
from backend.app.services.auth.jwt_service import JWTService
from backend.app.models.user import User


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def auth_service(self, mock_jwt_service):
        """Create AuthService instance with mocked dependencies."""
        return AuthService(jwt_service=mock_jwt_service)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def test_authenticate_user_success(self, auth_service, sample_user):
        """Test successful user authentication."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = sample_user
        mock_user_repo.verify_password.return_value = True

        # Act
        result = auth_service.authenticate_user(
            email="test@example.com",
            password="correct_password",
            user_repository=mock_user_repo
        )

        # Assert
        assert result == sample_user
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_user_repo.verify_password.assert_called_once_with(
            sample_user, "correct_password"
        )

    def test_authenticate_user_invalid_credentials(self, auth_service):
        """Test authentication with invalid credentials."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.authenticate_user(
                email="nonexistent@example.com",
                password="password",
                user_repository=mock_user_repo
            )

    def test_create_access_token(self, auth_service, mock_jwt_service):
        """Test JWT token creation."""
        # Arrange
        user_id = "test-user-id"
        expires_delta = timedelta(minutes=30)

        # Act
        token = auth_service.create_access_token(
            user_id=user_id,
            expires_delta=expires_delta
        )

        # Assert
        assert token == "mock-jwt-token"
        mock_jwt_service.encode_token.assert_called_once_with(
            {"sub": user_id, "exp": pytest.any(int)}
        )

    def test_get_current_user_success(self, auth_service, sample_user):
        """Test getting current user from token."""
        # Arrange
        mock_user_repo = Mock()
        mock_user_repo.get_by_id.return_value = sample_user

        # Act
        result = auth_service.get_current_user(
            token="valid-token",
            user_repository=mock_user_repo
        )

        # Assert
        assert result == sample_user
        mock_user_repo.get_by_id.assert_called_once_with("test-user-id")

    def test_get_current_user_invalid_token(self, auth_service):
        """Test getting current user with invalid token."""
        # Arrange
        mock_user_repo = Mock()

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.get_current_user(
                token="invalid-token",
                user_repository=mock_user_repo
            )
