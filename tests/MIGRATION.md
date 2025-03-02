# Test Suite Migration Guide

## Overview

This guide helps you migrate between different versions of the Webbly CMS test suite. It documents breaking changes, deprecations, and required updates for each version.

## Version Migration Paths

### 1.0.0 → 1.1.0

#### Breaking Changes
1. Test Configuration
```python
# Old format
TEST_CONFIG = {
    'database': 'sqlite:///:memory:'
}

# New format
TEST_CONFIG = {
    'database': {
        'url': 'sqlite:///:memory:',
        'options': {'echo': False}
    }
}
```

2. Fixture Changes
```python
# Old fixture
@pytest.fixture
def test_user():
    return create_test_user()

# New fixture with cleanup
@pytest.fixture
def test_user():
    user = create_test_user()
    yield user
    cleanup_user(user)
```

#### Deprecations
```python
# Deprecated
from tests.utils import old_helper  # Will be removed in 2.0.0

# Use instead
from tests.utils import new_helper
```

#### Required Updates
1. Update dependencies:
```bash
pip install -r requirements-test.txt
```

2. Update test configurations:
```bash
cp .env.test.example .env.test
# Update settings in .env.test
```

### 1.1.0 → 1.2.0

#### New Features
```python
# New async testing support
@pytest.mark.asyncio
async def test_async_feature():
    result = await async_operation()
    assert result.success
```

#### Performance Improvements
```python
# New parallel test execution
pytest -n auto

# New fixture optimization
@pytest.fixture(scope='session')
def optimized_resource():
    return setup_resource()
```

## Breaking Changes Guide

### Database Changes

#### Pre-1.0.0
```python
# Old database setup
def setup_database():
    return connect_db()
```

#### Post-1.0.0
```python
# New database setup with context
@contextmanager
def database_context():
    db = connect_db()
    yield db
    db.close()
```

### Authentication Changes

#### Pre-1.0.0
```python
# Old auth testing
def test_auth():
    user = login_user()
    assert user.is_authenticated
```

#### Post-1.0.0
```python
# New auth testing with token
def test_auth():
    token = generate_auth_token()
    user = authenticate_token(token)
    assert user.is_authenticated
```

## Deprecation Timeline

### Version 1.0.0
- Deprecated: `old_helper`
- Alternative: `new_helper`
- Removal: Version 2.0.0

### Version 1.1.0
- Deprecated: `legacy_fixture`
- Alternative: `modern_fixture`
- Removal: Version 2.0.0

## Update Process

### 1. Backup
```bash
# Backup test configurations
cp .env.test .env.test.backup

# Backup custom fixtures
cp -r tests/fixtures tests/fixtures.backup
```

### 2. Dependencies
```bash
# Update dependencies
pip install --upgrade -r requirements-test.txt

# Verify installation
pytest --version
```

### 3. Configuration
```bash
# Update configuration
cp .env.test.example .env.test
# Manual updates needed for custom settings
```

### 4. Code Updates
```python
# Update imports
from tests.utils import new_helper  # New import

# Update fixtures
@pytest.fixture
def updated_fixture():
    # New fixture implementation
    pass
```

### 5. Verification
```bash
# Run tests
pytest

# Check coverage
pytest --cov

# Verify reports
pytest --html=report.html
```

## Common Migration Issues

### 1. Database Connections
```python
# Problem: Connection leaks
# Old code
def test_db():
    db = connect_db()
    # Test code
    # No cleanup

# Solution
def test_db():
    with database_context() as db:
        # Test code
```

### 2. Async Support
```python
# Problem: Sync code in async tests
# Old code
async def test_async():
    result = sync_operation()  # Blocking

# Solution
async def test_async():
    result = await async_operation()
```

### 3. Resource Management
```python
# Problem: Resource leaks
# Old code
def test_resource():
    resource = allocate()
    # No cleanup

# Solution
def test_resource():
    with managed_resource() as resource:
        # Test code
```

## Version-Specific Notes

### Version 1.0.0
- Initial stable release
- Basic test framework
- Core fixtures

### Version 1.1.0
- Added async support
- Improved performance
- Enhanced reporting

### Version 1.2.0
- Security improvements
- New test patterns
- Extended fixtures

## Rollback Procedures

### Quick Rollback
```bash
# Restore configuration
cp .env.test.backup .env.test

# Restore fixtures
cp -r tests/fixtures.backup tests/fixtures

# Downgrade dependencies
pip install -r requirements-test-1.0.0.txt
```

### Clean Rollback
```bash
# Remove current version
rm -rf tests/

# Restore from backup
git checkout v1.0.0 tests/
```

## Best Practices

### During Migration
1. Update gradually
2. Test thoroughly
3. Monitor performance
4. Check coverage
5. Update documentation

### After Migration
1. Clean up old code
2. Update CI/CD
3. Train team members
4. Update documentation
5. Monitor for issues

## Support

### Getting Help
1. Check documentation
2. Review examples
3. Open issues
4. Contact support

### Reporting Issues
1. Provide version info
2. Include error logs
3. Add reproduction steps
4. Describe expected behavior

## Future Changes

### Planned Changes
1. New test patterns
2. Enhanced security
3. Better performance
4. More automation

### Preparation
1. Follow roadmap
2. Monitor announcements
3. Plan updates
4. Test early
5. Provide feedback

Remember to:
- Test thoroughly
- Update gradually
- Monitor performance
- Keep backups
- Document changes
