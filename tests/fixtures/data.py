"""Test data generation and management utilities."""

import random
import string
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

from .config import TEST_DATA_DIR
from .logging import logger

class TestDataGenerator:
    """Test data generator."""
    
    def __init__(self):
        self.fake = Faker()
    
    def generate_user(self, is_admin: bool = False) -> Dict[str, Any]:
        """Generate user data."""
        return {
            'username': self.fake.user_name(),
            'email': self.fake.email(),
            'password': self.fake.password(
                length=12,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
            ),
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'is_admin': is_admin,
            'created_at': self.fake.date_time_this_year()
        }
    
    def generate_post(self, author_id: int = None) -> Dict[str, Any]:
        """Generate post data."""
        return {
            'title': self.fake.sentence(),
            'content': self.fake.text(max_nb_chars=2000),
            'excerpt': self.fake.text(max_nb_chars=200),
            'author_id': author_id,
            'published': self.fake.boolean(chance_of_getting_true=80),
            'created_at': self.fake.date_time_this_year(),
            'updated_at': self.fake.date_time_this_year(),
            'tags': [self.fake.word() for _ in range(random.randint(1, 5))]
        }
    
    def generate_page(self, author_id: int = None) -> Dict[str, Any]:
        """Generate page data."""
        return {
            'title': self.fake.sentence(),
            'content': self.fake.text(max_nb_chars=5000),
            'author_id': author_id,
            'template': random.choice(['default', 'sidebar', 'full-width']),
            'published': self.fake.boolean(chance_of_getting_true=90),
            'created_at': self.fake.date_time_this_year(),
            'updated_at': self.fake.date_time_this_year()
        }
    
    def generate_comment(self, post_id: int = None, author_id: int = None) -> Dict[str, Any]:
        """Generate comment data."""
        return {
            'content': self.fake.text(max_nb_chars=500),
            'post_id': post_id,
            'author_id': author_id,
            'approved': self.fake.boolean(chance_of_getting_true=70),
            'created_at': self.fake.date_time_this_year()
        }
    
    def generate_theme(self) -> Dict[str, Any]:
        """Generate theme data."""
        return {
            'name': f"{self.fake.word().title()} Theme",
            'directory': self.fake.slug(),
            'version': f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            'author': self.fake.name(),
            'description': self.fake.text(max_nb_chars=200),
            'options': {
                'primary_color': self.fake.hex_color(),
                'font_family': random.choice(['Arial', 'Helvetica', 'Roboto', 'Open Sans']),
                'sidebar_position': random.choice(['left', 'right'])
            }
        }
    
    def generate_plugin(self) -> Dict[str, Any]:
        """Generate plugin data."""
        return {
            'name': f"{self.fake.word().title()} Plugin",
            'directory': self.fake.slug(),
            'version': f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            'author': self.fake.name(),
            'description': self.fake.text(max_nb_chars=200),
            'settings': {
                'enabled': self.fake.boolean(),
                'api_key': uuid.uuid4().hex,
                'cache_timeout': random.randint(300, 3600)
            }
        }
    
    def generate_settings(self) -> Dict[str, Any]:
        """Generate site settings data."""
        return {
            'site_title': f"{self.fake.word().title()} Site",
            'site_description': self.fake.text(max_nb_chars=200),
            'admin_email': self.fake.email(),
            'posts_per_page': random.randint(5, 20),
            'comments_enabled': self.fake.boolean(chance_of_getting_true=80),
            'comment_moderation': self.fake.boolean(chance_of_getting_true=70),
            'theme': 'default',
            'timezone': self.fake.timezone(),
            'date_format': random.choice(['Y-m-d', 'd/m/Y', 'm/d/Y']),
            'time_format': random.choice(['H:i', 'h:i A'])
        }

