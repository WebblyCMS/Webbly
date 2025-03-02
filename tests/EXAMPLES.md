# Test Examples

## Common Testing Scenarios

### 1. Basic Unit Test
```python
def test_user_creation():
    """Test basic user creation."""
    # Arrange
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123!'
    }
    
    # Act
    user = User.create(user_data)
    
    # Assert
    assert user.username == user_data['username']
    assert user.email == user_data['email']
    assert user.check_password(user_data['password'])
```

### 2. Integration Test
```python
def test_user_post_creation(database, cache):
    """Test user creating a post with caching."""
    # Arrange
    user = create_test_user()
    post_data = {'title': 'Test Post', 'content': 'Content'}
    
    # Act
    post = user.create_post(post_data)
    cached_post = cache.get(f'post_{post.id}')
    
    # Assert
    assert post in database.session.query(Post).all()
    assert cached_post['title'] == post_data['title']
```

### 3. API Test
```python
def test_api_endpoint(client):
    """Test API endpoint with authentication."""
    # Arrange
    auth_token = create_auth_token()
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Act
    response = client.get('/api/data', headers=headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'data' in response.json
```

### 4. Form Validation
```python
def test_form_validation():
    """Test form validation with invalid data."""
    # Arrange
    form_data = {
        'email': 'invalid-email',
        'password': 'short'
    }
    form = LoginForm(data=form_data)
    
    # Act
    is_valid = form.validate()
    
    # Assert
    assert not is_valid
    assert 'email' in form.errors
    assert 'password' in form.errors
```

### 5. Database Operations
```python
def test_database_transaction(session):
    """Test database transaction rollback."""
    # Arrange
    initial_count = session.query(User).count()
    
    # Act
    try:
        with session.begin():
            user = User(username='test', email='invalid')
            session.add(user)
            raise ValueError("Trigger rollback")
    except ValueError:
        pass
    
    # Assert
    final_count = session.query(User).count()
    assert final_count == initial_count
```

### 6. Async Testing
```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test asynchronous operation."""
    # Arrange
    async with AsyncClient() as client:
        # Act
        response = await client.get('/async-endpoint')
        
        # Assert
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
```

### 7. File Operations
```python
def test_file_upload(tmp_path):
    """Test file upload handling."""
    # Arrange
    file_content = b'Test file content'
    file_path = tmp_path / 'test.txt'
    file_path.write_bytes(file_content)
    
    # Act
    with open(file_path, 'rb') as f:
        response = client.post('/upload', files={'file': f})
    
    # Assert
    assert response.status_code == 200
    assert response.json['filename'] == 'test.txt'
```

### 8. Cache Operations
```python
def test_cache_operations(cache):
    """Test cache set and get operations."""
    # Arrange
    key = 'test_key'
    value = {'data': 'test_value'}
    
    # Act
    cache.set(key, value)
    cached_value = cache.get(key)
    
    # Assert
    assert cached_value == value
```

### 9. Authentication Test
```python
def test_user_authentication(client):
    """Test user login process."""
    # Arrange
    credentials = {
        'username': 'testuser',
        'password': 'Password123!'
    }
    
    # Act
    response = client.post('/login', json=credentials)
    
    # Assert
    assert response.status_code == 200
    assert 'access_token' in response.json
```

### 10. Error Handling
```python
def test_error_handling():
    """Test error handling with invalid input."""
    # Arrange
    invalid_data = {'key': 'invalid'}
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        process_data(invalid_data)
    assert str(exc_info.value) == 'Invalid data format'
```

### 11. Browser Testing
```python
def test_browser_interaction(selenium):
    """Test browser interaction with JavaScript."""
    # Arrange
    selenium.get('/login')
    username_input = selenium.find_element_by_id('username')
    password_input = selenium.find_element_by_id('password')
    
    # Act
    username_input.send_keys('testuser')
    password_input.send_keys('Password123!')
    selenium.find_element_by_id('submit').click()
    
    # Assert
    assert selenium.current_url == '/dashboard'
```

### 12. Performance Testing
```python
@pytest.mark.benchmark
def test_performance(benchmark):
    """Test performance of critical operation."""
    # Arrange
    data = prepare_test_data()
    
    # Act & Assert
    result = benchmark(lambda: process_data(data))
    assert result.stats.mean < 0.1
```

### 13. Security Testing
```python
def test_sql_injection_prevention():
    """Test SQL injection prevention."""
    # Arrange
    malicious_input = "'; DROP TABLE users; --"
    
    # Act
    result = User.find_by_username(malicious_input)
    
    # Assert
    assert result is None
    # Verify users table still exists
    assert User.query.count() > 0
```

### 14. Mocking Example
```python
def test_external_service(mocker):
    """Test with mocked external service."""
    # Arrange
    mock_service = mocker.patch('services.external.api_call')
    mock_service.return_value = {'status': 'success'}
    
    # Act
    result = process_external_data()
    
    # Assert
    assert result['status'] == 'success'
    mock_service.assert_called_once()
```

### 15. Parameterized Testing
```python
@pytest.mark.parametrize('input,expected', [
    ('test1', True),
    ('test2', False),
    ('test3', True)
])
def test_parameterized(input, expected):
    """Test with multiple input cases."""
    # Act
    result = validate_input(input)
    
    # Assert
    assert result == expected
```

## Best Practices Demonstrated

1. Clear Test Structure
   - Arrange-Act-Assert pattern
   - Descriptive test names
   - Proper documentation

2. Resource Management
   - Proper cleanup
   - Context managers
   - Temporary resources

3. Error Handling
   - Exception testing
   - Validation checks
   - Edge cases

4. Test Independence
   - No shared state
   - Isolated resources
   - Clear setup/teardown

5. Maintainability
   - Readable code
   - Reusable fixtures
   - Clear assertions

## Using These Examples

1. Copy and adapt the examples
2. Follow the patterns shown
3. Maintain consistent style
4. Add appropriate documentation
5. Include proper error handling

Remember to:
- Test both success and failure cases
- Clean up resources
- Use appropriate assertions
- Follow security best practices
- Consider performance implications
