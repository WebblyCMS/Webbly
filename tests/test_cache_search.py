import pytest
from datetime import datetime, timedelta
from webbly.cache import Cache
from webbly.search import Search
from webbly.models import Post, Page, User, db

def test_cache_initialization(app):
    """Test cache initialization."""
    with app.app_context():
        cache = Cache(app)
        
        # Test filesystem cache
        app.config['CACHE_TYPE'] = 'filesystem'
        cache.init_app(app)
        assert cache.cache is not None
        
        # Test Redis cache
        app.config['CACHE_TYPE'] = 'redis'
        app.config['REDIS_HOST'] = 'localhost'
        cache.init_app(app)
        assert cache.cache is not None

def test_cache_operations(app):
    """Test basic cache operations."""
    with app.app_context():
        cache = Cache(app)
        
        # Test setting and getting values
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        # Test deletion
        cache.delete('test_key')
        assert cache.get('test_key') is None
        
        # Test clearing cache
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.clear()
        assert cache.get('key1') is None
        assert cache.get('key2') is None

def test_cache_decorator(app):
    """Test cache decorator."""
    with app.app_context():
        cache = Cache(app)
        counter = {'value': 0}
        
        @cache.cached(timeout=60)
        def test_function():
            counter['value'] += 1
            return counter['value']
        
        # First call should execute function
        assert test_function() == 1
        
        # Second call should return cached value
        assert test_function() == 1
        assert counter['value'] == 1

def test_cache_memoize(app):
    """Test memoization decorator."""
    with app.app_context():
        cache = Cache(app)
        
        @cache.memoize(timeout=60)
        def test_function(arg):
            return datetime.utcnow()
        
        # Test that results are cached per argument
        result1 = test_function('arg1')
        result2 = test_function('arg2')
        
        assert test_function('arg1') == result1
        assert test_function('arg2') == result2
        assert result1 != result2

def test_search_initialization(app):
    """Test search initialization."""
    with app.app_context():
        search = Search(app)
        assert search.app is not None

def test_basic_search(app, test_user):
    """Test basic search functionality."""
    with app.app_context():
        search = Search(app)
        
        # Create test posts
        posts = [
            Post(title='Test Post', content='Test content', author=test_user, published=True),
            Post(title='Another Post', content='Different content', author=test_user, published=True),
            Post(title='Draft Post', content='Draft content', author=test_user, published=False)
        ]
        for post in posts:
            db.session.add(post)
        db.session.commit()
        
        # Test search
        results = search.search('test')
        assert len(results[0]) == 1  # One published post with 'test' in title
        assert results[0][0].title == 'Test Post'
        
        # Test search with include_drafts
        results = search.search('draft', include_drafts=True)
        assert len(results[0]) == 1
        assert results[0][0].title == 'Draft Post'

def test_search_pages(app, test_user):
    """Test page search functionality."""
    with app.app_context():
        search = Search(app)
        
        # Create test pages
        pages = [
            Page(title='Test Page', content='Test content', author=test_user, published=True),
            Page(title='Another Page', content='Different content', author=test_user, published=True)
        ]
        for page in pages:
            db.session.add(page)
        db.session.commit()
        
        # Test search
        results = search.search('test')
        assert len(results[1]) == 1  # One page with 'test' in title
        assert results[1][0].title == 'Test Page'

def test_search_excerpts(app):
    """Test search result excerpts."""
    with app.app_context():
        search = Search(app)
        
        content = "This is a long piece of content that contains the search term somewhere in the middle."
        excerpt = search.get_excerpt(content, "search term", length=50)
        
        assert "search term" in excerpt[0]
        assert len(excerpt[0]) <= 50
        assert excerpt[1]  # has_more should be True

def test_search_highlighting(app):
    """Test search result highlighting."""
    with app.app_context():
        search = Search(app)
        
        text = "This text contains the search term in it."
        highlighted = search.highlight_query(text, "search term")
        
        assert '<mark>search term</mark>' in highlighted

def test_related_posts(app, test_user):
    """Test related posts functionality."""
    with app.app_context():
        search = Search(app)
        
        # Create test posts
        posts = [
            Post(title='Python Programming', content='Python tutorial', author=test_user, published=True),
            Post(title='Python Tips', content='More Python content', author=test_user, published=True),
            Post(title='JavaScript Basics', content='JS tutorial', author=test_user, published=True)
        ]
        for post in posts:
            db.session.add(post)
        db.session.commit()
        
        # Get related posts
        related = search.get_related(posts[0], limit=2)
        assert len(related) == 1  # Should find one related Python post
        assert 'Python' in related[0].title

def test_search_reindexing(app):
    """Test search index rebuilding."""
    with app.app_context():
        search = Search(app)
        
        # Test reindexing
        count = search.reindex()
        assert count == Post.query.count() + Page.query.count()

def test_cache_invalidation(app):
    """Test cache invalidation patterns."""
    with app.app_context():
        cache = Cache(app)
        
        # Set multiple cache keys
        cache.set('user:1:profile', 'data')
        cache.set('user:1:posts', 'data')
        cache.set('user:2:profile', 'data')
        
        # Invalidate by pattern
        cache.invalidate('user:1:*')
        
        assert cache.get('user:1:profile') is None
        assert cache.get('user:1:posts') is None
        assert cache.get('user:2:profile') is not None

def test_search_performance(app, test_user):
    """Test search performance with large dataset."""
    with app.app_context():
        search = Search(app)
        
        # Create many test posts
        for i in range(100):
            post = Post(
                title=f'Test Post {i}',
                content=f'Content {i}',
                author=test_user,
                published=True
            )
            db.session.add(post)
        db.session.commit()
        
        # Time search operation
        import time
        start_time = time.time()
        results = search.search('test')
        end_time = time.time()
        
        # Search should complete in reasonable time
        assert end_time - start_time < 1.0  # Less than 1 second
        assert len(results[0]) > 0
