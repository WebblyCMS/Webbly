import re
from flask import current_app
from sqlalchemy import or_
from .models import Post, Page, db
from .cache import cache

class Search:
    """Search functionality for Webbly CMS."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize search with Flask application."""
        self.app = app
        
        # Register CLI commands
        @app.cli.group()
        def search():
            """Search management commands."""
            pass

        @search.command()
        def reindex():
            """Rebuild the search index."""
            self.reindex()
            click.echo("Search index rebuilt successfully!")

    @cache.memoize(timeout=300)
    def search(self, query, limit=None, include_drafts=False):
        """
        Search posts and pages.
        Returns tuple of (posts, pages) that match the query.
        """
        if not query:
            return [], []
        
        # Normalize query
        query = self._normalize_query(query)
        
        # Search posts
        posts_query = Post.query
        if not include_drafts:
            posts_query = posts_query.filter_by(published=True)
        
        posts = posts_query.filter(
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%'),
                Post.excerpt.ilike(f'%{query}%')
            )
        ).order_by(Post.created_at.desc())
        
        if limit:
            posts = posts.limit(limit)
        
        # Search pages
        pages_query = Page.query
        if not include_drafts:
            pages_query = pages_query.filter_by(published=True)
        
        pages = pages_query.filter(
            or_(
                Page.title.ilike(f'%{query}%'),
                Page.content.ilike(f'%{query}%')
            )
        ).order_by(Page.title)
        
        if limit:
            pages = pages.limit(limit)
        
        return posts.all(), pages.all()

    def _normalize_query(self, query):
        """Normalize search query."""
        # Convert to lowercase
        query = query.lower()
        
        # Remove special characters
        query = re.sub(r'[^\w\s-]', '', query)
        
        # Replace multiple spaces with single space
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query

    def get_excerpt(self, content, query, length=200):
        """
        Generate a search result excerpt with highlighted query terms.
        Returns tuple of (excerpt, has_more).
        """
        if not content or not query:
            return '', False
        
        # Strip HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Find first occurrence of query
        query_norm = self._normalize_query(query)
        content_norm = self._normalize_query(content)
        pos = content_norm.find(query_norm)
        
        if pos == -1:
            # Query not found, return start of content
            if len(content) <= length:
                return content, False
            return content[:length] + '...', True
        
        # Calculate excerpt range
        start = max(0, pos - length // 2)
        end = min(len(content), pos + len(query) + length // 2)
        
        # Add ellipsis if needed
        prefix = '...' if start > 0 else ''
        suffix = '...' if end < len(content) else ''
        
        excerpt = prefix + content[start:end] + suffix
        has_more = end < len(content)
        
        return excerpt, has_more

    def highlight_query(self, text, query):
        """Highlight query terms in text."""
        if not text or not query:
            return text
        
        # Escape HTML entities
        text = text.replace('&', '&amp;').replace('<', '<').replace('>', '>')
        
        # Split query into terms
        terms = self._normalize_query(query).split()
        
        # Highlight each term
        highlighted = text
        for term in terms:
            pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
            highlighted = pattern.sub(r'<mark>\1</mark>', highlighted)
        
        return highlighted

    def get_related(self, post, limit=5):
        """Get related posts based on content similarity."""
        if not post:
            return []
        
        # Extract keywords from post title and content
        keywords = self._extract_keywords(post.title + ' ' + post.content)
        
        # Find posts with similar keywords
        related = Post.query.filter(
            Post.id != post.id,
            Post.published == True
        ).filter(
            or_(
                *[Post.title.ilike(f'%{kw}%') for kw in keywords],
                *[Post.content.ilike(f'%{kw}%') for kw in keywords]
            )
        ).distinct()
        
        # Order by relevance (number of keyword matches)
        related = sorted(
            related.all(),
            key=lambda p: sum(
                kw.lower() in p.title.lower() or kw.lower() in p.content.lower()
                for kw in keywords
            ),
            reverse=True
        )
        
        return related[:limit]

    def _extract_keywords(self, text, min_length=4, max_keywords=10):
        """Extract keywords from text."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Convert to lowercase and split into words
        words = text.lower().split()
        
        # Remove common words and short words
        stop_words = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have'])
        words = [w for w in words if len(w) >= min_length and w not in stop_words]
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in keywords[:max_keywords]]

    def reindex(self):
        """Rebuild the search index."""
        # Clear existing cache
        cache.clear()
        
        # Reindex all posts and pages
        posts = Post.query.all()
        pages = Page.query.all()
        
        # Warm up cache with common searches
        common_terms = ['welcome', 'about', 'contact', 'news']
        for term in common_terms:
            self.search(term)
        
        return len(posts) + len(pages)

# Initialize search
search = Search()
