"""
Input Validation Utilities

This module provides comprehensive input validation functions for various data types
and business logic validation across the application.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format."""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def validate_url(url: str) -> bool:
    """Validate URL format."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_project_name(name: str) -> bool:
    """Validate project name."""
    if not name or not isinstance(name, str):
        return False
    if len(name.strip()) < 2 or len(name.strip()) > 100:
        return False
    # Allow alphanumeric, spaces, hyphens, underscores
    return bool(re.match(r'^[a-zA-Z0-9\s\-_]+$', name.strip()))


def validate_analysis_type(analysis_type: str) -> bool:
    """Validate analysis type."""
    valid_types = {
        'security', 'performance', 'complexity', 'duplication',
        'documentation', 'test_coverage', 'dependency', 'comprehensive'
    }
    return analysis_type in valid_types


def validate_severity(severity: str) -> bool:
    """Validate severity level."""
    valid_severities = {'critical', 'high', 'medium', 'low', 'info'}
    return severity in valid_severities


def validate_file_path(file_path: str) -> bool:
    """Validate file path format."""
    if not file_path or not isinstance(file_path, str):
        return False
    # Basic file path validation
    return len(file_path) > 0 and not file_path.startswith('..')


def validate_commit_sha(commit_sha: str) -> bool:
    """Validate Git commit SHA."""
    if not commit_sha or not isinstance(commit_sha, str):
        return False
    # SHA-1 is 40 characters, SHA-256 is 64
    return bool(re.match(r'^[a-f0-9]{40}$|^[a-f0-9]{64}$', commit_sha))


def validate_branch_name(branch_name: str) -> bool:
    """Validate Git branch name."""
    if not branch_name or not isinstance(branch_name, str):
        return False
    if len(branch_name) > 255:
        return False
    # Git branch name rules
    return bool(re.match(r'^[^\s\.\-][^\s]*[^\s\.\-]$|^\.$|^$', branch_name))


def validate_language_code(language: str) -> bool:
    """Validate programming language code."""
    valid_languages = {
        'python', 'javascript', 'typescript', 'java', 'go', 'rust',
        'csharp', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'c', 'cpp'
    }
    return language.lower() in valid_languages


def validate_positive_integer(value: int) -> bool:
    """Validate positive integer."""
    return isinstance(value, int) and value > 0


def validate_percentage(value: float) -> bool:
    """Validate percentage (0-100)."""
    return isinstance(value, (int, float)) and 0 <= value <= 100


def validate_confidence_score(score: float) -> bool:
    """Validate confidence score (0-1)."""
    return isinstance(score, (int, float)) and 0 <= score <= 1


def validate_json_string(json_str: str) -> bool:
    """Validate JSON string format."""
    if not json_str or not isinstance(json_str, str):
        return False
    try:
        import json
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def validate_datetime_iso(datetime_str: str) -> bool:
    """Validate ISO datetime string."""
    if not datetime_str or not isinstance(datetime_str, str):
        return False
    try:
        datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError):
        return False


def validate_report_config(config: Dict[str, Any]) -> bool:
    """Validate report configuration."""
    if not isinstance(config, dict):
        return False

    # Check required fields
    required_fields = ['output_format', 'include_raw_data']
    if not all(field in config for field in required_fields):
        return False

    # Validate output format
    valid_formats = ['pdf', 'html', 'json', 'xml']
    if config.get('output_format') not in valid_formats:
        return False

    # Validate boolean fields
    if not isinstance(config.get('include_raw_data'), bool):
        return False

    return True


def validate_analysis_config(config: Dict[str, Any]) -> bool:
    """Validate analysis configuration."""
    if not isinstance(config, dict):
        return False

    # Check analysis types
    if 'analysis_types' in config:
        analysis_types = config['analysis_types']
        if not isinstance(analysis_types, list):
            return False
        if not all(validate_analysis_type(t) for t in analysis_types):
            return False

    # Check file patterns
    if 'file_patterns' in config:
        file_patterns = config['file_patterns']
        if not isinstance(file_patterns, list):
            return False
        if not all(isinstance(p, str) for p in file_patterns):
            return False

    # Check exclude patterns
    if 'exclude_patterns' in config:
        exclude_patterns = config['exclude_patterns']
        if not isinstance(exclude_patterns, list):
            return False
        if not all(isinstance(p, str) for p in exclude_patterns):
            return False

    return True


def validate_user_permissions(permissions: List[str]) -> bool:
    """Validate user permissions list."""
    if not isinstance(permissions, list):
        return False

    valid_permissions = {
        'read:projects', 'write:projects', 'delete:projects',
        'read:analyses', 'write:analyses', 'delete:analyses',
        'read:reports', 'write:reports', 'delete:reports',
        'read:users', 'write:users', 'delete:users',
        'admin:*', 'system:*'
    }

    return all(perm in valid_permissions for perm in permissions)


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key or not isinstance(api_key, str):
        return False
    # API keys should be at least 32 characters, alphanumeric with some special chars
    return bool(re.match(r'^[a-zA-Z0-9_\-\.]{32,}$', api_key))


def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL."""
    if not validate_url(url):
        return False
    # Additional webhook-specific validation
    return url.startswith(('https://', 'http://localhost', 'http://127.0.0.1'))


