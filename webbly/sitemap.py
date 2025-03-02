from datetime import datetime
from flask import url_for
from .models import Post, Page
from .utils.settings import get_setting

class Sitemap:
    """Sitemap generator for Webbly CMS."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize sitemap with Flask application."""
        self.app = app
        
        # Register CLI commands
        @app.cli.group()
        def sitemap():
            """Sitemap management commands."""
            pass

        @sitemap.command()
        def generate():
            """Generate sitemap.xml file."""
            self.generate_sitemap()
            click.echo("Sitemap generated successfully!")

    def generate_sitemap(self):
        """Generate XML sitemap."""
        urls = []
        
        with self.app.app_context():
            # Add homepage
            urls.append({
                'loc': url_for('core.index', _external=True),
                'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '1.0'
            })
            
            # Add posts
            posts = Post.query.filter_by(published=True).all()
            for post in posts:
                urls.append({
                    'loc': url_for('core.post', slug=post.slug, _external=True),
                    'lastmod': post.updated_at.strftime('%Y-%m-%d'),
                    'changefreq': 'weekly',
                    'priority': '0.8'
                })
            
            # Add pages
            pages = Page.query.filter_by(published=True).all()
            for page in pages:
                urls.append({
                    'loc': url_for('core.page', slug=page.slug, _external=True),
                    'lastmod': page.updated_at.strftime('%Y-%m-%d'),
                    'changefreq': 'monthly',
                    'priority': '0.6'
                })
            
            # Add category pages if enabled
            if get_setting('enable_categories', 'true').lower() == 'true':
                for category in self._get_categories():
                    urls.append({
                        'loc': url_for('core.category', slug=category.slug, _external=True),
                        'changefreq': 'weekly',
                        'priority': '0.5'
                    })
            
            # Add tag pages if enabled
            if get_setting('enable_tags', 'true').lower() == 'true':
                for tag in self._get_tags():
                    urls.append({
                        'loc': url_for('core.tag', slug=tag.slug, _external=True),
                        'changefreq': 'weekly',
                        'priority': '0.5'
                    })
            
            # Add archive pages if enabled
            if get_setting('enable_archives', 'true').lower() == 'true':
                for year, month in self._get_archive_dates():
                    urls.append({
                        'loc': url_for('core.archive', year=year, month=month, _external=True),
                        'changefreq': 'monthly',
                        'priority': '0.4'
                    })
        
        return self._render_sitemap(urls)

    def generate_sitemap_index(self):
        """Generate sitemap index for large sites."""
        sitemaps = []
        
        with self.app.app_context():
            # Main sitemap
            sitemaps.append({
                'loc': url_for('core.sitemap', _external=True),
                'lastmod': datetime.utcnow().strftime('%Y-%m-%d')
            })
            
            # Post sitemaps (paginated)
            post_count = Post.query.filter_by(published=True).count()
            sitemap_size = 1000  # URLs per sitemap
            
            for i in range((post_count // sitemap_size) + 1):
                sitemaps.append({
                    'loc': url_for('core.sitemap_posts', page=i+1, _external=True),
                    'lastmod': datetime.utcnow().strftime('%Y-%m-%d')
                })
        
        return self._render_sitemap_index(sitemaps)

    def generate_post_sitemap(self, page=1, per_page=1000):
        """Generate sitemap for posts (paginated)."""
        urls = []
        
        with self.app.app_context():
            posts = Post.query.filter_by(published=True)\
                .order_by(Post.created_at.desc())\
                .paginate(page=page, per_page=per_page)
            
            for post in posts.items:
                urls.append({
                    'loc': url_for('core.post', slug=post.slug, _external=True),
                    'lastmod': post.updated_at.strftime('%Y-%m-%d'),
                    'changefreq': 'weekly',
                    'priority': '0.8'
                })
        
        return self._render_sitemap(urls)

    def _render_sitemap(self, urls):
        """Render sitemap XML."""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for url in urls:
            xml.append('  <url>')
            xml.append(f'    <loc>{url["loc"]}</loc>')
            if 'lastmod' in url:
                xml.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
            if 'changefreq' in url:
                xml.append(f'    <changefreq>{url["changefreq"]}</changefreq>')
            if 'priority' in url:
                xml.append(f'    <priority>{url["priority"]}</priority>')
            xml.append('  </url>')
        
        xml.append('</urlset>')
        return '\n'.join(xml)

    def _render_sitemap_index(self, sitemaps):
        """Render sitemap index XML."""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for sitemap in sitemaps:
            xml.append('  <sitemap>')
            xml.append(f'    <loc>{sitemap["loc"]}</loc>')
            if 'lastmod' in sitemap:
                xml.append(f'    <lastmod>{sitemap["lastmod"]}</lastmod>')
            xml.append('  </sitemap>')
        
        xml.append('</sitemapindex>')
        return '\n'.join(xml)

    def _get_categories(self):
        """Get all categories."""
        # TODO: Implement categories
        return []

    def _get_tags(self):
        """Get all tags."""
        # TODO: Implement tags
        return []

    def _get_archive_dates(self):
        """Get all archive dates."""
        dates = db.session.query(
            db.func.strftime('%Y', Post.created_at).label('year'),
            db.func.strftime('%m', Post.created_at).label('month')
        ).filter(
            Post.published == True
        ).group
