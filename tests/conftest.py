"""
Pytest configuration and fixtures for CQIA testing.
Provides comprehensive test setup, fixtures, and utilities.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import Mock, MagicMock, AsyncMock
from httpx import AsyncClient
import structlog
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base
from backend.app.core.config import Settings
from backend.app.main import app
from backend.app.db.session import get_db_session
from backend.app.services.auth.jwt_service import JWTService
from backend.app.services.auth.auth_service import AuthService
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.project import Project


# Configure structlog for testing
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


# Test database setup
@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Provide test database URL."""
    return "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    """Create test database engine."""
    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL debugging
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# Async test database setup
@pytest_asyncio.fixture(scope="function")
async def async_test_db_session(test_engine) -> AsyncGenerator[Session, None]:
    """Create async test database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    await session.close()
    transaction.rollback()
    connection.close()


# Application fixtures
@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """Provide test settings."""
    return Settings(
        DEBUG=True,
        DATABASE_URL="sqlite:///./test.db",
        DATABASE_POOL_SIZE=5,
        DATABASE_MAX_OVERFLOW=10,
        DATABASE_ECHO=False,
        SECRET_KEY="test-secret-key-for-testing-only",
        JWT_SECRET_KEY="test-jwt-secret-key-for-testing-only",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRE_MINUTES=30,
        REDIS_URL="redis://localhost:6379/1",
        CELERY_BROKER_URL="redis://localhost:6379/2",
        CELERY_RESULT_BACKEND="redis://localhost:6379/3",
        S3_BUCKET_NAME="test-bucket",
        S3_ACCESS_KEY="test-access-key",
        S3_SECRET_KEY="test-secret-key",
        S3_REGION="us-east-1",
        GITHUB_CLIENT_ID="test-github-client-id",
        GITHUB_CLIENT_SECRET="test-github-client-secret",
        GITLAB_CLIENT_ID="test-gitlab-client-id",
        GITLAB_CLIENT_SECRET="test-gitlab-client-secret",
        OPENAI_API_KEY="test-openai-api-key",
        ANTHROPIC_API_KEY="test-anthropic-api-key",
        EMAIL_HOST="localhost",
        EMAIL_PORT=587,
        EMAIL_USERNAME="test@example.com",
        EMAIL_PASSWORD="test-password",
        FRONTEND_URL="http://localhost:3000",
        API_V1_PREFIX="/api/v1",
    )


@pytest.fixture(scope="function")
def mock_jwt_service() -> JWTService:
    """Provide mock JWT service."""
    service = Mock(spec=JWTService)
    service.encode_token = Mock(return_value="mock-jwt-token")
    service.decode_token = Mock(return_value={"user_id": "test-user-id", "exp": 1234567890})
    service.verify_token = Mock(return_value=True)
    return service


@pytest.fixture(scope="function")
def mock_auth_service(mock_jwt_service) -> AuthService:
    """Provide mock auth service."""
    service = Mock(spec=AuthService)
    service.authenticate_user = Mock(return_value=User(
        id="test-user-id",
        email="test@example.com",
        username="testuser",
        is_active=True
    ))
    service.create_access_token = Mock(return_value="mock-access-token")
    service.get_current_user = Mock(return_value=User(
        id="test-user-id",
        email="test@example.com",
        username="testuser",
        is_active=True
    ))
    return service


# HTTP client fixtures
@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="function")
async def authenticated_async_client(async_client: AsyncClient, mock_auth_service) -> AsyncGenerator[AsyncClient, None]:
    """Provide authenticated async HTTP client."""
    # Mock authentication
    app.dependency_overrides[get_db_session] = lambda: mock_auth_service

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Set authentication headers
        client.headers.update({"Authorization": "Bearer mock-jwt-token"})
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture(scope="function")
def test_user_data() -> Dict[str, Any]:
    """Provide test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture(scope="function")
def test_organization_data() -> Dict[str, Any]:
    """Provide test organization data."""
    return {
        "name": "Test Organization",
        "slug": "test-org",
        "description": "Test organization for testing",
        "settings": {"theme": "dark", "notifications": True},
    }


@pytest.fixture(scope="function")
def test_project_data() -> Dict[str, Any]:
    """Provide test project data."""
    return {
        "name": "Test Project",
        "description": "Test project for testing",
        "repository_url": "https://github.com/test/test-repo.git",
        "repository_type": "github",
        "default_branch": "main",
        "languages": ["python", "javascript"],
        "settings": {"auto_analysis": True, "notifications": True},
    }


@pytest.fixture(scope="function")
def test_analysis_data() -> Dict[str, Any]:
    """Provide test analysis data."""
    return {
        "analysis_type": "full",
        "commit_sha": "abc123",
        "branch": "main",
        "config": {"include_patterns": ["*.py", "*.js"], "exclude_patterns": ["tests/*"]},
        "metadata": {"trigger": "manual", "source": "api"},
    }


# Mock fixtures
@pytest.fixture(scope="function")
def mock_s3_client():
    """Provide mock S3 client."""
    client = Mock()
    client.upload_file = Mock(return_value="https://s3.amazonaws.com/test-bucket/test-file")
    client.download_file = Mock(return_value=None)
    client.delete_object = Mock(return_value=None)
    return client


@pytest.fixture(scope="function")
def mock_redis_client():
    """Provide mock Redis client."""
    client = Mock()
    client.set = Mock(return_value=True)
    client.get = Mock(return_value='{"test": "data"}')
    client.delete = Mock(return_value=1)
    client.exists = Mock(return_value=True)
    return client


@pytest.fixture(scope="function")
def mock_celery_app():
    """Provide mock Celery app."""
    app = Mock()
    app.send_task = Mock(return_value=Mock(id="test-task-id"))
    return app


# Utility fixtures
@pytest.fixture(scope="function")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def mock_logger():
    """Provide mock logger."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to tests in integration directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add e2e marker to tests in e2e directory
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


# Test result hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # Log failed test information
        structlog.get_logger().error(
            "Test failed",
            test_name=item.name,
            test_path=str(item.fspath),
            error=str(rep.longrepr)
        )


# Cleanup fixtures
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Clean up test files after test session."""
    yield
    import os
    import glob

    # Clean up test database files
    for db_file in glob.glob("test*.db"):
        try:
            os.remove(db_file)
        except OSError:
            pass

    # Clean up test log files
    for log_file in glob.glob("test*.log"):
        try:
            os.remove(log_file)
        except OSError:
            pass
