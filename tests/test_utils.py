import os
import pytest
from datetime import datetime
from webbly.utils.theme import scan_for_themes, install_theme, get_active_theme
from webbly.utils.settings import get_setting, set_setting, init_default_settings
from webbly.utils.media import save_file, delete_file, get_file_url
from webbly.utils.email import send_email
from webbly.utils.decorators import admin_required, login_required, cache_control
from webbly.models import Theme, Setting, db

def test_theme_utils(app):
    """Test theme utility functions."""
    with app.app_context():
        # Test theme scanning
        themes = scan_for_themes()
        assert isinstance(themes, list)
        assert all(isinstance(theme, dict) for theme in themes)
        
        # Test theme installation
        theme_data = {
            'name': 'Test Theme',
            'directory': 'test_theme',
            'version': '1.0.0',
            'author': 'Test Author'
        }
        theme = install_theme(theme_data)
        assert isinstance(theme, Theme)
        assert theme.name == 'Test Theme'
        
        # Test getting active theme
        theme.active = True
        db.session.add(theme)
        db.session.commit()
        
        active_theme = get_active_theme()
        assert active_theme == theme

def test_settings_utils(app):
    """Test settings utility functions."""
    with app.app_context():
        # Test default settings initialization
        init_default_settings()
        assert Setting.query.count() > 0
        
        # Test setting retrieval
        value = get_setting('site_title')
        assert value is not None
        
        # Test setting update
        set_setting('site_title', 'New Title')
        assert get_setting('site_title') == 'New Title'
        
        # Test default value
        assert get_setting('nonexistent', 'default') == 'default'

def test_media_utils(app, tmp_path):
    """Test media utility functions."""
    with app.app_context():
        # Test file saving
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        with open(test_file, 'rb') as f:
            filename = save_file(f, 'test.txt')
            assert filename is not None
            assert os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Test file URL generation
        url = get_file_url(filename)
        assert url.startswith('/static/uploads/')
        
        # Test file deletion
        delete_file(filename)
        assert not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename))

def test_email_utils(app):
    """Test email utility functions."""
    with app.app_context():
        # Test email sending
        result = send_email(
            subject='Test Email',
            recipients=['test@example.com'],
            template='email/test',
            text_body='Test email content',
            html_body='<p>Test email content</p>'
        )
        assert result is True

def test_decorators(app, client):
    """Test custom decorators."""
    with app.app_context():
        # Test login_required decorator
        @app.route('/test-login-required')
        @login_required
        def test_login_required():
            return 'OK'
        
        response = client.get('/test-login-required')
        assert response.headers["Location"].startswith("/auth/login")
        
        # Test admin_required decorator
        @app.route('/test-admin-required')
        @admin_required
        def test_admin_required():
            return 'OK'
        
        response = client.get('/test-admin-required')
        assert response.headers["Location"].startswith("/auth/login")
        
        # Test cache_control decorator
        @app.route('/test-cache-control')
        @cache_control(max_age=3600)
        def test_cache_control():
            return 'OK'
        
        response = client.get('/test-cache-control')
        assert 'Cache-Control' in response.headers
        assert 'max-age=3600' in response.headers['Cache-Control']

def test_theme_validation(app):
    """Test theme validation."""
    with app.app_context():
        # Test invalid theme data
        invalid_data = {
            'name': 'Invalid Theme',
            # Missing required fields
        }
        with pytest.raises(ValueError):
            install_theme(invalid_data)
        
        # Test invalid theme directory
        with pytest.raises(ValueError):
            install_theme({
                'name': 'Invalid Theme',
                'directory': 'nonexistent',
                'version': '1.0.0',
                'author': 'Test Author'
            })

def test_file_validation(app, tmp_path):
    """Test file upload validation."""
    with app.app_context():
        # Test invalid file type
        test_file = tmp_path / "test.exe"
        test_file.write_text("Test content")
        
        with open(test_file, 'rb') as f:
            with pytest.raises(ValueError):
                save_file(f, 'test.exe')
        
        # Test file size limit
        large_file = tmp_path / "large.txt"
        large_file.write_bytes(b'0' * (16 * 1024 * 1024 + 1))  # 16MB + 1 byte
        
        with open(large_file, 'rb') as f:
            with pytest.raises(ValueError):
                save_file(f, 'large.txt')

def test_setting_validation(app):
    """Test setting validation."""
    with app.app_context():
        # Test invalid setting type
        with pytest.raises(ValueError):
            set_setting('posts_per_page', 'invalid')  # Should be int
        
        # Test restricted setting
        with pytest.raises(ValueError):
            set_setting('system_version', '2.0.0')  # Restricted setting

def test_email_validation(app):
    """Test email validation."""
    with app.app_context():
        # Test invalid email address
        with pytest.raises(ValueError):
            send_email(
                subject='Test',
                recipients=['invalid-email'],
                template='email/test',
                text_body='Test'
            )
        
        # Test missing template
        with pytest.raises(ValueError):
            send_email(
                subject='Test',
                recipients=['test@example.com'],
                template='email/nonexistent',
                text_body='Test'
            )
