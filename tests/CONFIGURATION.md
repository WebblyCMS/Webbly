# Test Suite Configuration Guide

## Overview

This guide explains how to configure the Webbly CMS test suite for different environments and use cases.

## Basic Configuration

### Environment Variables

#### .env.test
```ini
# Test environment configuration
TESTING=true
DEBUG=false
SECRET_KEY=test-secret-key

# Database configuration
DATABASE_URL=sqlite:///:memory:
DATABASE_ECHO=false

# Cache configuration
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Email configuration
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
```

### pytest Configuration

#### pytest.ini
```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Execution
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --cov=webbly
    --cov-report=html

# Markers
markers =
    unit: Unit tests
    integration: Integration tests
    functional: Functional tests
    performance: Performance tests
    security: Security tests
```

## Advanced Configuration

### Test Categories

#### conftest.py
```python
def pytest_configure(config):
    """Configure test categories."""
    config.addinivalue_line(
        "markers",
        "slow: Tests that take longer to run"
    )
    
    config.addinivalue_line(
        "markers",
        "requires_db: Tests that require database"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="Need --run-slow option")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
```

### Resource Configuration

#### resources.py
```python
class TestResources:
    """Test resource configuration."""
    
    def __init__(self):
        self.config = {
            'database': {
                'url': os.getenv('DATABASE_URL'),
                'echo': os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
                'pool_size': int(os.getenv('DATABASE_POOL_SIZE', '5'))
            },
            'cache': {
                'type': os.getenv('CACHE_TYPE', 'simple'),
                'url': os.getenv('CACHE_URL'),
                'timeout': int(os.getenv('CACHE_TIMEOUT', '300'))
            },
            'email': {
                'server': os.getenv('MAIL_SERVER'),
                'port': int(os.getenv('MAIL_PORT', '1025')),
                'use_tls': os.getenv('MAIL_USE_TLS', 'false').lower() == 'true'
            }
        }
    
    def get_database_config(self):
        """Get database configuration."""
        return self.config['database']
    
    def get_cache_config(self):
        """Get cache configuration."""
        return self.config['cache']
    
    def get_email_config(self):
        """Get email configuration."""
        return self.config['email']
```

## Environment-Specific Configuration

### Development

#### config/development.py
```python
"""Development test configuration."""

TEST_CONFIG = {
    'environment': 'development',
    'debug': True,
    'database': {
        'url': 'sqlite:///tests/data/dev.db',
        'echo': True
    },
    'cache': {
        'type': 'simple'
    },
    'email': {
        'backend': 'console'
    }
}
```

### Production

#### config/production.py
```python
"""Production test configuration."""

TEST_CONFIG = {
    'environment': 'production',
    'debug': False,
    'database': {
        'url': os.getenv('PROD_DATABASE_URL'),
        'echo': False
    },
    'cache': {
        'type': 'redis',
        'url': os.getenv('PROD_REDIS_URL')
    },
    'email': {
        'backend': 'smtp',
        'host': os.getenv('PROD_SMTP_HOST')
    }
}
```

## Feature Configuration

### Test Features

#### features.py
```python
class TestFeatures:
    """Test feature configuration."""
    
    def __init__(self):
        self.features = {
            'parallel_execution': os.getenv('ENABLE_PARALLEL_TESTS', 'true').lower() == 'true',
            'coverage_reporting': os.getenv('ENABLE_COVERAGE', 'true').lower() == 'true',
            'performance_monitoring': os.getenv('ENABLE_PERFORMANCE', 'true').lower() == 'true',
            'security_scanning': os.getenv('ENABLE_SECURITY', 'true').lower() == 'true'
        }
    
    def is_enabled(self, feature):
        """Check if feature is enabled."""
        return self.features.get(feature, False)
```

### Test Options

#### options.py
```python
class TestOptions:
    """Test execution options."""
    
    def __init__(self):
        self.options = {
            'timeout': int(os.getenv('TEST_TIMEOUT', '30')),
            'retries': int(os.getenv('TEST_RETRIES', '3')),
            'parallel_workers': int(os.getenv('TEST_WORKERS', '4')),
            'fail_fast': os.getenv('TEST_FAIL_FAST', 'false').lower() == 'true'
        }
    
    def get_option(self, name, default=None):
        """Get option value."""
        return self.options.get(name, default)
```

## Logging Configuration

### logging.py
```python
def configure_logging():
    """Configure test logging."""
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(message)s'
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'tests/logs/test.log',
                'formatter': 'standard'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'loggers': {
            '': {
                'handlers': ['file', 'console'],
                'level': os.getenv('TEST_LOG_LEVEL', 'INFO')
            }
        }
    })
```

## Configuration Management

### Loading Configuration

#### config_loader.py
```python
class ConfigLoader:
    """Load test configuration."""
    
    def __init__(self):
        self.config = {}
    
    def load_config(self, environment):
        """Load environment-specific configuration."""
        # Load base config
        self.config.update(self._load_base_config())
        
        # Load environment config
        env_config = self._load_environment_config(environment)
        self.config.update(env_config)
        
        # Load local overrides
        self._load_local_overrides()
    
    def get_config(self):
        """Get loaded configuration."""
        return self.config
```

### Validation

#### config_validator.py
```python
class ConfigValidator:
    """Validate test configuration."""
    
    def validate_config(self, config):
        """Validate configuration values."""
        errors = []
        
        # Check required values
        self._check_required_values(config, errors)
        
        # Validate types
        self._validate_types(config, errors)
        
        # Validate constraints
        self._validate_constraints(config, errors)
        
        return errors
```

## Best Practices

### Configuration Guidelines
1. Use environment variables
2. Separate environments
3. Validate configuration
4. Document options
5. Use sensible defaults

### Security Considerations
1. Protect sensitive data
2. Use secure defaults
3. Validate inputs
4. Audit configurations
5. Regular reviews

Remember:
- Keep it simple
- Document everything
- Validate inputs
- Secure sensitive data
- Regular updates
