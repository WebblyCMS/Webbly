import os
import pytest
import logging
from flask import url_for
from webbly.errors import init_error_handlers, handle_error
from webbly.logging import init_logging, log_error, setup_audit_log, setup_security_log

def test_404_error(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
    assert b'The page you\'re looking for doesn\'t exist' in response.data

def test_403_error(client, auth):
    """Test 403 error handling."""
    # Try to access admin area without permissions
    auth.login()  # Login as non-admin user
    response = client.get('/webb-admin/')
    assert response.status_code == 403
    assert b'Access Denied' in response.data
    assert b'don\'t have permission' in response.data

def test_500_error(app, client):
    """Test 500 error handling."""
    # Create a route that raises an error
    @app.route('/error')
    def error():
        raise Exception('Test error')
    
    response = client.get('/error')
    assert response.status_code == 500
    assert b'Internal Server Error' in response.data
    assert b'Something went wrong' in response.data

def test_maintenance_mode(app, client):
    """Test maintenance mode error handling."""
    with app.app_context():
        # Enable maintenance mode
        app.config['MAINTENANCE_MODE'] = True
        
        response = client.get('/')
        assert response.status_code == 503
        assert b'Under Maintenance' in response.data
        assert b'performing scheduled maintenance' in response.data

def test_error_logging(app, caplog):
    """Test error logging functionality."""
    with app.app_context():
        # Initialize logging
        init_logging(app)
        
        # Create test error
        error = Exception('Test error')
        error_id = log_error(app, error)
        
        # Check log file
        log_file = 'logs/webbly.log'
        assert os.path.exists(log_file)
        
        with open(log_file) as f:
            log_content = f.read()
            assert error_id in log_content
            assert 'Test error' in log_content

def test_audit_logging(app, caplog):
    """Test audit logging functionality."""
    with app.app_context():
        # Set up audit logging
        audit_logger = setup_audit_log(app)
        
        # Log an audit event
        with caplog.at_level(logging.INFO):
            audit_logger.info(
                'Audit event',
                extra={
                    'action': 'user_created',
                    'details': 'New user created',
                    'user': 'admin'
                }
            )
        
        # Check log contains audit event
        assert 'Audit event' in caplog.text
        assert 'user_created' in caplog.text
        assert 'New user created' in caplog.text

def test_security_logging(app, caplog):
    """Test security logging functionality."""
    with app.app_context():
        # Set up security logging
        security_logger = setup_security_log(app)
        
        # Log a security event
        with caplog.at_level(logging.INFO):
            security_logger.info(
                'Security event',
                extra={
                    'event': 'login_failed',
                    'details': 'Invalid password',
                    'user': 'unknown'
                }
            )
        
        # Check log contains security event
        assert 'Security event' in caplog.text
        assert 'login_failed' in caplog.text
        assert 'Invalid password' in caplog.text

def test_error_context_processor(app, client):
    """Test error context processor."""
    with app.app_context():
        # Create a test error
        error = Exception('Test error')
        
        # Get error details from context processor
        with app.test_request_context():
            context = app.jinja_env.globals['get_error_description'](error)
            assert 'unexpected error occurred' in context

def test_error_email_notification(app, caplog):
    """Test error email notifications."""
    with app.app_context():
        # Configure email settings
        app.config.update(
            MAIL_SERVER='smtp.test.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME='test',
            MAIL_PASSWORD='test',
            ADMIN_EMAIL='admin@test.com'
        )
        
        # Initialize logging with email handler
        init_logging(app)
        
        # Create test error
        error = Exception('Test error')
        log_error(app, error)
        
        # Check email handler was called
        assert 'Sending error email to admin@test.com' in caplog.text

def test_custom_error_pages(client):
    """Test custom error pages."""
    # Test 400 Bad Request
    response = client.post('/auth/login', data={'invalid': 'data'})
    assert response.status_code == 400
    assert b'Bad Request' in response.data
    
    # Test 401 Unauthorized
    response = client.get('/protected', headers={'Authorization': 'invalid'})
    assert response.status_code == 401
    assert b'Unauthorized' in response.data
    
    # Test 405 Method Not Allowed
    response = client.post('/static/file.txt')
    assert response.status_code == 405
    assert b'Method Not Allowed' in response.data
    
    # Test 429 Too Many Requests
    for _ in range(101):  # Exceed rate limit
        client.get('/')
    response = client.get('/')
    assert response.status_code == 429
    assert b'Too Many Requests' in response.data

def test_error_handler_registration(app):
    """Test error handler registration."""
    with app.app_context():
        # Register custom error handler
        @app.errorhandler(418)
        def teapot_error(error):
            return "I'm a teapot", 418
        
        # Test custom error handler
        with app.test_client() as client:
            response = client.get('/teapot')
            assert response.status_code == 418
            assert b"I'm a teapot" in response.data
