import os
import tempfile

class TestConfig:
    """Test configuration."""
    
    # Flask settings
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.test'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SECRET_KEY = 'test-secret-key'
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_TIME = 15  # minutes
    
    # Upload settings
    UPLOAD_FOLDER = tempfile.mkdtemp()
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Email settings
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'test@example.com'
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = tempfile.mkdtemp()
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Theme settings
    THEME_FOLDER = os.path.join(tempfile.mkdtemp(), 'themes')
    DEFAULT_THEME = 'default'
    
    # Plugin settings
    PLUGIN_FOLDER = os.path.join(tempfile.mkdtemp(), 'plugins')
    
    # Media settings
    MEDIA_FOLDER = os.path.join(tempfile.mkdtemp(), 'media')
    MEDIA_URL = '/media/'
    
    # Search settings
    SEARCH_RESULT_LIMIT = 20
    
    # Feed settings
    FEED_POSTS_LIMIT = 20
    
    # Sitemap settings
    SITEMAP_INCLUDE_RULES = True
    SITEMAP_URL_SCHEME = 'http'
    
    # Logging settings
    LOG_FOLDER = os.path.join(tempfile.mkdtemp(), 'logs')
    LOG_LEVEL = 'INFO'
    
    # Admin settings
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    
    # Content settings
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20
    ENABLE_COMMENTS = True
    COMMENT_MODERATION = True
    
    # Social settings
    SOCIAL_LINKS = {
        'twitter': 'https://twitter.com/test',
        'facebook': 'https://facebook.com/test',
        'instagram': 'https://instagram.com/test'
    }
    
    # Analytics settings
    ENABLE_ANALYTICS = False
    ANALYTICS_ID = None
    
    # Maintenance settings
    MAINTENANCE_MODE = False
    
    # Rate limiting
    RATELIMIT_ENABLED = False
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with test settings."""
        # Create necessary directories
        os.makedirs(cls.THEME_FOLDER, exist_ok=True)
        os.makedirs(cls.PLUGIN_FOLDER, exist_ok=True)
        os.makedirs(cls.MEDIA_FOLDER, exist_ok=True)
        os.makedirs(cls.LOG_FOLDER, exist_ok=True)
        
        # Configure logging
        if not os.path.exists(cls.LOG_FOLDER):
            os.makedirs(cls.LOG_FOLDER)
        
        # Configure file paths
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['THEME_FOLDER'] = cls.THEME_FOLDER
        app.config['PLUGIN_FOLDER'] = cls.PLUGIN_FOLDER
        app.config['MEDIA_FOLDER'] = cls.MEDIA_FOLDER
        app.config['LOG_FOLDER'] = cls.LOG_FOLDER
        
        # Configure session
        app.config['SESSION_FILE_DIR'] = cls.SESSION_FILE_DIR
        
        # Additional test-specific configuration
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['TESTING'] = True

def cleanup_test_files():
    """Clean up temporary test files."""
    dirs_to_cleanup = [
        TestConfig.UPLOAD_FOLDER,
        TestConfig.THEME_FOLDER,
        TestConfig.PLUGIN_FOLDER,
        TestConfig.MEDIA_FOLDER,
        TestConfig.LOG_FOLDER,
        TestConfig.SESSION_FILE_DIR
    ]
    
    for directory in dirs_to_cleanup:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(directory)