def validate_webhook_secret(secret: str) -> bool:
    """Validate webhook secret."""
    if not secret or not isinstance(secret, str):
        return False
    # Webhook secrets should be at least 16 characters
    return len(secret) >= 16


def validate_rate_limit(limit: int) -> bool:
    """Validate rate limit value."""
    return isinstance(limit, int) and 1 <= limit <= 10000


def validate_timeout(timeout: int) -> bool:
    """Validate timeout value in seconds."""
    return isinstance(timeout, int) and 1 <= timeout <= 3600


def validate_batch_size(size: int) -> bool:
    """Validate batch processing size."""
    return isinstance(size, int) and 1 <= size <= 1000


def sanitize_string(input_str: str, max_length: int = 1000) -> str:
    """Sanitize string input by removing potentially dangerous characters."""
    if not isinstance(input_str, str):
        return ""

    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)

    # Trim whitespace and limit length
    sanitized = sanitized.strip()[:max_length]

    return sanitized


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    if not isinstance(filename, str):
        return "untitled"

    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Trim and ensure minimum length
    sanitized = sanitized.strip()
    if not sanitized:
        sanitized = "untitled"

    return sanitized


def validate_and_sanitize_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize project creation/update data."""
    sanitized = {}

    if 'name' in data:
        name = sanitize_string(data['name'], 100)
        if validate_project_name(name):
            sanitized['name'] = name

    if 'description' in data:
        description = sanitize_string(data['description'], 1000)
        sanitized['description'] = description

    if 'repository_url' in data:
        url = sanitize_string(data['repository_url'])
        if validate_url(url):
            sanitized['repository_url'] = url

    if 'languages' in data:
        languages = data['languages']
        if isinstance(languages, list):
            valid_languages = [lang for lang in languages if validate_language_code(lang)]
            if valid_languages:
                sanitized['languages'] = valid_languages

    return sanitized


def validate_and_sanitize_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize user creation/update data."""
    sanitized = {}

    if 'email' in data:
        email = sanitize_string(data['email'])
        if validate_email_address(email):
            sanitized['email'] = email.lower()

    if 'username' in data:
        username = sanitize_string(data['username'], 50)
        if len(username) >= 3 and re.match(r'^[a-zA-Z0-9_]+$', username):
            sanitized['username'] = username

    if 'full_name' in data:
        full_name = sanitize_string(data['full_name'], 100)
        sanitized['full_name'] = full_name

    return sanitized


class BaseValidator(BaseModel):
    """Base Pydantic model with common validators."""

    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        """Sanitize string fields."""
        if isinstance(v, str):
            return sanitize_string(v)
        return v

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True


def bulk_validate_uuids(uuid_list: List[str]) -> List[str]:
    """Validate a list of UUIDs and return valid ones."""
    return [uid for uid in uuid_list if validate_uuid(uid)]


def bulk_validate_emails(email_list: List[str]) -> List[str]:
    """Validate a list of emails and return valid ones."""
    return [email for email in email_list if validate_email_address(email)]


def validate_environment_variables(env_vars: Dict[str, str]) -> Dict[str, str]:
    """Validate environment variable names and values."""
    validated = {}

    for key, value in env_vars.items():
        # Validate variable name
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', key):
            logger.warning(f"Invalid environment variable name: {key}")
            continue

        # Validate and sanitize value
        if isinstance(value, str):
            sanitized_value = sanitize_string(value, 10000)  # Large limit for env vars
            validated[key] = sanitized_value

    return validated
