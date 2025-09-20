"""
Input Validation Utilities

This module contains validation functions for various types of input data
used throughout the application, including project data, analysis configurations,
and user inputs.
"""

import re
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

from ..core.exceptions import ValidationError


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID.

    Args:
        uuid_string: String to validate

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid URL format, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # Basic URL validation
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))*)?$'
    return bool(re.match(pattern, url.strip()))


def validate_git_url(url: str) -> bool:
    """
    Validate Git repository URL.

    Args:
        url: Git URL to validate

    Returns:
        True if valid Git URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # Support both HTTPS and SSH Git URLs
    patterns = [
        r'^https://[^\s/$.?#].[^\s]*\.git/?$',  # HTTPS Git URLs
        r'^git@[^\s:]+:[^\s]+\.git/?$',         # SSH Git URLs
        r'^ssh://[^\s]+/[^\s]+\.git/?$',        # SSH protocol URLs
    ]

    return any(re.match(pattern, url.strip()) for pattern in patterns)


def validate_file_path(file_path: str) -> bool:
    """
    Validate file path format.

    Args:
        file_path: File path to validate

    Returns:
        True if valid file path, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False

    try:
        path = Path(file_path)
        # Check if it's a valid path format (doesn't mean file exists)
        return len(path.parts) > 0 and all(part for part in path.parts)
    except (ValueError, TypeError):
        return False


def validate_project_name(name: str) -> bool:
    """
    Validate project name.

    Args:
        name: Project name to validate

    Returns:
        True if valid project name, False otherwise
    """
    if not name or not isinstance(name, str):
        return False

    # Project names should be 1-100 characters, alphanumeric with spaces, hyphens, underscores
    if len(name.strip()) < 1 or len(name.strip()) > 100:
        return False

    pattern = r'^[a-zA-Z0-9\s\-_\.]+$'
    return bool(re.match(pattern, name.strip()))


def validate_analysis_config(config: Dict[str, Any]) -> bool:
    """
    Validate analysis configuration.

    Args:
        config: Analysis configuration to validate

    Returns:
