"""Test parameters and test cases."""

import pytest
from datetime import datetime, timedelta

# User test parameters
USER_TEST_CASES = [
    pytest.param(
        {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!'
        },
        id='valid_user'
    ),
    pytest.param(
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'AdminPass123!',
            'is_admin': True
        },
        id='valid_admin'
    )
]

INVALID_USER_TEST_CASES = [
    pytest.param(
        {
            'username': '',
            'email': 'test@example.com',
            'password': 'Password123!'
        },
        id='empty_username'
    ),
    pytest.param(
        {
            'username': 'testuser',
            'email': 'invalid_email',
            'password': 'Password123!'
        },
        id='invalid_email'
    ),
    pytest.param(
        {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short'
        },
        id='short_password'
    )
]

# Post test parameters
POST_TEST_CASES = [
    pytest.param(
        {
            'title': 'Test Post',
            'content': 'Test content',
            'published': True
        },
        id='valid_post'
    ),
    pytest.param(
        {
            'title': 'Draft Post',
            'content': 'Draft content',
            'published': False
        },
        id='draft_post'
    ),
    pytest.param(
        {
            'title': 'Post with Excerpt',
            'content': 'Test content',
            'excerpt': 'Test excerpt',
            'published': True
        },
        id='post_with_excerpt'
    )
]

INVALID_POST_TEST_CASES = [
    pytest.param(
        {
            'title': '',
            'content': 'Test content'
        },
        id='empty_title'
    ),
    pytest.param(
        {
            'title': 'Test Post',
            'content': ''
        },
        id='empty_content'
    )
]

# Page test parameters
PAGE_TEST_CASES = [
    pytest.param(
        {
            'title': 'Test Page',
            'content': 'Test content',
            'template': 'default',
            'published': True
        },
        id='valid_page'
    ),
    pytest.param(
        {
            'title': 'Custom Template',
            'content': 'Test content',
            'template': 'custom',
            'published': True
        },
        id='custom_template'
    )
]

# Theme test parameters
THEME_TEST_CASES = [
    pytest.param(
        {
            'name': 'Test Theme',
            'directory': 'test_theme',
            'version': '1.0.0',
            'author': 'Test Author'
        },
        id='valid_theme'
    ),
    pytest.param(
        {
            'name': 'Theme with Options',
            'directory': 'theme_options',
            'version': '1.0.0',
            'author': 'Test Author',
            'options': {
                'primary_color': '#007bff',
                'font_family': 'Arial'
            }
        },
        id='theme_with_options'
    )
]

# Plugin test parameters
PLUGIN_TEST_CASES = [
    pytest.param(
        {
            'name': 'Test Plugin',
            'directory': 'test_plugin',
            'version': '1.0.0',
            'author': 'Test Author'
        },
        id='valid_plugin'
    ),
    pytest.param(
        {
            'name': 'Plugin with Settings',
            'directory': 'plugin_settings',
            'version': '1.0.0',
            'author': 'Test Author',
            'settings': {
                'api_key': 'test_key',
                'enabled': True
            }
        },
        id='plugin_with_settings'
    )
]

# Comment test parameters
COMMENT_TEST_CASES = [
    pytest.param(
        {
            'content': 'Test comment',
            'approved': True
        },
        id='approved_comment'
    ),
    pytest.param(
        {
            'content': 'Pending comment',
            'approved': False
        },
        id='pending_comment'
    )
]

# Search test parameters
SEARCH_TEST_CASES = [
    pytest.param('test', ['Test Post', 'Test Page'], id='basic_search'),
    pytest.param('python', ['Python Tutorial', 'Learn Python'], id='keyword_search'),
    pytest.param('', [], id='empty_search'),
    pytest.param('nonexistent', [], id='no_results')
]

# Date test parameters
DATE_TEST_CASES = [
    pytest.param(
        datetime.now(),
        'just now',
        id='current_time'
    ),
    pytest.param(
        datetime.now() - timedelta(minutes=30),
        '30 minutes ago',
        id='minutes_ago'
    ),
    pytest.param(
        datetime.now() - timedelta(hours=2),
        '2 hours ago',
        id='hours_ago'
    ),
    pytest.param(
        datetime.now() - timedelta(days=1),
        'yesterday',
        id='yesterday'
    )
]

# File upload test parameters
UPLOAD_TEST_CASES = [
    pytest.param(
        {
            'filename': 'test.jpg',
            'content_type': 'image/jpeg',
            'size': 1024
        },
        id='valid_image'
    ),
    pytest.param(
        {
            'filename': 'test.pdf',
            'content_type': 'application/pdf',
            'size': 2048
        },
        id='valid_document'
    ),
    pytest.param(
        {
            'filename': 'test.exe',
            'content_type': 'application/x-msdownload',
            'size': 1024
        },
        id='invalid_type'
    ),
    pytest.param(
        {
            'filename': 'test.jpg',
            'content_type': 'image/jpeg',
            'size': 20 * 1024 * 1024  # 20MB
        },
        id='too_large'
    )
]

# API test parameters
API_TEST_CASES = [
    pytest.param('/api/posts', 'GET', 200, id='list_posts'),
    pytest.param('/api/posts', 'POST', 201, id='create_post'),
    pytest.param('/api/posts/1', 'GET', 200, id='get_post'),
    pytest.param('/api/posts/1', 'PUT', 200, id='update_post'),
    pytest.param('/api/posts/1', 'DELETE', 204, id='delete_post'),
    pytest.param('/api/nonexistent', 'GET', 404, id='not_found')
]

# Form validation test parameters
FORM_TEST_CASES = [
    pytest.param(
        {
            'username': 'test',
            'email': 'invalid',
            'password': 'short'
        },
        {
            'email': 'Invalid email address',
            'password': 'Password must be at least 8 characters'
        },
        id='invalid_form'
    ),
    pytest.param(
        {
            'username': '',
            'email': 'test@example.com',
            'password': 'Password123!'
        },
        {
            'username': 'This field is required'
        },
        id='missing_required'
    )
]

# Cache test parameters
CACHE_TEST_CASES = [
    pytest.param('key1', 'value1', 300, id='string_value'),
    pytest.param('key2', {'data': 'value2'}, 600, id='dict_value'),
    pytest.param('key3', [1, 2, 3], 900, id='list_value')
]

# Security test parameters
SECURITY_TEST_CASES = [
    pytest.param('<script>alert("xss")</script>', id='xss_attempt'),
    pytest.param("'; DROP TABLE users; --", id='sql_injection'),
    pytest.param('../../../etc/passwd', id='path_traversal')
]
