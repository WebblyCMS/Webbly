from datetime import datetime
from email.utils import formatdate
from flask import url_for, request
from werkzeug.contrib.atom import AtomFeed
from .models import Post
from .utils.settings import get_setting

class FeedGenerator:
    """Feed generator for Webbly CMS."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize feed generator with Flask application."""
        self.app = app

    def generate_atom(self, posts=None, category=None, tag=None):
        """Generate Atom feed."""
        site_title = get_setting('site_title', 'Webbly Site')
        feed_title = site_title
        
        if category:
            feed_title = f"{site_title} - Category: {category.name}"
        elif tag:
            feed_title = f"{site_title} - Tag: {tag.name}"
        
        feed = AtomFeed(
            title=feed_title,
            subtitle=get_setting('site_description'),
            feed_url=request.url,
            url=request.url_root,
            author=get_setting('site_author', site_title)
        )
        
        if posts is None:
            posts = Post.query.filter_by(published=True)\
                .order_by(Post.created_at.desc())\
                .limit(20)\
                .all()
        
        for post in posts:
            feed.add(
                title=post.title,
                content=post.content,
                content_type='html',
                author=post.author.username,
                url=url_for('core.post', slug=post.slug, _external=True),
                updated=post.updated_at,
                published=post.created_at
            )
        
        return feed.get_response()

    def generate_rss(self, posts=None, category=None, tag=None):
        """Generate RSS feed."""
        site_title = get_setting('site_title', 'Webbly Site')
        feed_title = site_title
        
        if category:
            feed_title = f"{site_title} - Category: {category.name}"
        elif tag:
            feed_title = f"{site_title} - Tag: {tag.name}"
        
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
        xml.append('<channel>')
        
        # Feed metadata
        xml.append(f'<title>{feed_title}</title>')
        xml.append(f'<link>{request.url_root}</link>')
        xml.append(f'<description>{get_setting("site_description", "")}</description>')
        xml.append(f'<language>{get_setting("site_language", "en-us")}</language>')
        xml.append(f'<pubDate>{formatdate()}</pubDate>')
        xml.append(f'<lastBuildDate>{formatdate()}</lastBuildDate>')
        xml.append(f'<atom:link href="{request.url}" rel="self" type="application/rss+xml" />')
        
        if posts is None:
            posts = Post.query.filter_by(published=True)\
                .order_by(Post.created_at.desc())\
                .limit(20)\
                .all()
        
        # Add items
        for post in posts:
            xml.append('<item>')
            xml.append(f'<title>{post.title}</title>')
            xml.append(f'<link>{url_for("core.post", slug=post.slug, _external=True)}</link>')
            xml.append(f'<guid>{url_for("core.post", slug=post.slug, _external=True)}</guid>')
            xml.append(f'<pubDate>{formatdate(float(post.created_at.strftime("%s")))}</pubDate>')
            xml.append(f'<author>{post.author.email} ({post.author.username})</author>')
            
            # Add categories if available
            if hasattr(post, 'categories'):
                for category in post.categories:
                    xml.append(f'<category>{category.name}</category>')
            
            # Add description (excerpt or truncated content)
            description = post.excerpt or self._truncate_html(post.content, 300)
            xml.append(f'<description><![CDATA[{description}]]></description>')
            
            # Add full content
            xml.append(f'<content:encoded><![CDATA[{post.content}]]></content:encoded>')
            
            xml.append('</item>')
        
        xml.append('</channel>')
        xml.append('</rss>')
        
        return '\n'.join(xml)

    def generate_json_feed(self, posts=None, category=None, tag=None):
        """Generate JSON Feed."""
        site_title = get_setting('site_title', 'Webbly Site')
        feed = {
            "version": "https://jsonfeed.org/version/1",
            "title": site_title,
            "home_page_url": request.url_root,
            "feed_url": request.url,
            "description": get_setting('site_description'),
            "author": {
                "name": get_setting('site_author', site_title)
            },
            "items": []
        }
        
        if category:
            feed["title"] = f"{site_title} - Category: {category.name}"
        elif tag:
            feed["title"] = f"{site_title} - Tag: {tag.name}"
        
        if posts is None:
            posts = Post.query.filter_by(published=True)\
                .order_by(Post.created_at.desc())\
                .limit(20)\
                .all()
        
        for post in posts:
            item = {
                "id": url_for('core.post', slug=post.slug, _external=True),
                "url": url_for('core.post', slug=post.slug, _external=True),
                "title": post.title,
                "content_html": post.content,
                "date_published": post.created_at.isoformat(),
                "date_modified": post.updated_at.isoformat(),
                "author": {
                    "name": post.author.username
                }
            }
            
            if post.excerpt:
                item["summary"] = post.excerpt
            
            if post.featured_image:
                item["image"] = url_for('static', 
                                      filename=post.featured_image, 
                                      _external=True)
            
            if hasattr(post, 'categories'):
                item["tags"] = [cat.name for cat in post.categories]
            
            feed["items"].append(item)
        
        return feed

    def _truncate_html(self, html, length=300):
        """Truncate HTML content to specified length while preserving tags."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        if len(text) <= length:
            return html
            
        # Find the last space within the length limit
        truncated = text[:length].rsplit(' ', 1)[0]
        
        # Re-add HTML tags
        soup = BeautifulSoup(html, 'html.parser')
        text_nodes = []
        current_length = 0
        
        for element in soup.descendants:
            if isinstance(element, str):
                if current_length + len(element) > len(truncated):
                    remaining = len(truncated) - current_length
                    element.replace_with(element[:remaining] + '...')
                    break
                current_length += len(element)
            
        return str(soup)

# Initialize feed generator
feeds = FeedGenerator()
