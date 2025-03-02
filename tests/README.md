# Webbly CMS Test Suite

This directory contains the test suite for Webbly CMS. The test suite is built using pytest and includes unit tests, integration tests, performance tests, security tests, and browser compatibility tests.

## Directory Structure

```
tests/
├── fixtures/              # Test fixtures and utilities
│   ├── assertions.py     # Custom test assertions
│   ├── benchmarks.py     # Performance benchmarking utilities
│   ├── cleanup.py        # Test cleanup utilities
│   ├── compatibility.py  # Browser compatibility testing
│   ├── config.py         # Test configuration
│   ├── data.py          # Test data generation
│   ├── decorators.py     # Test decorators
│   ├── documentation.py  # Test documentation generation
│   ├── exceptions.py     # Custom test exceptions
│   ├── init.py          # Test suite initialization
│   ├── integration.py    # Integration testing utilities
│   ├── logging.py       # Test logging utilities
│   ├── markers.py       # Custom pytest markers
│   ├── matchers.py      # Custom test matchers
│   ├── performance.py   # Performance testing utilities
│   ├── profiling.py     # Code profiling utilities
│   ├── reporters.py     # Test result reporting
│   ├── security.py      # Security testing utilities
│   ├── setup.py         # Test environment setup
│   ├── statistics.py    # Test statistics collection
│   ├── utils.py         # Common test utilities
│   └── validation.py    # Data validation utilities
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── functional/          # Functional tests
├── performance/         # Performance tests
├── security/           # Security tests
└── conftest.py         # pytest configuration
```

## Setup

1. Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

2. Configure test environment:
```bash
cp .env.example .env.test
# Edit .env.test with appropriate test settings
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test types:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Functional tests
pytest tests/functional/

# Performance tests
pytest tests/performance/

# Security tests
pytest tests/security/
```

### Run tests with specific markers:
```bash
# Run slow tests
pytest -m slow

# Run tests requiring database
pytest -m requires_db

# Run tests requiring cache
pytest -m requires_cache
```

### Run tests with coverage:
```bash
pytest --cov=webbly --cov-report=html
```

## Test Reports

Test reports are generated in the following directories:

- HTML test reports: `tests/reports/html/`
- Coverage reports: `tests/reports/coverage/`
- Performance reports: `tests/reports/performance/`
- Security reports: `tests/reports/security/`

## Writing Tests

### Using Test Fixtures

```python
from tests.fixtures import (
    assert_valid_response,
    assert_valid_html,
    data_generator,
    performance_test
)

def test_homepage(client):
    """Test homepage rendering."""
    response = client.get('/')
    assert_valid_response(response)
    assert_valid_html(response.data)

def test_create_post(client, logged_in_admin):
    """Test post creation."""
    post_data = data_generator.generate_post()
    response = client.post('/admin/posts/new', data=post_data)
    assert response.status_code == 302
```

### Using Test Decorators

```python
from tests.fixtures import (
    requires_login,
    requires_admin,
    performance_test,
    track_test
)

@requires_login
def test_user_profile(client):
    """Test user profile page."""
    response = client.get('/profile')
    assert response.status_code == 200

@requires_admin
def test_admin_dashboard(client):
    """Test admin dashboard."""
    response = client.get('/admin')
    assert response.status_code == 200

@performance_test(iterations=100)
def test_homepage_performance(client):
    """Test homepage performance."""
    response = client.get('/')
    assert response.status_code == 200
```

### Using Test Data Generation

```python
from tests.fixtures import data_generator

def test_user_registration(client):
    """Test user registration."""
    user_data = data_generator.generate_user()
    response = client.post('/auth/register', data=user_data)
    assert response.status_code == 302
```

## Contributing

1. Write tests for new features
2. Ensure all tests pass before submitting PR
3. Update test documentation as needed
4. Add appropriate test markers
5. Include performance tests for critical paths
6. Add security tests for sensitive features

## Best Practices

1. Use appropriate test markers
2. Write descriptive test names and docstrings
3. Use test fixtures for common operations
4. Clean up test data after tests
5. Keep tests focused and atomic
6. Use appropriate assertions
7. Handle test dependencies properly
8. Document complex test scenarios
9. Profile performance-critical tests
10. Include security checks for vulnerable areas

## Troubleshooting

### Common Issues

1. Test database connection issues:
   - Check database configuration in .env.test
   - Ensure test database exists
   - Verify database permissions

2. Cache-related test failures:
   - Clear test cache before running tests
   - Check cache configuration
   - Use appropriate cache fixtures

3. Browser compatibility test failures:
   - Ensure browser drivers are installed
   - Check browser configurations
   - Verify Selenium setup

### Debug Tools

1. Use pytest -v for verbose output
2. Enable debug logging
3. Use pytest-pdb for debugging
4. Check test logs in tests/logs/
5. Review test reports for details

## Maintenance

1. Regularly update test dependencies
2. Clean up test data and artifacts
3. Review and update test documentation
4. Monitor test coverage
5. Optimize slow tests
6. Update browser configurations
7. Review security test cases
