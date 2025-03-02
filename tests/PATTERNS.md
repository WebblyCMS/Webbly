# Test Patterns and Best Practices

## Overview

This document outlines common test patterns and best practices used in the Webbly CMS test suite. These patterns help maintain consistency, readability, and maintainability across the test suite.

## Test Organization Patterns

### 1. Arrange-Act-Assert (AAA)
```python
def test_user_registration():
    """Test user registration using AAA pattern."""
    # Arrange
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    
    # Act
    response = register_user(user_data)
    
    # Assert
    assert response.status_code == 200
    assert User.objects.filter(email=user_data['email']).exists()
```

### 2. Given-When-Then (BDD Style)
```python
@pytest.mark.bdd
def test_post_creation():
    """Test post creation using BDD style."""
    # Given
    user = create_test_user()
    post_data = generate_post_data()
    
    # When
    post = user.create_post(post_data)
    
    # Then
    assert post.title == post_data['title']
    assert post.author == user
```

## Fixture Patterns

### 1. Factory Fixtures
```python
@pytest.fixture
def user_factory():
    """Create user factory fixture."""
    def _create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        defaults.update(kwargs)
        return User.objects.create(**defaults)
    return _create_user
```

### 2. Resource Fixtures
```python
@pytest.fixture
def database():
    """Database fixture with cleanup."""
    # Setup
    db = setup_test_database()
    
    yield db
    
    # Cleanup
    db.cleanup()
```

## Test Data Patterns

### 1. Builder Pattern
```python
class TestDataBuilder:
    """Build complex test data."""
    
    def __init__(self):
        self.data = {}
    
    def with_user(self, user):
        self.data['user'] = user
        return self
    
    def with_posts(self, posts):
        self.data['posts'] = posts
        return self
    
    def build(self):
        return self.data
```

### 2. Object Mother Pattern
```python
class TestDataFactory:
    """Create standard test objects."""
    
    @staticmethod
    def create_test_user():
        return User(
            username='testuser',
            email='test@example.com',
            password='Password123!'
        )
    
    @staticmethod
    def create_test_post():
        return Post(
            title='Test Post',
            content='Test content'
        )
```

## Assertion Patterns

### 1. Custom Assertions
```python
def assert_valid_user(user):
    """Assert user object is valid."""
    assert user.username
    assert '@' in user.email
    assert user.password_hash
    assert user.created_at

def assert_valid_response(response):
    """Assert response is valid."""
    assert response.status_code in [200, 201]
    assert response.content_type == 'application/json'
    assert response.json
```

### 2. Context Assertions
```python
@contextmanager
def assert_database_queries(count):
    """Assert number of database queries."""
    initial_count = get_query_count()
    yield
    final_count = get_query_count()
    assert final_count - initial_count == count
```

## Error Handling Patterns

### 1. Exception Testing
```python
def test_invalid_input():
    """Test handling of invalid input."""
    with pytest.raises(ValueError) as exc_info:
        process_input(invalid_data)
    assert str(exc_info.value) == 'Invalid input'
```

### 2. Error Case Matrix
```python
@pytest.mark.parametrize('input,expected_error', [
    ('', 'Empty input'),
    (None, 'None input'),
    ('invalid', 'Invalid format')
])
def test_error_cases(input, expected_error):
    """Test various error cases."""
    with pytest.raises(ValueError) as exc_info:
        process_input(input)
    assert str(exc_info.value) == expected_error
```

## Performance Patterns

### 1. Resource Management
```python
@pytest.fixture
def managed_resource():
    """Manage test resource lifecycle."""
    resource = allocate_resource()
    try:
        yield resource
    finally:
        cleanup_resource(resource)
```

### 2. Performance Testing
```python
def test_performance():
    """Test performance with timing."""
    start_time = time.time()
    
    result = perform_operation()
    
    duration = time.time() - start_time
    assert duration < MAX_DURATION
    assert result.is_valid
```

## Integration Patterns

### 1. Service Mocking
```python
@pytest.fixture
def mock_service():
    """Mock external service."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            'http://api.example.com',
            json={'status': 'ok'}
        )
        yield rsps
```

### 2. Database Integration
```python
@pytest.mark.integration
def test_database_integration():
    """Test database integration."""
    with transaction.atomic():
        user = create_test_user()
        post = create_test_post(user)
        assert post in user.posts.all()
```

## Security Patterns

### 1. Security Testing
```python
def test_xss_prevention():
    """Test XSS prevention."""
    malicious_input = '<script>alert("xss")</script>'
    safe_output = sanitize_input(malicious_input)
    assert '<script>' not in safe_output
```

### 2. Authentication Testing
```python
def test_authentication():
    """Test authentication flow."""
    with login_user(credentials) as user:
        response = access_protected_resource()
        assert response.status_code == 200
        assert user.is_authenticated
```

## Best Practices

### 1. Test Independence
```python
@pytest.mark.isolated
def test_independent():
    """Independent test."""
    data = prepare_test_data()
    result = process_data(data)
    assert result.is_valid
```

### 2. Clean Up
```python
def test_with_cleanup():
    """Test with cleanup."""
    resource = create_resource()
    try:
        use_resource(resource)
    finally:
        cleanup_resource(resource)
```

### 3. Parameterization
```python
@pytest.mark.parametrize('input,expected', [
    ('test1', True),
    ('test2', False),
    ('test3', True)
])
def test_parameterized(input, expected):
    """Parameterized test cases."""
    result = process_input(input)
    assert result == expected
```

## Anti-Patterns to Avoid

### 1. Test Interdependence
```python
# Bad: Tests depend on each other
def test_first():
    global_data = create_data()

def test_second():
    # Don't use global_data from previous test
    process_data(global_data)
```

### 2. Complex Logic
```python
# Bad: Complex test logic
def test_complex():
    if condition1:
        if condition2:
            # Nested conditions make tests hard to understand
            pass
```

### 3. Hidden Dependencies
```python
# Bad: Hidden dependencies
def test_hidden():
    # Don't rely on external state
    result = process_external_data()
    assert result.is_valid
```

## Implementation Guidelines

1. Follow AAA or Given-When-Then pattern
2. Use appropriate fixtures
3. Clean up resources
4. Write clear assertions
5. Handle errors properly
6. Document complex tests
7. Maintain independence
8. Consider performance
