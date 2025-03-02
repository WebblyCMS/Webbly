"""Test constants and configuration values."""

import os
from pathlib import Path

# Test directories
TEST_DIR = Path(__file__).parent.parent
FIXTURE_DIR = TEST_DIR / 'fixtures'
TEMP_DIR = TEST_DIR / 'temp'
UPLOAD_DIR = TEMP_DIR / 'uploads'
MEDIA_DIR = TEMP_DIR / 'media'
THEME_DIR = TEMP_DIR / 'themes'
PLUGIN_DIR = TEMP_DIR / 'plugins'
LOG_DIR = TEMP_DIR / 'logs'
CACHE_DIR = TEMP_DIR / 'cache'

# Ensure directories exist
for directory in [TEMP_DIR, UPLOAD_DIR, MEDIA_DIR, THEME_DIR, PLUGIN_DIR, LOG_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Test files
TEST_IMAGE = FIXTURE_DIR / 'files/test-image.jpg'
TEST_DOC = FIXTURE_DIR / 'files/test-doc.pdf'
TEST_THEME_PACKAGE = FIXTURE_DIR / 'files/test-theme.zip'
TEST_PLUGIN_PACKAGE = FIXTURE_DIR / 'files/test-plugin.zip'

# Test user credentials
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'Password123!'
}

TEST_ADMIN = {
    'username': 'admin',
    'email': 'admin@example.com',
    'password': 'AdminPass123!'
}

# Test content
TEST_POST = {
    'title': 'Test Post',
    'content': 'This is a test post content.',
    'excerpt': 'Test post excerpt',
    'published': True
}

TEST_PAGE = {
    'title': 'Test Page',
    'content': 'This is a test page content.',
    'template': 'default',
    'published': True
}

# Test theme
TEST_THEME = {
    'name': 'Test Theme',
    'directory': 'test_theme',
    'version': '1.0.0',
    'author': 'Test Author',
    'description': 'A test theme',
    'options': {
        'primary_color': '#007bff',
        'font_family': 'Arial, sans-serif'
    }
}

# Test plugin
TEST_PLUGIN = {
    'name': 'Test Plugin',
    'directory': 'test_plugin',
    'version': '1.0.0',
    'author': 'Test Author',
    'description': 'A test plugin',
    'settings': {
        'api_key': 'test_key',
        'enabled': True
    }
}

# Test settings
TEST_SETTINGS = {
    'site_title': 'Test Site',
    'site_description': 'A test website',
    'posts_per_page': '10',
    'enable_comments': 'true',
    'comment_moderation': 'true'
}

# Test email settings
TEST_EMAIL = {
    'MAIL_SERVER': 'localhost',
    'MAIL_PORT': 25,
    'MAIL_USE_TLS': False,
    'MAIL_USERNAME': None,
    'MAIL_PASSWORD': None,
    'MAIL_DEFAULT_SENDER': 'test@example.com'
}

# Test database settings
TEST_DATABASE = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}

# Test security settings
TEST_SECURITY = {
    'SECRET_KEY': 'test-secret-key',
    'PASSWORD_SALT': 'test-salt',
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOGIN_LOCKOUT_TIME': 15,  # minutes
    'PASSWORD_MIN_LENGTH': 8,
    'REQUIRE_PASSWORD_COMPLEXITY': True
}

# Test upload settings
TEST_UPLOAD = {
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
}

# Test cache settings
TEST_CACHE = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Test search settings
TEST_SEARCH = {
    'SEARCH_RESULT_LIMIT': 20,
    'SEARCH_MIN_CHARS': 3
}

# Test pagination settings
TEST_PAGINATION = {
    'POSTS_PER_PAGE': 10,
    'ADMIN_POSTS_PER_PAGE': 20,
    'COMMENTS_PER_PAGE': 20
}

# Test API settings
TEST_API = {
    'API_VERSION': '1.0',
    'API_PREFIX': '/api/v1',
    'API_DEFAULT_FORMAT': 'json',
    'API_KEY_HEADER': 'X-API-Key'
}

# Test error messages
TEST_ERRORS = {
    'AUTH': {
        'INVALID_CREDENTIALS': 'Invalid email or password.',
        'ACCOUNT_LOCKED': 'Account is locked. Please try again later.',
        'EMAIL_EXISTS': 'Email already registered.',
        'WEAK_PASSWORD': 'Password does not meet requirements.'
    },
    'FORMS': {
        'REQUIRED': 'This field is required.',
        'INVALID_EMAIL': 'Please enter a valid email address.',
        'MIN_LENGTH': 'Must be at least {min} characters.',
        'MAX_LENGTH': 'Must be no more than {max} characters.'
    }
}

# Test success messages
TEST_MESSAGES = {
    'AUTH': {
        'LOGIN_SUCCESS': 'Logged in successfully.',
        'LOGOUT_SUCCESS': 'Logged out successfully.',
        'REGISTER_SUCCESS': 'Registration successful.',
        'PASSWORD_RESET': 'Password reset successful.'
    },
    'CONTENT': {
        'POST_CREATED': 'Post created successfully.',
        'PAGE_CREATED': 'Page created successfully.',
        'COMMENT_ADDED': 'Comment added successfully.'
    }
}

# Test routes
TEST_ROUTES = {
    'AUTH': {
        'login': '/auth/login',
        'logout': '/auth/logout',
        'register': '/auth/register',
        'reset_password': '/auth/reset_password'
    },
    'ADMIN': {
        'dashboard': '/webb-admin/',
        'posts': '/webb-admin/posts',
        'pages': '/webb-admin/pages',
        'users': '/webb-admin/users',
        'settings': '/webb-admin/settings'
    }
}
