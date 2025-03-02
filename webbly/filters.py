import hashlib
import markdown2
import bleach
import timeago
from datetime import datetime
from jinja2 import Markup
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def init_filters(app):
    """Initialize custom template filters."""
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown to HTML with code highlighting."""
        html = markdown2.markdown(text, extras=[
            'fenced-code-blocks',
            'tables',
            'break-on-newline',
            'header-ids',
            'footnotes',
            'metadata',
            'strike',
            'task_list'
        ])
        return Markup(html)

    @app.template_filter('gravatar')
    def gravatar_filter(email, size=32):
        """Generate Gravatar URL for an email address."""
        email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
        return email_hash

    @app.template_filter('timeago')
    def timeago_filter(date):
        """Convert datetime to relative time (e.g., "2 hours ago")."""
        if not date:
            return ''
        now = datetime.utcnow()
        return timeago.format(date, now)

    @app.template_filter('truncate_html')
    def truncate_html_filter(text, length=100, suffix='...'):
        """Truncate HTML text to a certain number of characters."""
        if not text:
            return ''
        
        soup = BeautifulSoup(text, 'html.parser')
        text_content = soup.get_text()
        
        if len(text_content) <= length:
            return text
            
        truncated = text_content[:length].rsplit(' ', 1)[0] + suffix
        return truncated

    @app.template_filter('strip_html')
    def strip_html_filter(text):
        """Remove HTML tags from text."""
        if not text:
            return ''
        return bleach.clean(text, tags=[], strip=True)

    @app.template_filter('sanitize')
    def sanitize_filter(text):
        """Sanitize HTML content."""
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img'
        ]
        allowed_attrs = {
            'a': ['href', 'title', 'rel'],
            'img': ['src', 'alt', 'title']
        }
        return Markup(bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        ))

    @app.template_filter('domain')
    def domain_filter(url):
        """Extract domain from URL."""
        if not url:
            return ''
        parsed = urlparse(url)
        return parsed.netloc

    @app.template_filter('format_date')
    def format_date_filter(date, format='%B %d, %Y'):
        """Format date with custom format string."""
        if not date:
            return ''
        return date.strftime(format)

    @app.template_filter('wordcount')
    def wordcount_filter(text):
        """Count words in text."""
        if not text:
            return 0
        text = strip_html_filter(text)
        words = text.split()
        count = len(words)
        # Estimate reading time (assuming 200 words per minute)
        minutes = max(1, round(count / 200))
        return minutes

    @app.template_filter('pluralize')
    def pluralize_filter(number, singular='', plural='s'):
        """Return singular or plural suffix based on number."""
        return singular if number == 1 else plural

    @app.template_filter('filesize')
    def filesize_filter(size):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    @app.template_filter('excerpt')
    def excerpt_filter(text, length=150, suffix='...'):
        """Generate an excerpt from text content."""
        if not text:
            return ''
        
        # Remove HTML tags
        text = strip_html_filter(text)
        
        # Truncate to length
        if len(text) <= length:
            return text
            
        truncated = text[:length].rsplit(' ', 1)[0] + suffix
        return truncated

    @app.template_filter('json')
    def json_filter(value):
        """Convert string to JSON if it's valid."""
        import json
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return value

    @app.template_filter('active_link')
    def active_link_filter(path, active_class='active'):
        """Return active class if current path matches."""
        from flask import request
        return active_class if request.path.startswith(path) else ''

    @app.template_filter('theme_asset')
    def theme_asset_filter(path):
        """Generate URL for theme asset."""
        from flask import url_for
        from ..utils.theme import get_active_theme
        theme = get_active_theme()
        if theme:
            return url_for('static', filename=f'themes/{theme.directory}/{path}')
        return url_for('static', filename=path)

    @app.template_filter('split')
    def split_filter(value, delimiter=','):
        """Split string into list."""
        if not value:
            return []
        return [x.strip() for x in value.split(delimiter)]

    @app.template_filter('join')
    def join_filter(value, delimiter=', '):
        """Join list into string."""
        if not value:
            return ''
        return delimiter.join(value)
