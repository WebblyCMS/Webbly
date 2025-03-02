import pytest
from datetime import datetime, timedelta
from webbly.models import User, Post, Page, Theme, Plugin, Setting, Comment, db
from werkzeug.security import check_password_hash

def test_user_model(app):
    """Test User model."""
    with app.app_context():
        # Test user creation
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Test password hashing
        assert user.password_hash is not None
        assert not check_password_hash(user.password_hash, 'wrong_password')
        assert check_password_hash(user.password_hash, 'password123')
        
        # Test password reset token
        token = user.get_reset_password_token()
        assert User.verify_reset_password_token(token) == user
        assert User.verify_reset_password_token('invalid-token') is None
        
        # Test user permissions
        assert not user.is_admin
        user.is_admin = True
        assert user.is_admin
        assert user.has_permission('admin')

def test_post_model(app, test_user):
    """Test Post model."""
    with app.app_context():
        # Test post creation
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user
        )
        db.session.add(post)
        db.session.commit()
        
        # Test slug generation
        assert post.slug == 'test-post'
        
        # Test duplicate slug handling
        post2 = Post(
            title='Test Post',
            content='Another test content',
            author=test_user
        )
        db.session.add(post2)
        db.session.commit()
        assert post2.slug == 'test-post-1'
        
        # Test post status
        assert not post.published
        post.published = True
        assert post.published
        
        # Test timestamps
        assert isinstance(post.created_at, datetime)
        assert isinstance(post.updated_at, datetime)
        
        # Test relationships
        assert post.author == test_user
        assert post in test_user.posts

def test_page_model(app, test_user):
    """Test Page model."""
    with app.app_context():
        # Test page creation
        page = Page(
            title='Test Page',
            content='Test content',
            author=test_user
        )
        db.session.add(page)
        db.session.commit()
        
        # Test slug generation
        assert page.slug == 'test-page'
        
        # Test template handling
        assert page.template == 'default'  # Default template
        page.template = 'custom'
        assert page.template == 'custom'
        
        # Test page status
        assert not page.published
        page.published = True
        assert page.published

def test_theme_model(app):
    """Test Theme model."""
    with app.app_context():
        # Test theme creation
        theme = Theme(
            name='Test Theme',
            directory='test_theme',
            version='1.0.0',
            author='Test Author'
        )
        db.session.add(theme)
        db.session.commit()
        
        # Test theme activation
        assert not theme.active
        theme.active = True
        db.session.commit()
        assert theme.active
        
        # Test theme options
        theme.set_option('primary_color', '#ff0000')
        assert theme.get_option('primary_color') == '#ff0000'
        assert theme.get_option('nonexistent', 'default') == 'default'

def test_plugin_model(app):
    """Test Plugin model."""
    with app.app_context():
        # Test plugin creation
        plugin = Plugin(
            name='Test Plugin',
            directory='test_plugin',
            version='1.0.0',
            author='Test Author'
        )
        db.session.add(plugin)
        db.session.commit()
        
        # Test plugin activation
        assert not plugin.active
        plugin.active = True
        db.session.commit()
        assert plugin.active
        
        # Test plugin settings
        plugin.set_setting('api_key', 'test123')
        assert plugin.get_setting('api_key') == 'test123'
        assert plugin.get_setting('nonexistent', 'default') == 'default'

def test_setting_model(app):
    """Test Setting model."""
    with app.app_context():
        # Test setting creation
        setting = Setting(key='test_key', value='test_value')
        db.session.add(setting)
        db.session.commit()
        
        # Test setting retrieval
        assert Setting.get('test_key') == 'test_value'
        assert Setting.get('nonexistent', 'default') == 'default'
        
        # Test setting update
        Setting.set('test_key', 'new_value')
        assert Setting.get('test_key') == 'new_value'

def test_comment_model(app, test_user, test_post):
    """Test Comment model."""
    with app.app_context():
        # Test comment creation
        comment = Comment(
            content='Test comment',
            author=test_user,
            post=test_post
        )
        db.session.add(comment)
        db.session.commit()
        
        # Test comment approval
        assert not comment.approved
        comment.approved = True
        assert comment.approved
        
        # Test relationships
        assert comment.author == test_user
        assert comment.post == test_post
        assert comment in test_post.comments
        assert comment in test_user.comments

def test_model_relationships(app, test_user):
    """Test relationships between models."""
    with app.app_context():
        # Create test data
        post = Post(title='Test Post', content='Content', author=test_user)
        page = Page(title='Test Page', content='Content', author=test_user)
        comment = Comment(content='Test comment', author=test_user, post=post)
        
        db.session.add_all([post, page, comment])
        db.session.commit()
        
        # Test user relationships
        assert post in test_user.posts
        assert page in test_user.pages
        assert comment in test_user.comments
        
        # Test post relationships
        assert post.author == test_user
        assert comment in post.comments
        
        # Test cascading deletes
        db.session.delete(test_user)
        db.session.commit()
        
        assert Post.query.get(post.id) is None
        assert Page.query.get(page.id) is None
        assert Comment.query.get(comment.id) is None

def test_model_validation(app):
    """Test model validation."""
    with app.app_context():
        # Test required fields
        user = User()
        with pytest.raises(Exception):
            db.session.add(user)
            db.session.commit()
        db.session.rollback()
        
        # Test unique constraints
        user1 = User(username='test', email='test@example.com')
        user2 = User(username='test', email='test@example.com')
        db.session.add(user1)
        db.session.commit()
        
        with pytest.raises(Exception):
            db.session.add(user2)
            db.session.commit()
        db.session.rollback()
        
        # Test field length limits
        with pytest.raises(Exception):
            user = User(username='a' * 100, email='test@example.com')
            db.session.add(user)
            db.session.commit()
