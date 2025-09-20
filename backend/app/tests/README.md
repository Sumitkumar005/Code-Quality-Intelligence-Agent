# CQIA Test Suite

Comprehensive testing framework for the Code Quality Intelligence Agent (CQIA) application.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                # Pytest configuration and fixtures
├── README.md                  # This file
├── unit/                      # Unit tests
│   ├── __init__.py
│   ├── services/              # Service layer unit tests
│   ├── models/                # Model layer unit tests
│   └── utils/                 # Utility function tests
├── integration/               # Integration tests
│   ├── __init__.py
│   ├── api/                   # API endpoint integration tests
│   └── services/              # Service integration tests
└── e2e/                       # End-to-end tests
    └── __init__.py
```

## 🚀 Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run with verbose output
pytest -v

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
pytest -m "e2e"
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# API endpoint tests
pytest tests/integration/api/ -v

# Service tests
pytest tests/unit/services/ -v

# Model tests
pytest tests/unit/models/ -v

# Utility tests
pytest tests/unit/utils/ -v
```

### Run Tests with Markers

```bash
# Run slow tests
pytest -m "slow"

# Run fast tests only
pytest -m "not slow"

# Run authentication tests
pytest -m "auth"

# Run database tests
pytest -m "database"

# Run API tests
pytest -m "api"
```

### Run Tests in Parallel

```bash
# Parallel execution
pytest -n auto

# Specify number of workers
pytest -n 4
```

## 📋 Test Categories

### Unit Tests (`tests/unit/`)

Isolated tests for individual components:

- **Services** (`tests/unit/services/`): Test business logic in isolation
- **Models** (`tests/unit/models/`): Test database models and relationships
- **Utils** (`tests/unit/utils/`): Test utility functions and helpers

### Integration Tests (`tests/integration/`)

Tests for component interactions:

- **API** (`tests/integration/api/`): Test HTTP endpoints and request/response handling
- **Services** (`tests/integration/services/`): Test service layer integrations

### End-to-End Tests (`tests/e2e/`)

Complete workflow tests that simulate real user scenarios.

## 🛠️ Test Configuration

### Pytest Configuration (`pytest.ini`)

The `pytest.ini` file contains comprehensive configuration:

- **Coverage**: 80% minimum coverage requirement
- **Markers**: Custom test markers for categorization
- **Output**: Verbose output with short tracebacks
- **Parallel**: Support for parallel test execution

### Fixtures (`conftest.py`)

The `conftest.py` file provides:

- **Database fixtures**: Test database setup and teardown
- **HTTP client fixtures**: Async HTTP clients for API testing
- **Mock fixtures**: Mocked services and external dependencies
- **Test data fixtures**: Sample data for testing
- **Authentication fixtures**: Authenticated test clients

## 📝 Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock

class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def auth_service(self, mock_jwt_service):
        """Create AuthService instance with mocked dependencies."""
        return AuthService(jwt_service=mock_jwt_service)

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
```

### Integration Test Example

```python
import pytest

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
```

## 🎯 Test Markers

Use these markers to categorize your tests:

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.unit
@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.api
@pytest.mark.database
@pytest.mark.external
@pytest.mark.mock
```

## 📊 Coverage Reports

Generate coverage reports:

```bash
# HTML report
pytest --cov=backend --cov-report=html

# XML report (for CI/CD)
pytest --cov=backend --cov-report=xml

# Terminal report with missing lines
pytest --cov=backend --cov-report=term-missing
```

Coverage reports are saved to:
- `htmlcov/index.html` (HTML report)
- `coverage.xml` (XML report)

## 🔧 Debugging Tests

### Debug Failed Tests

```bash
# Stop at first failure
pytest -x

# Show more detailed output
pytest -v -s

# Show local variables on failure
pytest --tb=long
```

### Debug with PDB

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on specific test
pytest -k "test_name" --pdb
```

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

## 📈 Best Practices

### Test Organization

1. **One test per behavior**: Each test should verify one specific behavior
2. **Descriptive names**: Use descriptive test method names
3. **Arrange-Act-Assert**: Follow the AAA pattern
4. **Independent tests**: Tests should not depend on each other
5. **Fast execution**: Keep tests fast for quick feedback

### Mocking Strategy

1. **Mock external dependencies**: Database, APIs, file systems
2. **Use fixtures**: For setup and teardown logic
3. **Mock at boundaries**: Mock services, not implementations
4. **Real data**: Use real data structures when possible

### Database Testing

1. **Test isolation**: Each test gets a clean database state
2. **Rollback transactions**: Use transactions for fast cleanup
3. **Real models**: Test with actual model instances
4. **Migration testing**: Test database migrations separately

## 🐛 Troubleshooting

### Common Issues

1. **Database connection errors**: Check database URL in test configuration
2. **Import errors**: Ensure test files have proper `__init__.py` files
3. **Async test issues**: Use `@pytest.mark.asyncio` for async tests
4. **Fixture errors**: Check fixture scope and dependencies

### Performance Issues

1. **Slow tests**: Use markers to skip slow tests in development
2. **Database cleanup**: Ensure proper transaction rollback
3. **Parallel execution**: Use pytest-xdist for faster test runs
4. **Coverage overhead**: Run coverage only when needed

## 📞 Support

For questions about the test suite:

1. Check this README first
2. Look at existing test examples
3. Check the pytest documentation
4. Ask the development team

---

**Happy Testing! 🧪**
