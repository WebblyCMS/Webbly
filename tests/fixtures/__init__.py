"""Test fixtures initialization and exports."""

from .assertions import *
from .benchmarks import *
from .cleanup import *
from .compatibility import *
from .config import *
from .data import *
from .decorators import *
from .documentation import *
from .exceptions import *
from .init import *
from .integration import *
from .logging import *
from .markers import *
from .matchers import *
from .performance import *
from .profiling import *
from .reporters import *
from .security import *
from .setup import *
from .statistics import *
from .utils import *
from .validation import *

# Initialize test suite
from .init import suite
suite.initialize()

# Set up test environment
from .setup import setup_test_environment
setup_test_environment()

# Initialize test components
from .logging import logger, output
from .profiling import analyzer
from .statistics import statistics
from .documentation import documentation

# Test data management
from .data import generator as data_generator
from .data import manager as data_manager

# Test utilities
from .utils import (
    wait_for,
    compare_dicts,
    compare_lists,
    normalize_whitespace,
    normalize_html,
    extract_csrf_token,
    parse_response_data,
    get_file_hash,
    temp_file,
    temp_directory,
    create_test_file,
    create_test_image,
    load_json_file,
    save_json_file,
    format_datetime,
    parse_datetime,
    get_relative_url,
    get_query_params,
    generate_random_string,
    generate_random_email,
    generate_random_password
)

# Test assertions
from .assertions import (
    assert_valid_html,
    assert_contains_elements,
    assert_page_title,
    assert_flash_message,
    assert_form_errors,
    assert_valid_pagination,
    assert_valid_post,
    assert_valid_page,
    assert_valid_user,
    assert_valid_theme,
    assert_valid_plugin,
    assert_valid_settings,
    assert_valid_response,
    assert_valid_json_response,
    assert_valid_redirect,
    assert_requires_login,
    assert_requires_admin
)

# Test decorators
from .decorators import (
    requires_login,
    requires_admin,
    track_test,
    mock_datetime,
    mock_mail,
    mock_requests,
    retry_on_failure,
    skip_in_ci,
    only_in_ci,
    requires_database,
    requires_cache,
    requires_email,
    requires_media,
    requires_internet
)

# Security testing
from .security import (
    security_test,
    XSSScanner,
    SQLInjectionScanner,
    CSRFScanner
)

# Performance testing
from .performance import (
    performance_test,
    LoadGenerator,
    PerformanceTest
)

# Integration testing
from .integration import (
    integration_test_environment,
    environment as integration_env,
    db_helper,
    cache_helper,
    email_helper
)

# Browser compatibility testing
from .compatibility import (
    browser_manager,
    platform_manager,
    BROWSER_CONFIGS
)

__all__ = [
    # Test suite
    'suite',
    
    # Test environment
    'setup_test_environment',
    
    # Logging and reporting
    'logger',
    'output',
    'analyzer',
    'statistics',
    'documentation',
    
    # Test data
    'data_generator',
    'data_manager',
    
    # Test utilities
    'wait_for',
    'compare_dicts',
    'compare_lists',
    'normalize_whitespace',
    'normalize_html',
    'extract_csrf_token',
    'parse_response_data',
    'get_file_hash',
    'temp_file',
    'temp_directory',
    'create_test_file',
    'create_test_image',
    'load_json_file',
    'save_json_file',
    'format_datetime',
    'parse_datetime',
    'get_relative_url',
    'get_query_params',
    'generate_random_string',
    'generate_random_email',
    'generate_random_password',
    
    # Test assertions
    'assert_valid_html',
    'assert_contains_elements',
    'assert_page_title',
    'assert_flash_message',
    'assert_form_errors',
    'assert_valid_pagination',
    'assert_valid_post',
    'assert_valid_page',
    'assert_valid_user',
    'assert_valid_theme',
    'assert_valid_plugin',
    'assert_valid_settings',
    'assert_valid_response',
    'assert_valid_json_response',
    'assert_valid_redirect',
    'assert_requires_login',
    'assert_requires_admin',
    
    # Test decorators
    'requires_login',
    'requires_admin',
    'track_test',
    'mock_datetime',
    'mock_mail',
    'mock_requests',
    'retry_on_failure',
    'skip_in_ci',
    'only_in_ci',
    'requires_database',
    'requires_cache',
    'requires_email',
    'requires_media',
    'requires_internet',
    
    # Security testing
    'security_test',
    'XSSScanner',
    'SQLInjectionScanner',
    'CSRFScanner',
    
    # Performance testing
    'performance_test',
    'LoadGenerator',
    'PerformanceTest',
    
    # Integration testing
    'integration_test_environment',
    'integration_env',
    'db_helper',
    'cache_helper',
    'email_helper',
    
    # Browser compatibility testing
    'browser_manager',
    'platform_manager',
    'BROWSER_CONFIGS'
]
