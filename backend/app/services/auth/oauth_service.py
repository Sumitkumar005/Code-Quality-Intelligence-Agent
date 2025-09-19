"""
OAuth service for third-party authentication.
"""

from typing import Dict, Any, Optional
import secrets
import httpx
from urllib.parse import urlencode

from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging import get_logger

logger = get_logger(__name__)


class OAuthService:
    """
    OAuth service for handling third-party authentication providers.
    """

    def __init__(self):
        self.providers = {
            "github": {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_url": "https://api.github.com/user",
                "scope": "user:email"
            },
            "gitlab": {
                "client_id": settings.GITLAB_CLIENT_ID,
                "client_secret": settings.GITLAB_CLIENT_SECRET,
                "authorize_url": "https://gitlab.com/oauth/authorize",
                "token_url": "https://gitlab.com/oauth/token",
                "user_url": "https://gitlab.com/api/v4/user",
                "scope": "read_user"
            },
            "bitbucket": {
                "client_id": settings.BITBUCKET_CLIENT_ID,
                "client_secret": settings.BITBUCKET_CLIENT_SECRET,
                "authorize_url": "https://bitbucket.org/site/oauth2/authorize",
                "token_url": "https://bitbucket.org/site/oauth2/access_token",
                "user_url": "https://api.bitbucket.org/2.0/user",
                "scope": "account"
            }
        }

    def get_authorization_url(self, provider: str, redirect_uri: str) -> str:
        """
        Generate OAuth authorization URL for a provider.
        """
        if provider not in self.providers:
            raise APIException(
                status_code=400,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        config = self.providers[provider]
        state = secrets.token_urlsafe(32)  # CSRF protection

        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "state": state,
            "response_type": "code"
        }

        url = f"{config['authorize_url']}?{urlencode(params)}"
        return url, state

    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        """
        if provider not in self.providers:
            raise APIException(
                status_code=400,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        config = self.providers[provider]

        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    config["token_url"],
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                token_data = response.json()

                return token_data

            except httpx.HTTPError as e:
                logger.error(f"OAuth token exchange failed for {provider}: {e}")
                raise APIException(
                    status_code=400,
                    detail="Failed to exchange authorization code for token"
                )

    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """
        Get user information from OAuth provider.
        """
        if provider not in self.providers:
            raise APIException(
                status_code=400,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        config = self.providers[provider]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(config["user_url"], headers=headers)
                response.raise_for_status()
                user_data = response.json()

                # Normalize user data across providers
                normalized_data = self._normalize_user_data(provider, user_data)

                return normalized_data

            except httpx.HTTPError as e:
                logger.error(f"Failed to get user info from {provider}: {e}")
                raise APIException(
                    status_code=400,
                    detail="Failed to get user information from OAuth provider"
                )

    def _normalize_user_data(self, provider: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user data from different OAuth providers to a common format.
        """
        if provider == "github":
            return {
                "provider": "github",
                "provider_id": str(user_data.get("id")),
                "email": user_data.get("email"),
                "username": user_data.get("login"),
                "full_name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url"),
                "profile_url": user_data.get("html_url"),
                "raw_data": user_data
            }

        elif provider == "gitlab":
            return {
                "provider": "gitlab",
                "provider_id": str(user_data.get("id")),
                "email": user_data.get("email"),
                "username": user_data.get("username"),
                "full_name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url"),
                "profile_url": user_data.get("web_url"),
                "raw_data": user_data
            }

        elif provider == "bitbucket":
            return {
                "provider": "bitbucket",
                "provider_id": user_data.get("account_id"),
                "email": None,  # Bitbucket doesn't provide email in basic user info
                "username": user_data.get("username"),
                "full_name": user_data.get("display_name"),
                "avatar_url": user_data.get("links", {}).get("avatar", {}).get("href"),
                "profile_url": user_data.get("links", {}).get("html", {}).get("href"),
                "raw_data": user_data
            }

        else:
            return {
                "provider": provider,
                "raw_data": user_data
            }

    async def refresh_token(self, provider: str, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an OAuth access token.
        """
        if provider not in self.providers:
            raise APIException(
                status_code=400,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        config = self.providers[provider]

        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    config["token_url"],
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                token_data = response.json()

                return token_data

            except httpx.HTTPError as e:
                logger.error(f"OAuth token refresh failed for {provider}: {e}")
                raise APIException(
                    status_code=400,
                    detail="Failed to refresh OAuth token"
                )

    def validate_state(self, received_state: str, expected_state: str) -> bool:
        """
        Validate OAuth state parameter for CSRF protection.
        """
        return secrets.compare_digest(received_state, expected_state)
