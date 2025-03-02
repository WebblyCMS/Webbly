import os
import time
from datetime import datetime, timedelta
from threading import Thread
from flask import current_app
from .models import Post, Page, User, Comment, db
from .utils.settings import get_setting
from .utils.media import delete_file
from .utils.email import send_email
from .cache import cache
from .search import search
from .sitemap import Sitemap

class TaskManager:
    """Background task manager for Webbly CMS."""
    
    def __init__(self, app=None):
        self.app = app
        self.tasks = {}
        self.scheduled_tasks = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize task manager with Flask application."""
        self.app = app
        
        # Register default tasks
        self.register_task('cleanup_old_drafts', self.cleanup_old_drafts)
        self.register_task('cleanup_expired_sessions', self.cleanup_expired_sessions)
        self.register_task('cleanup_old_media', self.cleanup_old_media)
        self.register_task('send_digest_emails', self.send_digest_emails)
        self.register_task('update_search_index', self.update_search_index)
        self.register_task('update_sitemap', self.update_sitemap)
        self.register_task('backup_database', self.backup_database)
        
        # Schedule default tasks
        self.schedule_task('cleanup_old_drafts', hours=24)
        self.schedule_task('cleanup_expired_sessions', hours=1)
        self.schedule_task('cleanup_old_media', days=7)
        self.schedule_task('send_digest_emails', hours=24)
        self.schedule_task('update_search_index', hours=1)
        self.schedule_task('update_sitemap', hours=24)
        self.schedule_task('backup_database', days=1)
        
        # Start scheduler thread
        self.start_scheduler()

    def register_task(self, name, func):
        """Register a new task."""
        self.tasks[name] = func

    def schedule_task(self, name, minutes=None, hours=None, days=None):
        """Schedule a task to run periodically."""
        if name not in self.tasks:
            raise ValueError(f"Task {name} not registered")
        
        interval = timedelta(
            minutes=minutes or 0,
            hours=hours or 0,
            days=days or 0
        ).total_seconds()
        
        self.scheduled_tasks.append({
            'name': name,
            'interval': interval,
            'last_run': None
        })

    def run_task(self, name, *args, **kwargs):
        """Run a task asynchronously."""
        if name not in self.tasks:
            raise ValueError(f"Task {name} not registered")
        
        def run_in_context():
            with self.app.app_context():
                try:
                    self.tasks[name](*args, **kwargs)
                except Exception as e:
                    current_app.logger.error(f"Error running task {name}: {str(e)}")
        
        thread = Thread(target=run_in_context)
        thread.daemon = True
        thread.start()
        return thread

    def start_scheduler(self):
        """Start the task scheduler."""
        def scheduler():
            while True:
                with self.app.app_context():
                    now = time.time()
                    for task in self.scheduled_tasks:
                        if (task['last_run'] is None or 
                            now - task['last_run'] >= task['interval']):
                            self.run_task(task['name'])
                            task['last_run'] = now
                time.sleep(60)  # Check every minute
        
        thread = Thread(target=scheduler)
        thread.daemon = True
        thread.start()

    def cleanup_old_drafts(self):
        """Delete old draft posts."""
        threshold = datetime.utcnow() - timedelta(days=30)
        drafts = Post.query.filter_by(published=False)\
            .filter(Post.updated_at < threshold)\
            .all()
        
        for draft in drafts:
            if draft.featured_image:
                delete_file(draft.featured_image)
            db.session.delete(draft)
        
        db.session.commit()

    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        from flask_session import Session
        if isinstance(Session.redis, dict):
            # File-based sessions
            session_dir = self.app.config['SESSION_FILE_DIR']
            threshold = datetime.utcnow() - timedelta(days=7)
            
            for filename in os.listdir(session_dir):
                filepath = os.path.join(session_dir, filename)
                if os.path.getmtime(filepath) < threshold.timestamp():
                    os.remove(filepath)

    def cleanup_old_media(self):
        """Clean up unused media files."""
        uploads_dir = os.path.join(self.app.root_path, 'static', 'uploads')
        threshold = datetime.utcnow() - timedelta(days=7)
        
        for root, _, files in os.walk(uploads_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.getmtime(filepath) < threshold.timestamp():
                    # Check if file is referenced in any content
                    filename = os.path.relpath(filepath, uploads_dir)
                    if not self._is_file_referenced(filename):
                        os.remove(filepath)

    def send_digest_emails(self):
        """Send daily digest emails to subscribers."""
        if not get_setting('enable_digests', 'false').lower() == 'true':
            return
            
        # Get posts from last 24 hours
        threshold = datetime.utcnow() - timedelta(days=1)
        posts = Post.query.filter_by(published=True)\
            .filter(Post.created_at > threshold)\
            .all()
        
        if not posts:
            return
        
        # Get subscribers
        subscribers = User.query.filter_by(subscribed_to_digest=True).all()
        
        for user in subscribers:
            send_email(
                subject=f"Daily Digest - {get_setting('site_title')}",
                recipients=[user.email],
                template='email/digest',
                user=user,
                posts=posts
            )

    def update_search_index(self):
        """Update search index."""
        search.reindex()

    def update_sitemap(self):
        """Update sitemap."""
        sitemap = Sitemap(self.app)
        xml = sitemap.generate_sitemap()
        
        sitemap_path = os.path.join(
            self.app.root_path, 'static', 'sitemap.xml'
        )
        with open(sitemap_path, 'w') as f:
            f.write(xml)

    def backup_database(self):
        """Create database backup."""
        import shutil
        from datetime import datetime
        
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(self.app.root_path, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Create backup filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'webbly_{timestamp}.db')
        
        # Copy database file
        db_path = self.app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        shutil.copy2(db_path, backup_file)
        
        # Remove old backups (keep last 5)
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
        for old_backup in backups[:-5]:
            os.remove(os.path.join(backup_dir, old_backup))

    def _is_file_referenced(self, filename):
        """Check if a file is referenced in any content."""
        # Check posts
        if Post.query.filter(
            (Post.content.like(f'%{filename}%')) |
            (Post.featured_image == filename)
        ).first():
            return True
        
        # Check pages
        if Page.query.filter(
            Page.content.like(f'%{filename}%')
        ).first():
            return True
        
        return False

# Initialize task manager
task_manager = TaskManager()
