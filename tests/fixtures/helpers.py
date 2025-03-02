"""Test helper functions and utilities."""

import os
import json
import shutil
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta
from flask import url_for
from werkzeug.security import generate_password_hash
from webbly.models import User, Post, Page, Theme, Plugin, Setting, db

def create_user(username='testuser', email='test@example.com', password='password123', is_admin=False):
    """Create a test user."""
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=is_admin
    )
    db.session.add(user)
    db.session.commit()
    return user

def create_post(title='Test Post', content='Test content', author=None, published=True):
    """Create a test post."""
    if author is None:
        author = create_user()
    
    post = Post(
        title=title,
        content=content,
        author=author,
        published=published
    )
    db.session.add(post)
    db.session.commit()
    return post

def create_page(title='Test Page', content='Test content', author=None, published=True):
    """Create a test page."""
    if author is None:
        author = create_user()
    
    page = Page(
        title=title,
        content=content,
        author=author,
        published=published
    )
    db.session.add(page)
    db.session.commit()
    return page

def create_theme(name='Test Theme', directory='test_theme', active=False):
    """Create a test theme."""
    theme = Theme(
        name=name,
        directory=directory,
        version='1.0.0',
        author='Test Author',
        active=active
    )
    db.session.add(theme)
    db.session.commit()
    return theme

def create_plugin(name='Test Plugin', directory='test_plugin', active=False):
    """Create a test plugin."""
    plugin = Plugin(
        name=name,
        directory=directory,
        version='1.0.0',
        author='Test Author',
        active=active
    )
    db.session.add(plugin)
    db.session.commit()
    return plugin

def create_setting(key, value):
    """Create a test setting."""
    setting = Setting(key=key, value=value)
    db.session.add(setting)
    db.session.commit()
    return setting

@contextmanager
def login_user(client, user=None):
    """Context manager for logging in a user."""
    if user is None:
        user = create_user()
    
    with client:
        client.post(url_for('auth.login'), data={
            'email': user.email,
            'password': 'password123'
        })
        yield user
        client.get(url_for('auth.logout'))

@contextmanager
def temp_uploads():
    """Context manager for temporary uploads directory."""
    temp_dir = Path('tests/temp/uploads')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

@contextmanager
def temp_media():
    """Context manager for temporary media directory."""
    temp_dir = Path('tests/temp/media')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

def create_test_image(path, size=(100, 100)):
    """Create a test image file."""
    from PIL import Image
    
    img = Image.new('RGB', size, color='red')
    img.save(path)
    return path

def create_test_file(path, content='Test content'):
    """Create a test file with content."""
    Path(path).write_text(content)
    return path

def assert_redirects(response, location):
    """Assert that response is a redirect to location."""
    assert response.status_code in (301, 302)
    assert response.location == location

def assert_flashes(response, message, category='message'):
    """Assert that message was flashed."""
    with response.session_transaction() as session:
        flashes = session.get('_flashes', [])
        assert (category, message) in flashes

def get_token_from_response(response):
    """Extract CSRF token from response."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')
    return soup.find('input', {'name': 'csrf_token'})['value']

def create_test_data(app):
    """Create a complete set of test data."""
    with app.app_context():
        # Create admin user
        admin = create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_admin=True
        )
        
        # Create regular users
        users = [
            create_user(f'user{i}', f'user{i}@example.com')
            for i in range(3)
        ]
        
        # Create posts
        posts = []
        for user in [admin] + users:
            for i in range(3):
                post = create_post(
                    title=f'Post {i} by {user.username}',
                    content=f'Content of post {i}',
                    author=user
                )
                posts.append(post)
        
        # Create pages
        pages = [
            create_page('About', 'About page content', admin),
            create_page('Contact', 'Contact page content', admin)
        ]
        
        # Create theme
        theme = create_theme(active=True)
        
        # Create plugin
        plugin = create_plugin(active=True)
        
        # Create settings
        settings = {
            'site_title': 'Test Site',
            'site_description': 'A test website',
            'posts_per_page': '10'
        }
        for key, value in settings.items():
            create_setting(key, value)
        
        return {
            'admin': admin,
            'users': users,
            'posts': posts,
            'pages': pages,
            'theme': theme,
            'plugin': plugin
        }

def cleanup_test_data(app):
    """Clean up test data."""
    with app.app_context():
        db.drop_all()
        db.create_all()

def mock_datetime(monkeypatch, dt=None):
    """Mock datetime.now() and datetime.utcnow()."""
    if dt is None:
        dt = datetime(2023, 1, 1, 12, 0, 0)
    
    class MockDateTime:
        @classmethod
        def now(cls):
            return dt
        
        @classmethod
        def utcnow(cls):
            return dt
    
    monkeypatch.setattr('webbly.utils.datetime', MockDateTime)

def compare_dicts(dict1, dict2, exclude_keys=None):
    """Compare two dictionaries, optionally excluding certain keys."""
    if exclude_keys is None:
        exclude_keys = set()
    
    dict1 = {k: v for k, v in dict1.items() if k not in exclude_keys}
    dict2 = {k: v for k, v in dict2.items() if k not in exclude_keys}
    
    return dict1 == dict2
