# Test Suite Troubleshooting Guide

## Common Issues and Solutions

### Table of Contents
1. [Test Environment Issues](#test-environment-issues)
2. [Test Execution Issues](#test-execution-issues)
3. [Test Coverage Issues](#test-coverage-issues)
4. [Performance Issues](#performance-issues)
5. [Browser Testing Issues](#browser-testing-issues)
6. [Database Issues](#database-issues)
7. [Integration Issues](#integration-issues)
8. [Security Test Issues](#security-test-issues)

## Test Environment Issues

### Virtual Environment Problems

#### Issue: Virtual environment not activating
```bash
# Solution
# Windows
.\venv\Scripts\activate
# Unix/Linux
source venv/bin/activate
```

#### Issue: Package installation failures
```bash
# Solutions
# Clear pip cache
pip cache purge

# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements-test.txt -v
```

### Python Version Conflicts

#### Issue: Incompatible Python version
```bash
# Check Python version
python --version

# Solution: Use pyenv to manage Python versions
pyenv install 3.8.10
pyenv local 3.8.10
```

## Test Execution Issues

### Test Discovery Problems

#### Issue: Tests not being discovered
```python
# Check test naming
# Good
def test_feature():
    pass

# Bad
def feature_test():
    pass
```

#### Issue: Test path configuration
```bash
# Run pytest with verbose discovery
pytest --collect-only -v

# Check pytest configuration
pytest --setup-plan
```

### Test Failures

#### Issue: Flaky tests
```python
# Add retries to flaky tests
@pytest.mark.flaky(reruns=3)
def test_unstable_feature():
    pass
```

#### Issue: Order-dependent tests
```python
# Use explicit ordering
@pytest.mark.run(order=1)
def test_first():
    pass

@pytest.mark.run(order=2)
def test_second():
    pass
```

## Test Coverage Issues

### Low Coverage

#### Issue: Missing coverage reports
```bash
# Run with coverage
pytest --cov=webbly --cov-report=html

# Check specific paths
pytest --cov=webbly/specific/path
```

#### Issue: Excluded code
```ini
# Coverage configuration (.coveragerc)
[run]
omit =
    */tests/*
    */migrations/*
```

## Performance Issues

### Slow Tests

#### Issue: Tests taking too long
```python
# Profile slow tests
pytest --durations=10

# Run specific test with profiling
pytest --profile test_slow.py
```

#### Issue: Resource leaks
```python
# Use cleanup fixtures
@pytest.fixture
def resource():
    r = create_resource()
    yield r
    cleanup_resource(r)
```

## Browser Testing Issues

### Selenium Problems

#### Issue: WebDriver not found
```python
# Set up WebDriver manager
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
```

#### Issue: Browser crashes
```python
# Add error handling
try:
    driver.get(url)
except WebDriverException:
    driver.quit()
    driver = webdriver.Chrome()
    driver.get(url)
```

## Database Issues

### Connection Problems

#### Issue: Database connection failures
```python
# Check connection settings
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/test_db'

# Verify database exists
pytest --setup-show
```

#### Issue: Transaction rollback failures
```python
# Use transaction fixtures
@pytest.fixture(autouse=True)
def db_transaction():
    connection = db.engine.connect()
    transaction = connection.begin()
    yield
    transaction.rollback()
    connection.close()
```

## Integration Issues

### Service Dependencies

#### Issue: External service unavailable
```python
# Mock external services
@pytest.fixture
def mock_service():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            'http://api.example.com',
            json={'status': 'ok'}
        )
        yield rsps
```

#### Issue: Race conditions
```python
# Add waits and retries
def wait_for_condition(condition, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(0.1)
    return False
```

## Security Test Issues

### Scan Failures

#### Issue: Security scan timeouts
```python
# Adjust scan timeout
@pytest.mark.timeout(300)
def test_security_scan():
    scanner = SecurityScanner()
    results = scanner.scan()
    assert results.vulnerabilities == []
```

#### Issue: False positives
```python
# Add scan exclusions
scanner = SecurityScanner(
    exclusions=[
        'known-false-positive-1',
        'known-false-positive-2'
    ]
)
```

## Debug Techniques

### Debugging Tools

```python
# Use pytest-pdb
pytest --pdb

# Use print debugging
pytest -s

# Use logging
import logging
logging.debug("Debug info")
```

### Test Information

```bash
# Show test information
pytest --verbose

# Show fixture information
pytest --setup-show

# Show markers
pytest --markers
```

## Common Error Messages

### "fixture not found"
```python
# Solution: Check fixture availability
@pytest.fixture(scope='session')
def missing_fixture():
    return 'fixture value'
```

### "assert failed"
```python
# Solution: Use detailed assertions
from pytest import approx
assert value == approx(expected, rel=1e-6)
```

## Best Practices

### Test Isolation
```python
# Use fresh fixtures
@pytest.fixture(autouse=True)
def clean_environment():
    # Setup
    yield
    # Cleanup
```

### Resource Management
```python
# Use context managers
with managed_resource() as resource:
    test_with_resource(resource)
```

## Getting Help

1. Check the logs
   ```bash
   pytest --log-cli-level=DEBUG
   ```

2. Generate report
   ```bash
   pytest --html=report.html
   ```

3. Contact support
   - Open an issue
   - Include test output
   - Share environment details

## Prevention

1. Regular Maintenance
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements-test.txt
   
   # Check for security issues
   safety check
   ```

2. Test Hygiene
   ```bash
   # Run linting
   flake8 tests/
   
   # Run type checking
   mypy tests/
   ```

3. Documentation
   ```bash
   # Generate documentation
   pytest --doc
   ```

Remember to:
- Keep dependencies updated
- Clean test environment regularly
- Document issues and solutions
- Share knowledge with team
