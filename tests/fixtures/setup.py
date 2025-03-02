"""Test fixtures initialization and setup."""

import os
import sys
import pytest
import logging
from pathlib import Path
from typing import Dict, Any

from .constants import (
    TEMP_DIR, UPLOAD_DIR, MEDIA_DIR, THEME_DIR, PLUGIN_DIR, LOG_DIR, CACHE_DIR
)
from .coverage import setup_coverage
from .reporters import ConsoleReporter, HTMLReporter, JUnitReporter
from .benchmarks import MemoryProfiler

def setup_test_environment():
    """Set up test environment."""
    # Create necessary directories
    for directory in [TEMP_DIR, UPLOAD_DIR, MEDIA_DIR, THEME_DIR, PLUGIN_DIR, LOG_DIR, CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_DIR / 'test.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def setup_test_config() -> Dict[str, Any]:
    """Set up test configuration."""
    return {
        'TESTING': True,
        'DEBUG': False,
        'SERVER_NAME': 'localhost.test',
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'UPLOAD_FOLDER': str(UPLOAD_DIR),
        'MEDIA_FOLDER': str(MEDIA_DIR),
        'THEME_FOLDER': str(THEME_DIR),
        'PLUGIN_FOLDER': str(PLUGIN_DIR),
        'CACHE_TYPE': 'simple',
        'MAIL_SERVER': 'localhost',
        'MAIL_PORT': 25,
        'MAIL_USE_TLS': False,
        'MAIL_USERNAME': None,
        'MAIL_PASSWORD': None,
        'MAIL_DEFAULT_SENDER': 'test@example.com'
    }

def setup_test_database(app):
    """Set up test database."""
    from webbly.models import db
    
    with app.app_context():
        db.create_all()

def setup_test_cache(app):
    """Set up test cache."""
    from webbly.cache import cache
    
    cache.init_app(app)

def setup_test_mail(app):
    """Set up test mail."""
    from webbly.utils.email import mail
    
    mail.init_app(app)

def setup_test_security(app):
    """Set up test security."""
    from webbly.security import security
    
    security.init_app(app)

def setup_test_plugins(app):
    """Set up test plugins."""
    from webbly.plugins import plugin_manager
    
    plugin_manager.init_app(app)

def setup_test_themes(app):
    """Set up test themes."""
    from webbly.utils.theme import theme_manager
    
    theme_manager.init_app(app)

def setup_test_search(app):
    """Set up test search."""
    from webbly.search import search
    
    search.init_app(app)

def setup_test_tasks(app):
    """Set up test tasks."""
    from webbly.tasks import task_manager
    
    task_manager.init_app(app)

def setup_test_coverage():
    """Set up test coverage."""
    return setup_coverage()

def setup_test_reporters():
    """Set up test reporters."""
    return {
        'console': ConsoleReporter(),
        'html': HTMLReporter(),
        'junit': JUnitReporter()
    }

def setup_test_profiler():
    """Set up test profiler."""
    return MemoryProfiler()

@pytest.fixture(scope='session', autouse=True)
def test_env():
    """Set up test environment."""
    setup_test_environment()
    yield
    # Cleanup can be added here if needed

@pytest.fixture(scope='session')
def test_config():
    """Provide test configuration."""
    return setup_test_config()

@pytest.fixture(scope='session')
def test_app(test_config):
    """Provide test application."""
    from webbly import create_app
    
    app = create_app(test_config)
    
    # Set up components
    setup_test_database(app)
    setup_test_cache(app)
    setup_test_mail(app)
    setup_test_security(app)
    setup_test_plugins(app)
    setup_test_themes(app)
    setup_test_search(app)
    setup_test_tasks(app)
    
    return app

@pytest.fixture(scope='session')
def test_db(test_app):
    """Provide test database."""
    from webbly.models import db
    
    with test_app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='session')
def test_client(test_app):
    """Provide test client."""
    return test_app.test_client()

@pytest.fixture(scope='session')
def test_runner(test_app):
    """Provide test CLI runner."""
    return test_app.test_cli_runner()

@pytest.fixture(scope='session')
def coverage():
    """Provide coverage reporter."""
    return setup_test_coverage()

@pytest.fixture(scope='session')
def reporters():
    """Provide test reporters."""
    return setup_test_reporters()

@pytest.fixture(scope='session')
def profiler():
    """Provide memory profiler."""
    return setup_test_profiler()

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register markers
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "requires_db: mark test as requiring database")
    config.addinivalue_line("markers", "requires_cache: mark test as requiring cache")
    config.addinivalue_line("markers", "requires_mail: mark test as requiring mail")
    
    # Set up coverage if enabled
    if config.option.cov:
        config.coverage = setup_test_coverage()
        config.coverage.start()
    
    # Set up reporters
    config._reporters = setup_test_reporters()

def pytest_sessionstart(session):
    """Called before test session starts."""
    setup_test_environment()

def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes."""
    # Clean up temporary files
    import shutil
    for directory in [TEMP_DIR, UPLOAD_DIR, MEDIA_DIR, THEME_DIR, PLUGIN_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
