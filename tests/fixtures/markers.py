"""Custom pytest markers and their documentation."""

import pytest

def pytest_configure(config):
    """Configure custom pytest markers."""
    
    # Test type markers
    config.addinivalue_line(
        "markers",
        "unit: Unit tests that test individual components in isolation"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that test component interactions"
    )
    config.addinivalue_line(
        "markers",
        "functional: Functional tests that test complete features"
    )
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests that test the complete system"
    )
    
    # Feature markers
    config.addinivalue_line(
        "markers",
        "auth: Authentication and authorization tests"
    )
    config.addinivalue_line(
        "markers",
        "admin: Admin interface tests"
    )
    config.addinivalue_line(
        "markers",
        "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers",
        "db: Database operation tests"
    )
    config.addinivalue_line(
        "markers",
        "cache: Cache functionality tests"
    )
    config.addinivalue_line(
        "markers",
        "search: Search functionality tests"
    )
    config.addinivalue_line(
        "markers",
        "themes: Theme system tests"
    )
    config.addinivalue_line(
        "markers",
        "plugins: Plugin system tests"
    )
    
    # Component markers
    config.addinivalue_line(
        "markers",
        "models: Database model tests"
    )
    config.addinivalue_line(
        "markers",
        "views: View function tests"
    )
    config.addinivalue_line(
        "markers",
        "forms: Form handling tests"
    )
    config.addinivalue_line(
        "markers",
        "utils: Utility function tests"
    )
    config.addinivalue_line(
        "markers",
        "tasks: Background task tests"
    )
    
    # Performance markers
    config.addinivalue_line(
        "markers",
        "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers",
        "benchmark: Performance benchmark tests"
    )
    
    # Security markers
    config.addinivalue_line(
        "markers",
        "security: Security-related tests"
    )
    config.addinivalue_line(
        "markers",
        "csrf: CSRF protection tests"
    )
    config.addinivalue_line(
        "markers",
        "xss: XSS vulnerability tests"
    )
    config.addinivalue_line(
        "markers",
        "sql_injection: SQL injection tests"
    )
    
    # Resource markers
    config.addinivalue_line(
        "markers",
        "requires_db: Tests that require a database"
    )
    config.addinivalue_line(
        "markers",
        "requires_cache: Tests that require a cache"
    )
    config.addinivalue_line(
        "markers",
        "requires_email: Tests that require email functionality"
    )
    config.addinivalue_line(
        "markers",
        "requires_media: Tests that require media storage"
    )
    
    # Environment markers
    config.addinivalue_line(
        "markers",
        "dev: Tests for development environment"
    )
    config.addinivalue_line(
        "markers",
        "prod: Tests for production environment"
    )
    config.addinivalue_line(
        "markers",
        "requires_internet: Tests that require internet connection"
    )

# Unit test marker
unit = pytest.mark.unit

# Integration test marker
integration = pytest.mark.integration

# Functional test marker
functional = pytest.mark.functional

# End-to-end test marker
e2e = pytest.mark.e2e

# Feature test markers
auth = pytest.mark.auth
admin = pytest.mark.admin
api = pytest.mark.api
db = pytest.mark.db
cache = pytest.mark.cache
search = pytest.mark.search
themes = pytest.mark.themes
plugins = pytest.mark.plugins

# Component test markers
models = pytest.mark.models
views = pytest.mark.views
forms = pytest.mark.forms
utils = pytest.mark.utils
tasks = pytest.mark.tasks

# Performance test markers
slow = pytest.mark.slow
benchmark = pytest.mark.benchmark

# Security test markers
security = pytest.mark.security
csrf = pytest.mark.csrf
xss = pytest.mark.xss
sql_injection = pytest.mark.sql_injection

# Resource requirement markers
requires_db = pytest.mark.requires_db
requires_cache = pytest.mark.requires_cache
requires_email = pytest.mark.requires_email
requires_media = pytest.mark.requires_media

# Environment markers
dev = pytest.mark.dev
prod = pytest.mark.prod
requires_internet = pytest.mark.requires_internet

def skip_if_no_db(reason="Test requires database"):
    """Skip test if database is not available."""
    return pytest.mark.skipif(
        not pytest.config.getoption("--db"),
        reason=reason
    )

def skip_if_no_cache(reason="Test requires cache"):
    """Skip test if cache is not available."""
    return pytest.mark.skipif(
        not pytest.config.getoption("--cache"),
        reason=reason
    )

def skip_if_no_email(reason="Test requires email"):
    """Skip test if email is not available."""
    return pytest.mark.skipif(
        not pytest.config.getoption("--email"),
        reason=reason
    )

def skip_if_no_media(reason="Test requires media storage"):
    """Skip test if media storage is not available."""
    return pytest.mark.skipif(
        not pytest.config.getoption("--media"),
        reason=reason
    )

def skip_if_no_internet(reason="Test requires internet connection"):
    """Skip test if internet is not available."""
    return pytest.mark.skipif(
        not pytest.config.getoption("--internet"),
        reason=reason
    )
