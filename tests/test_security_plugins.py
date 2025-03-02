import os
import pytest
from datetime import datetime, timedelta
from flask import session
from webbly.security import Security
from webbly.plugins import PluginManager, hook
from webbly.models import User, Plugin, db

def test_security_initialization(app):
    """Test security system initialization."""
    with app.app_context():
        security = Security(app)
        
        # Test default security settings
        assert app.config['MAX_LOGIN_ATTEMPTS'] == 5
        assert app.config['LOGIN_LOCKOUT_TIME'] == 15
        assert app.config['PASSWORD_MIN_LENGTH'] == 8

def test_password_strength(app):
    """Test password strength validation."""
    with app.app_context():
        security = Security(app)
        
        # Test weak passwords
        assert not security.check_password_strength('short')
        assert not security.check_password_strength('nodigits')
        assert not security.check_password_strength('no-upper-123')
        assert not security.check_password_strength('NO-LOWER-123')
        
        # Test strong password
        assert security.check_password_strength('StrongPass123!')

def test_rate_limiting(app, client):
    """Test rate limiting functionality."""
    with app.app_context():
        security = Security(app)
        
        # Test rate limit decorator
        @app.route('/test-rate-limit')
        @security.rate_limit(limit=2, per=60)
        def test_endpoint():
            return 'OK'
        
        # First two requests should succeed
        assert client.get('/test-rate-limit').status_code == 200
        assert client.get('/test-rate-limit').status_code == 200
        
        # Third request should be blocked
        assert client.get('/test-rate-limit').status_code == 429

def test_login_tracking(app):
    """Test login attempt tracking."""
    with app.app_context():
        security = Security(app)
        
        # Track failed attempts
        for _ in range(app.config['MAX_LOGIN_ATTEMPTS']):
            security.track_login_attempt('test@example.com', success=False)
        
        # Account should be locked
        assert security.check_account_lockout('test@example.com')
        
        # Test lockout expiry
        user = User.query.filter_by(email='test@example.com').first()
        user.locked_until = datetime.utcnow() - timedelta(minutes=16)
        db.session.commit()
        
        assert not security.check_account_lockout('test@example.com')

def test_csrf_protection(app, client):
    """Test CSRF protection."""
    with app.app_context():
        security = Security(app)
        
        # Test CSRF token generation
        token = security.generate_csrf_token()
        assert token is not None
        assert len(token) > 0
        
        # Test token validation
        assert security.check_csrf_token(token)
        assert not security.check_csrf_token('invalid-token')
        
        # Test CSRF protection on forms
        @app.route('/test-csrf', methods=['POST'])
        @security.require_csrf
        def test_endpoint():
            return 'OK'
        
        # Request without token should fail
        assert client.post('/test-csrf').status_code == 400
        
        # Request with valid token should succeed
        response = client.post('/test-csrf', data={'csrf_token': token})
        assert response.status_code == 200

def test_plugin_initialization(app):
    """Test plugin system initialization."""
    with app.app_context():
        plugin_manager = PluginManager(app)
        
        # Test plugin directory creation
        plugins_dir = os.path.join(app.root_path, 'plugins')
        assert os.path.exists(plugins_dir)

def test_plugin_installation(app, tmp_path):
    """Test plugin installation."""
    with app.app_context():
        plugin_manager = PluginManager(app)
        
        # Create test plugin
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text("""
        {
            "name": "Test Plugin",
            "version": "1.0.0",
            "author": "Test Author",
            "description": "Test plugin"
        }
        """)
        (plugin_dir / "__init__.py").write_text("""
        def init_app(app):
            pass
        """)
        
        # Install plugin
        plugin_manager.install_plugin(str(plugin_dir))
        
        # Check plugin was installed
        plugin = Plugin.query.filter_by(name='Test Plugin').first()
        assert plugin is not None
        assert plugin.version == '1.0.0'

def test_plugin_hooks(app):
    """Test plugin hook system."""
    with app.app_context():
        plugin_manager = PluginManager(app)
        
        # Define test hook
        @hook('test_hook')
        def test_hook_function(arg):
            return f"Processed {arg}"
        
        # Register hook
        plugin_manager.register_hooks(test_hook_function)
        
        # Execute hook
        results = plugin_manager.execute_hook('test_hook', 'test')
        assert results == ['Processed test']

def test_plugin_activation(app, test_plugin):
    """Test plugin activation/deactivation."""
    with app.app_context():
        plugin_manager = PluginManager(app)
        
        # Activate plugin
        plugin_manager.activate_plugin(test_plugin.directory)
        assert test_plugin.active
        
        # Deactivate plugin
        plugin_manager.deactivate_plugin(test_plugin.directory)
        assert not test_plugin.active

def test_plugin_settings(app, test_plugin):
    """Test plugin settings management."""
    with app.app_context():
        # Set plugin setting
        test_plugin.set_setting('test_key', 'test_value')
        assert test_plugin.get_setting('test_key') == 'test_value'
        
        # Test default value
        assert test_plugin.get_setting('nonexistent', 'default') == 'default'

def test_security_headers(app, client):
    """Test security headers."""
    with app.app_context():
        security = Security(app)
        
        response = client.get('/')
        
        # Check security headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Content-Security-Policy' in response.headers
        assert 'Strict-Transport-Security' in response.headers

def test_filename_sanitization(app):
    """Test filename sanitization."""
    with app.app_context():
        security = Security(app)
        
        # Test various filenames
        assert security.sanitize_filename('../test.txt') == 'test.txt'
        assert security.sanitize_filename('test../../etc/passwd') == 'test.passwd'
        assert security.sanitize_filename('test.php.jpg') == 'test.php.jpg'

def test_redirect_validation(app):
    """Test redirect URL validation."""
    with app.app_context():
        security = Security(app)
        
        # Test valid URLs
        assert security.validate_redirect_url('/dashboard')
        assert security.validate_redirect_url('/admin/posts')
        
        # Test invalid URLs
        assert not security.validate_redirect_url('http://evil.com')
        assert not security.validate_redirect_url('//evil.com')
