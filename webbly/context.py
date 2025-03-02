from datetime import datetime
from flask import request, current_app
from flask_login import current_user
from .models import Post, Page, Theme, Setting, User
from .utils.theme import get_active_theme
from .utils.settings import get_setting

def init_context_processors(app):
    """Initialize context processors for templates."""
    
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context."""
        def get_recent_posts(limit=5):
            """Get recent published posts."""
            return Post.query.filter_by(published=True)\
                .order_by(Post.created_at.desc())\
                .limit(limit)\
                .all()
        
        def get_pages():
            """Get all published pages."""
            return Page.query.filter_by(published=True)\
                .order_by(Page.title)\
                .all()
        
        def get_categories():
            """Get all categories with post counts."""
            # TODO: Implement categories
            return []
        
        def get_tags():
            """Get all tags with post counts."""
            # TODO: Implement tags
            return []
        
        def get_archive_months():
            """Get archive months with post counts."""
            # TODO: Implement archive
            return []
        
        def get_user_stats():
            """Get user statistics."""
            return {
                'total': User.query.count(),
                'admins': User.query.filter_by(is_admin=True).count(),
                'recent': User.query.order_by(User.created_at.desc()).limit(5).all()
            }
        
        def format_datetime(dt, format='%B %d, %Y %H:%M'):
            """Format datetime object."""
            return dt.strftime(format) if dt else ''
        
        def is_active_page(endpoint):
            """Check if current page matches endpoint."""
            return request.endpoint == endpoint
        
        def get_breadcrumbs():
            """Generate breadcrumbs based on current URL."""
            parts = request.path.split('/')
            breadcrumbs = []
            path = ''
            
            for part in parts:
                if part:
                    path += f'/{part}'
                    breadcrumbs.append({
                        'text': part.replace('-', ' ').title(),
                        'url': path
                    })
            
            return breadcrumbs
        
        return dict(
            get_recent_posts=get_recent_posts,
            get_pages=get_pages,
            get_categories=get_categories,
            get_tags=get_tags,
            get_archive_months=get_archive_months,
            get_user_stats=get_user_stats,
            format_datetime=format_datetime,
            is_active_page=is_active_page,
            get_breadcrumbs=get_breadcrumbs
        )
    
    @app.context_processor
    def theme_processor():
        """Add theme-related variables to template context."""
        theme = get_active_theme()
        return dict(
            active_theme=theme,
            theme_option=lambda key, default=None: theme.get_option(key, default) if theme else default
        )
    
    @app.context_processor
    def settings_processor():
        """Add settings to template context."""
        return dict(
            get_setting=get_setting,
            site_name=get_setting('site_title', 'Webbly Site'),
            site_description=get_setting('site_description', ''),
            site_logo=get_setting('site_logo'),
            favicon=get_setting('favicon'),
            social_links={
                'twitter': get_setting('social_twitter'),
                'facebook': get_setting('social_facebook'),
                'instagram': get_setting('social_instagram')
            }
        )
    
    @app.context_processor
    def user_processor():
        """Add user-related variables to template context."""
        return dict(
            current_user=current_user,
            is_admin=current_user.is_authenticated and current_user.is_admin if current_user else False
        )
    
    @app.context_processor
    def time_processor():
        """Add time-related variables to template context."""
        now = datetime.utcnow()
        return dict(
            now=now,
            year=now.year,
            month=now.month,
            day=now.day
        )
    
    @app.context_processor
    def meta_processor():
        """Add meta information to template context."""
        return dict(
            meta_title=lambda title: f"{title} - {get_setting('site_title')}" if title else get_setting('site_title'),
            meta_description=lambda desc: desc or get_setting('site_description'),
            meta_image=lambda image: image or get_setting('default_meta_image'),
            version=current_app.config.get('VERSION', '1.0.0')
        )
    
    @app.context_processor
    def debug_processor():
        """Add debug information to template context in development."""
        return dict(
            debug=current_app.debug,
            debug_queries=getattr(current_app, 'debug_queries', None)
        )
