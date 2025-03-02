import pytest
from datetime import datetime
from bs4 import BeautifulSoup
import json
from webbly.sitemap import Sitemap
from webbly.feeds import FeedGenerator
from webbly.models import Post, Page, User, db

def test_sitemap_initialization(app):
    """Test sitemap initialization."""
    with app.app_context():
        sitemap = Sitemap(app)
        assert sitemap.app is not None

def test_sitemap_generation(app, test_user):
    """Test sitemap XML generation."""
    with app.app_context():
        sitemap = Sitemap(app)
        
        # Create test content
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user,
            published=True
        )
        page = Page(
            title='Test Page',
            content='Test content',
            author=test_user,
            published=True
        )
        db.session.add_all([post, page])
        db.session.commit()
        
        # Generate sitemap
        xml = sitemap.generate_sitemap()
        
        # Parse XML
        soup = BeautifulSoup(xml, 'xml')
        urls = soup.find_all('url')
        
        # Check content
        assert len(urls) >= 3  # Homepage + post + page
        assert any(post.slug in url.loc.text for url in urls)
        assert any(page.slug in url.loc.text for url in urls)
        
        # Check required elements
        for url in urls:
            assert url.loc is not None
            assert url.lastmod is not None
            assert url.changefreq is not None
            assert url.priority is not None

def test_sitemap_index(app):
    """Test sitemap index generation."""
    with app.app_context():
        sitemap = Sitemap(app)
        
        # Generate sitemap index
        xml = sitemap.generate_sitemap_index()
        
        # Parse XML
        soup = BeautifulSoup(xml, 'xml')
        sitemaps = soup.find_all('sitemap')
        
        # Check content
        assert len(sitemaps) > 0
        for sitemap_tag in sitemaps:
            assert sitemap_tag.loc is not None
            assert sitemap_tag.lastmod is not None

def test_post_sitemap(app, test_user):
    """Test post-specific sitemap generation."""
    with app.app_context():
        sitemap = Sitemap(app)
        
        # Create multiple posts
        for i in range(1500):  # More than sitemap size limit
            post = Post(
                title=f'Test Post {i}',
                content=f'Content {i}',
                author=test_user,
                published=True
            )
            db.session.add(post)
        db.session.commit()
        
        # Generate post sitemap
        xml = sitemap.generate_post_sitemap(page=1)
        
        # Parse XML
        soup = BeautifulSoup(xml, 'xml')
        urls = soup.find_all('url')
        
        # Check pagination
        assert len(urls) <= 1000  # Maximum URLs per sitemap

def test_feed_initialization(app):
    """Test feed generator initialization."""
    with app.app_context():
        feed = FeedGenerator(app)
        assert feed.app is not None

def test_atom_feed(app, test_user):
    """Test Atom feed generation."""
    with app.app_context():
        feed = FeedGenerator(app)
        
        # Create test posts
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user,
            published=True
        )
        db.session.add(post)
        db.session.commit()
        
        # Generate Atom feed
        response = feed.generate_atom()
        
        # Parse feed
        soup = BeautifulSoup(response.data, 'xml')
        entries = soup.find_all('entry')
        
        # Check content
        assert len(entries) > 0
        entry = entries[0]
        assert entry.title.text == 'Test Post'
        assert entry.content.text == 'Test content'
        assert entry.author.name.text == test_user.username

def test_rss_feed(app, test_user):
    """Test RSS feed generation."""
    with app.app_context():
        feed = FeedGenerator(app)
        
        # Create test posts
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user,
            published=True
        )
        db.session.add(post)
        db.session.commit()
        
        # Generate RSS feed
        xml = feed.generate_rss()
        
        # Parse feed
        soup = BeautifulSoup(xml, 'xml')
        items = soup.find_all('item')
        
        # Check content
        assert len(items) > 0
        item = items[0]
        assert item.title.text == 'Test Post'
        assert 'Test content' in item.description.text
        assert test_user.email in item.author.text

def test_json_feed(app, test_user):
    """Test JSON feed generation."""
    with app.app_context():
        feed = FeedGenerator(app)
        
        # Create test posts
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user,
            published=True
        )
        db.session.add(post)
        db.session.commit()
        
        # Generate JSON feed
        feed_data = feed.generate_json_feed()
        
        # Check content
        assert feed_data['version'] == 'https://jsonfeed.org/version/1'
        assert len(feed_data['items']) > 0
        item = feed_data['items'][0]
        assert item['title'] == 'Test Post'
        assert item['content_html'] == 'Test content'
        assert item['author']['name'] == test_user.username

def test_category_feeds(app, test_user):
    """Test category-specific feeds."""
    with app.app_context():
        feed = FeedGenerator(app)
        
        # Create test category and post
        category = {'name': 'Test Category', 'slug': 'test-category'}
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user,
            published=True,
            categories=[category]
        )
        db.session.add(post)
        db.session.commit()
        
        # Generate category feed
        response = feed.generate_atom(category=category)
        
        # Parse feed
        soup = BeautifulSoup(response.data, 'xml')
        assert category['name'] in soup.title.text
        assert len(soup.find_all('entry')) > 0

def test_feed_caching(app, test_user):
    """Test feed caching."""
    with app.app_context():
        feed = FeedGenerator(app)
        
        # Generate feed first time
        first_response = feed.generate_atom()
        
        # Create new post
        post = Post(
            title='New Post',
            content='New content',
            author=test_user,
            published=True
        )
        db.session.add(post)
        db.session.commit()
        
        # Generate feed second time (should be cached)
        second_response = feed.generate_atom()
        
        # Responses should be identical due to caching
        assert first_response.data == second_response.data

def test_sitemap_validation(app):
    """Test sitemap validation."""
    with app.app_context():
        sitemap = Sitemap(app)
        
        # Generate sitemap
        xml = sitemap.generate_sitemap()
        
        # Validate against schema
        from lxml import etree
        schema = etree.XMLSchema(file='path/to/sitemap.xsd')
        doc = etree.fromstring(xml.encode())
        assert schema.validate(doc)

def test_feed_validation(app):
    """Test feed validation."""
    with app.app_context():
        feed = FeedGenerator(app)
        
        # Generate feeds
        atom_response = feed.generate_atom()
        rss_xml = feed.generate_rss()
        
        # Validate Atom feed
        from lxml import etree
        atom_schema = etree.XMLSchema(file='path/to/atom.xsd')
        atom_doc = etree.fromstring(atom_response.data)
        assert atom_schema.validate(atom_doc)
        
        # Validate RSS feed
        rss_schema = etree.XMLSchema(file='path/to/rss.xsd')
        rss_doc = etree.fromstring(rss_xml.encode())
        assert rss_schema.validate(rss_doc)
