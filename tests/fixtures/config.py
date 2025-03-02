"""Test configuration settings."""

import os
from pathlib import Path
from typing import Dict, Any

# Test environment settings
TEST_ENV = {
    'TESTING': True,
    'DEBUG': False,
    'ENV': 'testing'
}

# Test paths
TEST_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = TEST_ROOT / 'data'
TEST_FIXTURES_DIR = TEST_ROOT / 'fixtures'
TEST_REPORTS_DIR = TEST_ROOT / 'reports'
TEST_TEMP_DIR = TEST_ROOT / 'temp'

# Ensure directories exist
for directory in [TEST_DATA_DIR, TEST_FIXTURES_DIR, TEST_REPORTS_DIR, TEST_TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database settings
TEST_DATABASE = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ECHO': False
}

# Cache settings
TEST_CACHE = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Security settings
TEST_SECURITY = {
    'SECRET_KEY': 'test-secret-key',
    'SECURITY_PASSWORD_SALT': 'test-password-salt',
    'WTF_CSRF_ENABLED': False,
    'LOGIN_DISABLED': False
}

# Mail settings
TEST_MAIL = {
    'MAIL_SERVER': 'localhost',
    'MAIL_PORT': 25,
    'MAIL_USE_TLS': False,
    'MAIL_USERNAME': None,
    'MAIL_PASSWORD': None,
    'MAIL_DEFAULT_SENDER': 'test@example.com'
}

# Upload settings
TEST_UPLOAD = {
    'UPLOAD_FOLDER': str(TEST_TEMP_DIR / 'uploads'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
}

# Theme settings
TEST_THEME = {
    'THEME_FOLDER': str(TEST_TEMP_DIR / 'themes'),
    'DEFAULT_THEME': 'default'
}

# Plugin settings
TEST_PLUGIN = {
    'PLUGIN_FOLDER': str(TEST_TEMP_DIR / 'plugins'),
    'PLUGIN_SETTINGS_FILE': str(TEST_TEMP_DIR / 'plugin_settings.json')
}

# Search settings
TEST_SEARCH = {
    'SEARCH_RESULT_LIMIT': 20,
    'SEARCH_MIN_CHARS': 3
}

# Pagination settings
TEST_PAGINATION = {
    'POSTS_PER_PAGE': 10,
    'ADMIN_POSTS_PER_PAGE': 20,
    'COMMENTS_PER_PAGE': 20
}

# Logging settings
TEST_LOGGING = {
    'LOG_FILE': str(TEST_TEMP_DIR / 'test.log'),
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s [%(levelname)s] %(message)s'
}

# Coverage settings
TEST_COVERAGE = {
    'COVERAGE_REPORT_DIR': str(TEST_REPORTS_DIR / 'coverage'),
    'COVERAGE_XML_FILE': str(TEST_REPORTS_DIR / 'coverage.xml'),
    'COVERAGE_JSON_FILE': str(TEST_REPORTS_DIR / 'coverage.json')
}

# Test report settings
TEST_REPORTS = {
    'HTML_REPORT': str(TEST_REPORTS_DIR / 'report.html'),
    'XML_REPORT': str(TEST_REPORTS_DIR / 'report.xml'),
    'JSON_REPORT': str(TEST_REPORTS_DIR / 'report.json')
}

# Test user credentials
TEST_USERS = {
    'admin': {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'AdminPass123!',
        'is_admin': True
    },
    'user': {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'UserPass123!',
        'is_admin': False
    }
}

# Test content
TEST_CONTENT = {
    'post': {
        'title': 'Test Post',
        'content': 'Test post content',
        'excerpt': 'Test excerpt'
    },
    'page': {
        'title': 'Test Page',
        'content': 'Test page content',
        'template': 'default'
    },
    'comment': {
        'content': 'Test comment'
    }
}

# Test timeouts
TEST_TIMEOUTS = {
    'SETUP': 30,  # seconds
    'TEARDOWN': 30,
    'DATABASE': 10,
    'CACHE': 5,
    'MAIL': 5,
    'UPLOAD': 10
}

# Test retries
TEST_RETRIES = {
    'MAX_ATTEMPTS': 3,
    'DELAY': 1  # seconds
}

def get_test_config() -> Dict[str, Any]:
    """Get complete test configuration."""
    return {
        **TEST_ENV,
        **TEST_DATABASE,
        **TEST_CACHE,
        **TEST_SECURITY,
        **TEST_MAIL,
        **TEST_UPLOAD,
        **TEST_THEME,
        **TEST_PLUGIN,
        **TEST_SEARCH,
        **TEST_PAGINATION
    }

def get_test_paths() -> Dict[str, Path]:
    """Get test directory paths."""
    return {
        'root': TEST_ROOT,
        'data': TEST_DATA_DIR,
        'fixtures': TEST_FIXTURES_DIR,
        'reports': TEST_REPORTS_DIR,
        'temp': TEST_TEMP_DIR
    }

def get_test_user(user_type: str = 'user') -> Dict[str, str]:
    """Get test user credentials."""
    return TEST_USERS.get(user_type, TEST_USERS['user'])

def get_test_content(content_type: str = 'post') -> Dict[str, str]:
    """Get test content."""
    return TEST_CONTENT.get(content_type, TEST_CONTENT['post'])

def get_test_timeout(operation: str = 'SETUP') -> int:
    """Get test timeout value."""
    return TEST_TIMEOUTS.get(operation.upper(), 30)

def get_test_retries() -> Dict[str, int]:
    """Get test retry settings."""
    return TEST_RETRIES