class TestDataManager:
    """Test data manager."""
    
    def __init__(self):
        self.generator = TestDataGenerator()
        self.data_dir = TEST_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_test_data(self, num_users: int = 5, num_posts: int = 20,
                          num_pages: int = 5, num_comments: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """Generate complete test dataset."""
        data = {
            'users': [],
            'posts': [],
            'pages': [],
            'comments': [],
            'themes': [],
            'plugins': [],
            'settings': self.generator.generate_settings()
        }
        
        # Generate users
        admin = self.generator.generate_user(is_admin=True)
        data['users'].append(admin)
        
        for _ in range(num_users - 1):
            data['users'].append(self.generator.generate_user())
        
        # Generate posts
        for _ in range(num_posts):
            author_id = random.randint(1, num_users)
            data['posts'].append(self.generator.generate_post(author_id))
        
        # Generate pages
        for _ in range(num_pages):
            author_id = random.randint(1, num_users)
            data['pages'].append(self.generator.generate_page(author_id))
        
        # Generate comments
        for _ in range(num_comments):
            post_id = random.randint(1, num_posts)
            author_id = random.randint(1, num_users)
            data['comments'].append(self.generator.generate_comment(post_id, author_id))
        
        # Generate themes and plugins
        for _ in range(3):
            data['themes'].append(self.generator.generate_theme())
            data['plugins'].append(self.generator.generate_plugin())
        
        return data
    
    def save_test_data(self, data: Dict[str, Any], filename: str = 'test_data.json'):
        """Save test data to file."""
        file_path = self.data_dir / filename
        
        # Convert datetime objects to strings
        data_copy = self._serialize_data(data)
        
        with open(file_path, 'w') as f:
            json.dump(data_copy, f, indent=2)
        
        logger.info(f"Test data saved to {file_path}")
    
    def load_test_data(self, filename: str = 'test_data.json') -> Dict[str, Any]:
        """Load test data from file."""
        file_path = self.data_dir / filename
        
        with open(file_path) as f:
            data = json.load(f)
        
        # Convert string dates back to datetime objects
        return self._deserialize_data(data)
    
    def _serialize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize data for JSON storage."""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        return data
    
    def _deserialize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize data from JSON storage."""
        if isinstance(data, str):
            try:
                return datetime.fromisoformat(data)
            except ValueError:
                return data
        elif isinstance(data, dict):
            return {k: self._deserialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deserialize_data(item) for item in data]
        return data

class TestDataLoader:
    """Test data loader for database."""
    
    def __init__(self, db):
        self.db = db
        self.manager = TestDataManager()
    
    def load_all(self, data: Dict[str, Any]):
        """Load all test data into database."""
        try:
            self.load_users(data.get('users', []))
            self.load_posts(data.get('posts', []))
            self.load_pages(data.get('pages', []))
            self.load_comments(data.get('comments', []))
            self.load_themes(data.get('themes', []))
            self.load_plugins(data.get('plugins', []))
            self.load_settings(data.get('settings', {}))
            
            self.db.session.commit()
            logger.info("Test data loaded successfully")
        
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error loading test data: {e}")
            raise
    
    def load_users(self, users: List[Dict[str, Any]]):
        """Load user data into database."""
        from webbly.models import User
        for user_data in users:
            user = User(**user_data)
            self.db.session.add(user)
    
    def load_posts(self, posts: List[Dict[str, Any]]):
        """Load post data into database."""
        from webbly.models import Post
        for post_data in posts:
            post = Post(**post_data)
            self.db.session.add(post)
    
    def load_pages(self, pages: List[Dict[str, Any]]):
        """Load page data into database."""
        from webbly.models import Page
        for page_data in pages:
            page = Page(**page_data)
            self.db.session.add(page)
    
    def load_comments(self, comments: List[Dict[str, Any]]):
        """Load comment data into database."""
        from webbly.models import Comment
        for comment_data in comments:
            comment = Comment(**comment_data)
            self.db.session.add(comment)
    
    def load_themes(self, themes: List[Dict[str, Any]]):
        """Load theme data into database."""
        from webbly.models import Theme
        for theme_data in themes:
            theme = Theme(**theme_data)
            self.db.session.add(theme)
    
    def load_plugins(self, plugins: List[Dict[str, Any]]):
        """Load plugin data into database."""
        from webbly.models import Plugin
        for plugin_data in plugins:
            plugin = Plugin(**plugin_data)
            self.db.session.add(plugin)
    
    def load_settings(self, settings: Dict[str, Any]):
        """Load settings data into database."""
        from webbly.models import Setting
        for key, value in settings.items():
            setting = Setting(key=key, value=str(value))
            self.db.session.add(setting)

# Global instances
generator = TestDataGenerator()
manager = TestDataManager()
