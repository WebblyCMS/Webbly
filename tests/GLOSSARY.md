# Test Suite Glossary

## A

### Assertion
A statement that verifies a specific condition or expectation in a test.
```python
assert user.is_authenticated
assert_valid_response(response)
```

### Arrange-Act-Assert (AAA)
A pattern for structuring tests with three distinct phases: setup, execution, and verification.
```python
# Arrange
user = create_test_user()
# Act
response = user.login()
# Assert
assert response.status_code == 200
```

## B

### Benchmark Test
A test that measures and verifies performance metrics.
```python
@pytest.mark.benchmark
def test_performance():
    result = benchmark(function_under_test)
    assert result.stats.mean < 0.1
```

### Browser Test
A test that verifies web application behavior in a browser environment.
```python
def test_browser_interaction(selenium):
    selenium.get(url)
    element = selenium.find_element_by_id('button')
    element.click()
```

## C

### Coverage
The measure of how much code is exercised by tests.
```python
# Run tests with coverage
pytest --cov=webbly
```

### Continuous Integration (CI)
The practice of automatically running tests when code changes are pushed.
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
```

## D

### Database Fixture
A fixture that provides a test database instance.
```python
@pytest.fixture
def database():
    db = setup_test_database()
    yield db
    cleanup_database(db)
```

### Dependency Injection
A technique where dependencies are passed into a test rather than created within it.
```python
def test_feature(database, cache, mailer):
    feature = Feature(database, cache, mailer)
```

## E

### End-to-End Test (E2E)
A test that verifies the entire system from start to finish.
```python
def test_user_workflow():
    user = register_user()
    post = user.create_post()
    comment = other_user.comment_on(post)
```

### Environment Variable
A configuration value set in the test environment.
```python
os.environ['TESTING'] = 'true'
TEST_DATABASE_URL = os.getenv('TEST_DB_URL')
```

## F

### Factory
A pattern for creating test objects with default values.
```python
class UserFactory:
    @staticmethod
    def create(**kwargs):
        return User(**{**defaults, **kwargs})
```

### Fixture
A function that provides test data or test environment setup.
```python
@pytest.fixture
def test_user():
    return create_test_user()
```

## I

### Integration Test
A test that verifies multiple components working together.
```python
def test_user_post_creation(database, cache):
    user.create_post()
    assert cache.get(f'user_{user.id}_posts') is not None
```

### Isolation
The principle that tests should be independent of each other.
```python
def test_isolated():
    data = create_fresh_data()  # Not shared between tests
```

## M

### Mock
A substitute for a real object used in testing.
```python
@mock.patch('services.email')
def test_notification(mock_email):
    send_notification()
    mock_email.send.assert_called_once()
```

### Marker
A decorator that adds metadata to a test.
```python
@pytest.mark.slow
def test_long_running():
    perform_lengthy_operation()
```

## P

### Parameterized Test
A test that runs multiple times with different inputs.
```python
@pytest.mark.parametrize('input,expected', [
    ('test1', True),
    ('test2', False)
])
def test_validation(input, expected):
    assert validate(input) == expected
```

### Performance Test
A test that verifies system performance characteristics.
```python
def test_response_time():
    start = time.time()
    response = client.get('/api/data')
    duration = time.time() - start
    assert duration < 0.1
```

## R

### Regression Test
A test that verifies a previously fixed bug doesn't recur.
```python
def test_bug_fix():
    # Verify specific bug #1234 doesn't recur
    assert process_edge_case() == expected_result
```

### Resource Cleanup
The practice of cleaning up resources after tests.
```python
def test_with_cleanup():
    resource = allocate_resource()
    try:
        use_resource(resource)
    finally:
        cleanup_resource(resource)
```

## S

### Security Test
A test that verifies security requirements.
```python
def test_xss_prevention():
    malicious_input = '<script>alert("xss")</script>'
    assert sanitize(malicious_input) == safe_output
```

### Stub
A simplified implementation used in testing.
```python
class StubPaymentGateway:
    def process_payment(self, amount):
        return {'status': 'success'}
```

## T

### Test Case
A single test function or method.
```python
def test_user_login():
    """Test case for user login."""
    pass
```

### Test Suite
A collection of related tests.
```python
class TestUserAuthentication:
    """Suite of authentication tests."""
    pass
```

## U

### Unit Test
A test that verifies a single component in isolation.
```python
def test_password_validation():
    assert validate_password('Password123!') is True
```

### URL Pattern
A pattern for generating test URLs.
```python
def get_test_url(endpoint):
    return f'http://testserver/{endpoint}'
```

## V

### Validation Test
A test that verifies input validation.
```python
def test_input_validation():
    with pytest.raises(ValidationError):
        process_invalid_input()
```

### Virtual Environment
An isolated Python environment for testing.
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

## Terms to Remember

1. **Test Pyramid**
   - Unit tests form the base
   - Integration tests in the middle
   - End-to-end tests at the top

2. **Test Doubles**
   - Dummy: Placeholder objects
   - Stub: Provides predefined responses
   - Spy: Records information about usage
   - Mock: Verifies expected interactions
   - Fake: Working implementation, but not production-ready

3. **Testing Principles**
   - F.I.R.S.T.
     - Fast
     - Independent
     - Repeatable
     - Self-validating
     - Timely

4. **Common Acronyms**
   - TDD: Test-Driven Development
   - BDD: Behavior-Driven Development
   - CI/CD: Continuous Integration/Continuous Deployment
   - E2E: End-to-End
   - SUT: System Under Test

5. **Test Categories**
   - Smoke Tests
   - Regression Tests
   - Load Tests
   - Stress Tests
   - Security Tests
   - Performance Tests
   - Acceptance Tests
