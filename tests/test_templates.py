import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from webbly.filters import init_filters
from webbly.context import init_context_processors
from webbly.models import Post, Page, Theme, Setting, db

def test_markdown_filter(app):
    """Test markdown filter."""
    with app.app_context():
        init_filters(app)
        
        # Test basic markdown
        markdown = "**Bold** and *italic*"
        html = app.jinja_env.filters['markdown'](markdown)
        assert '<strong>Bold</strong>' in html
        assert '<em>italic</em>' in html
        
        # Test code blocks
        markdown = "```python\nprint('hello')\n```"
        html = app.jinja_env.filters['markdown'](markdown)
        assert 'class="language-python"' in html
        assert "print('hello')" in html

def test_gravatar_filter(app):
    """Test gravatar filter."""
    with app.app_context():
        init_filters(app)
        
        email = "test@example.com"
        hash = app.jinja_env.filters['gravatar'](email)
        assert len(hash) == 32  # MD5 hash length
        assert hash == "55502f40dc8b7c769880b10874abc9d0"

def test_timeago_filter(app):
    """Test timeago filter."""
    with app.app_context():
        init_filters(app)
        
        now = datetime.utcnow()
        
        # Test various time differences
        assert 'just now' in app.jinja_env.filters['timeago'](now)
        assert 'minute ago' in app.jinja_env.filters['timeago'](now - timedelta(minutes=1))
        assert 'hour ago' in app.jinja_env.filters['timeago'](now - timedelta(hours=1))
        assert 'day ago' in app.jinja_env.filters['timeago'](now - timedelta(days=1))

def test_truncate_html_filter(app):
    """Test HTML truncation filter."""
    with app.app_context():
        init_filters(app)
        
        html = "<p>This is a <strong>long</strong> paragraph that needs truncating.</p>"
        truncated = app.jinja_env.filters['truncate_html'](html, length=20)
        
        # Check length and tags
        assert len(BeautifulSoup(truncated, 'html.parser').get_text()) <= 20
        assert '...' in truncated
        assert '<p>' in truncated and '</p>' in truncated

def test_strip_html_filter(app):
    """Test HTML stripping filter."""
    with app.app_context():
        init_filters(app)
        
        html = "<p>Text with <strong>HTML</strong> tags</p>"
        text = app.jinja_env.filters['strip_html'](html)
        assert text == "Text with HTML tags"

def test_sanitize_filter(app):
    """Test HTML sanitization filter."""
    with app.app_context():
        init_filters(app)
        
        # Test allowed tags
        html = '<p>Safe <strong>HTML</strong></p>'
        assert app.jinja_env.filters['sanitize'](html) == html
        
        # Test disallowed tags
        html = '<script>alert("xss")</script>'
        assert 'script' not in app.jinja_env.filters['sanitize'](html)

def test_utility_context_processor(app, client):
    """Test utility context processor."""
    with app.app_context():
        init_context_processors(app)
        
        @app.route('/test-context')
        def test_context():
            return """
            {{ get_recent_posts()|length }}
            {{ get_pages()|length }}
            {{ format_datetime(now) }}
            """
        
        response = client.get('/test-context')
        assert response.status_code == 200
        assert str(Post.query.count()) in response.data.decode()

def test_theme_context_processor(app, client, test_theme):
    """Test theme context processor."""
    with app.app_context():
        init_context_processors(app)
        db.session.add(test_theme)
        db.session.commit()
        
        @app.route('/test-theme-context')
        def test_theme_context():
            return """
            {{ active_theme.name }}
            {{ theme_option('primary_color', '#000000') }}
            """
        
        response = client.get('/test-theme-context')
        assert response.status_code == 200
        assert test_theme.name in response.data.decode()

def test_settings_context_processor(app, client):
    """Test settings context processor."""
    with app.app_context():
        init_context_processors(app)
        
        # Add test settings
        Setting.set('site_title', 'Test Site')
        Setting.set('site_description', 'Test Description')
        
        @app.route('/test-settings-context')
        def test_settings_context():
            return """
            {{ site_name }}
            {{ site_description }}
            {{ get_setting('nonexistent', 'default') }}
            """
        
        response = client.get('/test-settings-context')
        assert response.status_code == 200
        assert 'Test Site' in response.data.decode()
        assert 'Test Description' in response.data.decode()
        assert 'default' in response.data.decode()

def test_wordcount_filter(app):
    """Test word count filter."""
    with app.app_context():
        init_filters(app)
        
        text = "This is a test sentence with seven words."
        count = app.jinja_env.filters['wordcount'](text)
        assert count == 1  # Returns reading time in minutes

def test_filesize_filter(app):
    """Test filesize filter."""
    with app.app_context():
        init_filters(app)
        
        assert app.jinja_env.filters['filesize'](1024) == "1.0 KB"
        assert app.jinja_env.filters['filesize'](1024 * 1024) == "1.0 MB"
        assert app.jinja_env.filters['filesize'](1024 * 1024 * 1024) == "1.0 GB"

def test_active_link_filter(app, client):
    """Test active link filter."""
    with app.app_context():
        init_filters(app)
        
        @app.route('/test-active')
        def test_active():
            return "{{ '/test-active'|active_link }}"
        
        response = client.get('/test-active')
        assert response.status_code == 200
        assert 'active' in response.data.decode()

def test_theme_asset_filter(app, client, test_theme):
    """Test theme asset filter."""
    with app.app_context():
        init_filters(app)
        db.session.add(test_theme)
        test_theme.active = True
        db.session.commit()
        
        @app.route('/test-theme-asset')
        def test_theme_asset():
            return "{{ 'style.css'|theme_asset }}"
        
        response = client.get('/test-theme-asset')
        assert response.status_code == 200
        assert f'themes/{test_theme.directory}' in response.data.decode()

def test_meta_context_processor(app, client):
    """Test meta context processor."""
    with app.app_context():
        init_context_processors(app)
        Setting.set('site_title', 'Test Site')
        
        @app.route('/test-meta')
        def test_meta():
            return """
            {{ meta_title('Page Title') }}
            {{ meta_description('Page description') }}
            """
        
        response = client.get('/test-meta')
        assert response.status_code == 200
        assert 'Page Title - Test Site' in response.data.decode()
        assert 'Page description' in response.data.decode()
