"""Global pytest configuration and fixtures."""

import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test fixtures
from tests.fixtures import (
    suite,
    setup_test_environment,
    logger,
    statistics,
    documentation,
    data_manager,
    cleanup_all
)

def pytest_configure(config):
    """Configure pytest."""
    # Register custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "functional: Functional tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
    config.addinivalue_line("markers", "requires_db: Tests that require database")
    config.addinivalue_line("markers", "requires_cache: Tests that require cache")
    config.addinivalue_line("markers", "requires_mail: Tests that require email")
    config.addinivalue_line("markers", "requires_media: Tests that require media storage")
    
    # Initialize test suite
    suite.initialize()

def pytest_sessionstart(session):
    """Called before test session starts."""
    # Set up test environment
    setup_test_environment()
    
    # Start statistics collection
    statistics.start_session()
    
    # Create test data
    if not session.config.getoption("--no-testdata"):
        data = data_manager.generate_test_data()
        data_manager.save_test_data(data)

def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes."""
    # End statistics collection
    statistics.end_session()
    
    # Generate reports
    if not session.config.getoption("--no-report"):
        statistics.generate_report()
        documentation.generate_markdown()
        documentation.generate_html()
    
    # Clean up test environment
    if not session.config.getoption("--no-cleanup"):
        cleanup_all(session.app)

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--no-testdata",
        action="store_true",
        default=False,
        help="Don't generate test data"
    )
    parser.addoption(
        "--no-report",
        action="store_true",
        default=False,
        help="Don't generate test reports"
    )
    parser.addoption(
        "--no-cleanup",
        action="store_true",
        default=False,
        help="Don't clean up test environment"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use for UI tests"
    )

@pytest.fixture(scope='session')
def app():
    """Create test application."""
    from webbly import create_app
    from tests.fixtures.config import get_test_config
    
    app = create_app(get_test_config())
    return app

@pytest.fixture(scope='session')
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture(scope='session')
def db(app):
    """Set up test database."""
    from webbly.models import db
    
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Create database session."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def logged_in_user(client, session):
    """Create and log in a test user."""
    from webbly.models import User
    from tests.fixtures.data import generator
    
    user_data = generator.generate_user()
    user = User(**user_data)
    session.add(user)
    session.commit()
    
    client.post('/auth/login', data={
        'email': user_data['email'],
        'password': user_data['password']
    })
    
    return user

@pytest.fixture(scope='function')
def logged_in_admin(client, session):
    """Create and log in an admin user."""
    from webbly.models import User
    from tests.fixtures.data import generator
    
    admin_data = generator.generate_user(is_admin=True)
    admin = User(**admin_data)
    session.add(admin)
    session.commit()
    
    client.post('/auth/login', data={
        'email': admin_data['email'],
        'password': admin_data['password']
    })
    
    return admin

@pytest.fixture(scope='function')
def browser(request):
    """Create Selenium WebDriver."""
    from selenium import webdriver
    
    browser_name = request.config.getoption("--browser")
    
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    
    yield driver
    driver.quit()

def pytest_runtest_setup(item):
    """Called before each test."""
    # Log test start
    logger.info(f"Starting test: {item.name}")
    
    # Skip tests based on markers and configuration
    for marker in item.iter_markers():
        if marker.name == 'requires_db' and not item.config.getoption("--db"):
            pytest.skip("Test requires database")
        elif marker.name == 'requires_cache' and not item.config.getoption("--cache"):
            pytest.skip("Test requires cache")
        elif marker.name == 'requires_mail' and not item.config.getoption("--mail"):
            pytest.skip("Test requires email")
        elif marker.name == 'requires_media' and not item.config.getoption("--media"):
            pytest.skip("Test requires media storage")

def pytest_runtest_teardown(item, nextitem):
    """Called after each test."""
    logger.info(f"Finished test: {item.name}")

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary information to test report."""
    if not config.getoption("--no-report"):
        stats = statistics.get_summary()
        
        terminalreporter.write_sep("=", "Test Summary")
        terminalreporter.write_line(f"Total Tests: {stats['total_tests']}")
        terminalreporter.write_line(f"Passed: {stats['passed']}")
        terminalreporter.write_line(f"Failed: {stats['failed']}")
        terminalreporter.write_line(f"Skipped: {stats['skipped']}")
        terminalreporter.write_line(f"Duration: {stats['total_duration']:.2f}s")
