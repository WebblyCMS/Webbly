"""Test suite initialization and configuration."""

import os
import sys
import pytest
from pathlib import Path
from typing import Dict, Any, Optional

from .config import (
    get_test_config,
    get_test_paths,
    get_test_timeout,
    get_test_retries
)
from .setup import setup_test_environment
from .cleanup import cleanup_all
from .logging import logger, output
from .profiling import analyzer
from .statistics import statistics
from .documentation import documentation

class TestSuite:
    """Test suite manager."""
    
    def __init__(self):
        self.config = get_test_config()
        self.paths = get_test_paths()
        self.timeouts = {
            'setup': get_test_timeout('SETUP'),
            'teardown': get_test_timeout('TEARDOWN')
        }
        self.retries = get_test_retries()
        self.initialized = False
    
    def initialize(self, app=None):
        """Initialize test suite."""
        if self.initialized:
            return
        
        try:
            # Set up test environment
            setup_test_environment()
            
            # Start statistics collection
            statistics.start_session()
            
            # Initialize test application if provided
            if app:
                self._initialize_app(app)
            
            self.initialized = True
            logger.info("Test suite initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize test suite: {e}")
            raise
    
    def _initialize_app(self, app):
        """Initialize test application."""
        # Configure app for testing
        app.config.update(self.config)
        
        # Set up database
        with app.app_context():
            from webbly.models import db
            db.create_all()
        
        # Initialize components
        self._initialize_components(app)
    
    def _initialize_components(self, app):
        """Initialize application components."""
        with app.app_context():
            # Initialize cache
            from webbly.cache import cache
            cache.init_app(app)
            
            # Initialize mail
            from webbly.utils.email import mail
            mail.init_app(app)
            
            # Initialize security
            from webbly.security import security
            security.init_app(app)
            
            # Initialize plugins
            from webbly.plugins import plugin_manager
            plugin_manager.init_app(app)
            
            # Initialize themes
            from webbly.utils.theme import theme_manager
            theme_manager.init_app(app)
            
            # Initialize search
            from webbly.search import search
            search.init_app(app)
            
            # Initialize tasks
            from webbly.tasks import task_manager
            task_manager.init_app(app)
    
    def cleanup(self, app=None):
        """Clean up test suite."""
        try:
            # Clean up resources
            cleanup_all(app)
            
            # End statistics collection
            statistics.end_session()
            
            # Generate reports
            self._generate_reports()
            
            logger.info("Test suite cleanup completed successfully")
        
        except Exception as e:
            logger.error(f"Failed to clean up test suite: {e}")
            raise
    
    def _generate_reports(self):
        """Generate test reports."""
        try:
            # Generate statistics report
            statistics.generate_report()
            
            # Generate performance analysis
            analyzer.generate_report()
            
            # Generate documentation
            documentation.generate_markdown()
            documentation.generate_html()
        
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")
    
    @property
    def app_config(self) -> Dict[str, Any]:
        """Get application test configuration."""
        return self.config
    
    @property
    def test_paths(self) -> Dict[str, Path]:
        """Get test paths."""
        return self.paths

def pytest_configure(config):
    """Configure pytest for the test suite."""
    # Initialize test suite
    suite = TestSuite()
    config.suite = suite
    
    # Register markers
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "requires_db: mark test as requiring database")
    config.addinivalue_line("markers", "requires_cache: mark test as requiring cache")
    config.addinivalue_line("markers", "requires_mail: mark test as requiring mail")

def pytest_sessionstart(session):
    """Called before test session starts."""
    # Initialize test suite
    session.suite.initialize()

def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes."""
    # Clean up test suite
    session.suite.cleanup()

def pytest_runtest_setup(item):
    """Called before each test."""
    logger.set_test(item.name)

def pytest_runtest_teardown(item, nextitem):
    """Called after each test."""
    logger.set_test(None)

def get_test_suite() -> TestSuite:
    """Get the test suite instance."""
    return pytest.config.suite if hasattr(pytest, 'config') else TestSuite()

# Global test suite instance
suite = get_test_suite()
