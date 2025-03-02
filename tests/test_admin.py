import pytest
from webbly.models import Post, Page, Theme, Plugin, Setting, User, db

def test_admin_access(client, auth):
    """Test admin dashboard access control."""
    # Test unauthenticated access
    response = client.get('/webb-admin/')
    assert response.headers["Location"].startswith("/auth/login")
    
    # Test non-admin access
    auth.login()
    response = client.get('/webb-admin/')
    assert response.status_code == 403
    
    # Test admin access
    auth.login('admin@example.com', 'password')
    response = client.get('/webb-admin/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_post_management(client, logged_in_admin):
    """Test post management."""
    # Test post list
    response = client.get('/webb-admin/posts')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    
    # Test post creation
    response = client.post('/webb-admin/posts/new', data={
        'title': 'New Test Post',
        'content': 'New test content',
        'excerpt': 'Test excerpt',
        'published': True
    })
    assert response.headers["Location"] == "/webb-admin/posts"
    
    # Test post exists
    response = client.get('/webb-admin/posts')
    assert b'New Test Post' in response.data
    
    # Test post edit
    post = Post.query.filter_by(title='New Test Post').first()
    response = client.post(f'/webb-admin/posts/{post.id}/edit', data={
        'title': 'Updated Test Post',
        'content': 'Updated test content',
        'excerpt': 'Updated excerpt',
        'published': True
    })
    assert response.headers["Location"] == "/webb-admin/posts"
    
    # Test post deletion
    response = client.post(f'/webb-admin/posts/{post.id}/delete')
    assert response.headers["Location"] == "/webb-admin/posts"
    assert Post.query.filter_by(id=post.id).first() is None

def test_page_management(client, logged_in_admin):
    """Test page management."""
    # Test page list
    response = client.get('/webb-admin/pages')
    assert response.status_code == 200
    assert b'Test Page' in response.data
    
    # Test page creation
    response = client.post('/webb-admin/pages/new', data={
        'title': 'New Test Page',
        'content': 'New test content',
        'template': 'default',
        'published': True
    })
    assert response.headers["Location"] == "/webb-admin/pages"
    
    # Test page exists
    response = client.get('/webb-admin/pages')
    assert b'New Test Page' in response.data
    
    # Test page edit
    page = Page.query.filter_by(title='New Test Page').first()
    response = client.post(f'/webb-admin/pages/{page.id}/edit', data={
        'title': 'Updated Test Page',
        'content': 'Updated test content',
        'template': 'default',
        'published': True
    })
    assert response.headers["Location"] == "/webb-admin/pages"
    
    # Test page deletion
    response = client.post(f'/webb-admin/pages/{page.id}/delete')
    assert response.headers["Location"] == "/webb-admin/pages"
    assert Page.query.filter_by(id=page.id).first() is None

def test_theme_management(client, logged_in_admin, test_theme):
    """Test theme management."""
    # Test theme list
    response = client.get('/webb-admin/themes')
    assert response.status_code == 200
    assert b'Test Theme' in response.data
    
    # Test theme activation
    response = client.post(f'/webb-admin/themes/{test_theme.id}/activate')
    assert response.headers["Location"] == "/webb-admin/themes"
    assert Theme.query.filter_by(id=test_theme.id).first().active == True
    
    # Test theme customization
    response = client.post(f'/webb-admin/themes/{test_theme.id}/customize', data={
        'primary_color': '#ff0000',
        'font_family': 'Arial'
    })
    assert response.headers["Location"] == "/webb-admin/themes"

def test_plugin_management(client, logged_in_admin, test_plugin):
    """Test plugin management."""
    # Test plugin list
    response = client.get('/webb-admin/plugins')
    assert response.status_code == 200
    assert b'Test Plugin' in response.data
    
    # Test plugin activation
    response = client.post(f'/webb-admin/plugins/{test_plugin.id}/toggle')
    assert response.headers["Location"] == "/webb-admin/plugins"
    
    # Test plugin settings
    response = client.post(f'/webb-admin/plugins/{test_plugin.id}/settings', data={
        'setting1': 'value1',
        'setting2': 'value2'
    })
    assert response.headers["Location"] == "/webb-admin/plugins"

def test_user_management(client, logged_in_admin):
    """Test user management."""
    # Test user list
    response = client.get('/webb-admin/users')
    assert response.status_code == 200
    assert b'testuser' in response.data
    
    # Test user creation
    response = client.post('/webb-admin/users/new', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Password123!',
        'is_admin': False
    })
    assert response.headers["Location"] == "/webb-admin/users"
    
    # Test user edit
    user = User.query.filter_by(username='newuser').first()
    response = client.post(f'/webb-admin/users/{user.id}/edit', data={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'is_admin': True
    })
    assert response.headers["Location"] == "/webb-admin/users"
    
    # Test user deletion
    response = client.post(f'/webb-admin/users/{user.id}/delete')
    assert response.headers["Location"] == "/webb-admin/users"
    assert User.query.filter_by(id=user.id).first() is None

def test_settings_management(client, logged_in_admin):
    """Test settings management."""
    # Test settings page
    response = client.get('/webb-admin/settings')
    assert response.status_code == 200
    
    # Test settings update
    response = client.post('/webb-admin/settings', data={
        'site_title': 'Updated Site Title',
        'site_description': 'Updated description',
        'posts_per_page': '20',
        'enable_comments': 'true'
    })
    assert response.headers["Location"] == "/webb-admin/settings"
    
    # Verify settings were updated
    assert Setting.query.filter_by(key='site_title').first().value == 'Updated Site Title'
    assert Setting.query.filter_by(key='posts_per_page').first().value == '20'

def test_media_management(client, logged_in_admin):
    """Test media management."""
    # Test media library
    response = client.get('/webb-admin/media')
    assert response.status_code == 200
    
    # Test file upload
    with open('tests/fixtures/test-image.jpg', 'rb') as img:
        response = client.post('/webb-admin/media/upload', data={
            'file': (img, 'test-image.jpg')
        })
        assert response.status_code == 200
        assert b'uploaded successfully' in response.data
    
    # Test file deletion
    response = client.post('/webb-admin/media/delete', data={
        'filename': 'test-image.jpg'
    })
    assert response.status_code == 200
    assert b'deleted successfully' in response.data

def test_backup_management(client, logged_in_admin):
    """Test backup functionality."""
    # Test backup creation
    response = client.post('/webb-admin/backup/create')
    assert response.status_code == 200
    assert b'Backup created successfully' in response.data
    
    # Test backup download
    response = client.get('/webb-admin/backup/download/latest')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/x-sqlite3'
    
    # Test backup restore
    with open('tests/fixtures/test-backup.db', 'rb') as backup:
        response = client.post('/webb-admin/backup/restore', data={
            'file': backup
        })
        assert response.status_code == 200
        assert b'Backup restored successfully' in response.data
