import pytest
from webbly.models import Post, Page, Comment, db

def test_index(client, app):
    """Test index page."""
    response = client.get('/')
    assert response.status_code == 200
    
    # Check if test posts are displayed
    assert b'Test Post 0' in response.data
    assert b'Test Post 1' in response.data
    assert b'Test Post 2' in response.data
    
    # Test pagination
    with app.app_context():
        # Create more posts
        user = db.session.query(Post.author_id).first()[0]
        for i in range(15):
            post = Post(
                title=f'Pagination Test Post {i}',
                content=f'Content for pagination test post {i}',
                author_id=user,
                published=True
            )
            db.session.add(post)
        db.session.commit()
    
    # Test first page
    response = client.get('/?page=1')
    assert response.status_code == 200
    assert b'Pagination Test Post 14' in response.data
    
    # Test second page
    response = client.get('/?page=2')
    assert response.status_code == 200
    assert b'Pagination Test Post 4' in response.data

def test_post_view(client, test_post):
    """Test single post view."""
    with client.application.app_context():
        db.session.add(test_post)
        db.session.commit()
        
        response = client.get(f'/post/{test_post.slug}')
        assert response.status_code == 200
        assert test_post.title.encode() in response.data
        assert test_post.content.encode() in response.data

def test_page_view(client, test_page):
    """Test single page view."""
    with client.application.app_context():
        db.session.add(test_page)
        db.session.commit()
        
        response = client.get(f'/page/{test_page.slug}')
        assert response.status_code == 200
        assert test_page.title.encode() in response.data
        assert test_page.content.encode() in response.data

def test_search(client, app):
    """Test search functionality."""
    # Test empty search
    response = client.get('/search')
    assert response.status_code == 200
    assert b'Please enter a search term' in response.data
    
    # Test search with results
    response = client.get('/search?q=test')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    
    # Test search with no results
    response = client.get('/search?q=nonexistent')
    assert response.status_code == 200
    assert b'No results found' in response.data

def test_comments(client, test_post, logged_in_user):
    """Test comment functionality."""
    with client.application.app_context():
        db.session.add(test_post)
        db.session.commit()
        
        # Test adding comment
        response = client.post(
            f'/post/{test_post.slug}/comment',
            data={'content': 'Test comment'}
        )
        assert response.headers["Location"] == f"/post/{test_post.slug}"
        
        # Test comment appears on post page
        response = client.get(f'/post/{test_post.slug}')
        assert b'Test comment' in response.data
        
        # Test comment moderation
        comment = Comment.query.first()
        assert not comment.approved  # Comments should be unapproved by default

def test_feeds(client):
    """Test feed generation."""
    # Test RSS feed
    response = client.get('/feed.rss')
    assert response.status_code == 200
    assert b'<?xml' in response.data
    assert b'Test Post' in response.data
    
    # Test Atom feed
    response = client.get('/feed.atom')
    assert response.status_code == 200
    assert b'<?xml' in response.data
    assert b'Test Post' in response.data
    
    # Test JSON feed
    response = client.get('/feed.json')
    assert response.status_code == 200
    assert b'Test Post' in response.data

def test_sitemap(client):
    """Test sitemap generation."""
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert b'<?xml' in response.data
    assert b'urlset' in response.data
    assert b'loc' in response.data

def test_theme_assets(client, test_theme):
    """Test theme asset serving."""
    with client.application.app_context():
        db.session.add(test_theme)
        db.session.commit()
        
        # Test theme CSS
        response = client.get('/static/themes/test_theme/style.css')
        assert response.status_code == 200
        
        # Test theme JavaScript
        response = client.get('/static/themes/test_theme/script.js')
        assert response.status_code == 200

def test_media_uploads(client, logged_in_admin):
    """Test media upload functionality."""
    # Test image upload
    data = {
        'file': (open('tests/fixtures/test-image.jpg', 'rb'), 'test-image.jpg')
    }
    response = client.post('/webb-admin/media/upload', data=data)
    assert response.status_code == 200
    assert b'uploaded successfully' in response.data
    
    # Test invalid file type
    data = {
        'file': (open('tests/fixtures/test.txt', 'rb'), 'test.txt')
    }
    response = client.post('/webb-admin/media/upload', data=data)
    assert response.status_code == 400
    assert b'File type not allowed' in response.data

def test_maintenance_mode(client, app):
    """Test maintenance mode."""
    with app.app_context():
        # Enable maintenance mode
        app.config['MAINTENANCE_MODE'] = True
        
        # Test all routes return maintenance page
        routes = ['/', '/post/test', '/page/test']
        for route in routes:
            response = client.get(route)
            assert response.status_code == 503
            assert b'Under Maintenance' in response.data
        
        # Admin should still have access
        client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'password'
        })
        response = client.get('/webb-admin/')
        assert response.status_code == 200
