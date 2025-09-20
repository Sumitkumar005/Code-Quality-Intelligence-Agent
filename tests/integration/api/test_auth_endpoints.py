"""
Integration tests for authentication API endpoints.
Tests complete authentication workflows via HTTP API.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Test successful user login."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }

        # Act
        response = await async_client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        # Arrange
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        # Act
        response = await async_client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_current_user_authenticated(self, authenticated_async_client: AsyncClient):
        """Test getting current user with valid authentication."""
        # Act
        response = await authenticated_async_client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data

    @pytest.mark.asyncio
    async def test_get_current_user_unauthenticated(self, async_client: AsyncClient):
        """Test getting current user without authentication."""
        # Act
        response = await async_client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_user(self, async_client: AsyncClient):
        """Test user registration."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "full_name": "New User"
        }

        # Act
        response = await async_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_logout(self, authenticated_async_client: AsyncClient):
        """Test user logout."""
        # Act
        response = await authenticated_async_client.post("/api/v1/auth/logout")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"
