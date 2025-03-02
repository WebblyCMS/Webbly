"""Test cleanup and resource management utilities."""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Set
from contextlib import contextmanager

from .config import (
    TEST_TEMP_DIR, TEST_DATA_DIR, TEST_REPORTS_DIR,
    get_test_paths, get_test_timeout
)

class ResourceTracker:
    """Track resources that need cleanup."""
    
    def __init__(self):
        self.files: Set[Path] = set()
        self.directories: Set[Path] = set()
        self.databases: Set[str] = set()
        self.other_resources: List[dict] = []
    
    def add_file(self, path: Path):
        """Track a file for cleanup."""
        self.files.add(Path(path))
    
    def add_directory(self, path: Path):
        """Track a directory for cleanup."""
        self.directories.add(Path(path))
    
    def add_database(self, name: str):
        """Track a database for cleanup."""
        self.databases.add(name)
    
    def add_resource(self, resource_type: str, identifier: str, cleanup_func=None):
        """Track any other type of resource."""
        self.other_resources.append({
            'type': resource_type,
            'id': identifier,
            'cleanup': cleanup_func
        })
    
    def cleanup(self):
        """Clean up all tracked resources."""
        # Clean up files
        for file_path in self.files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logging.warning(f"Failed to delete file {file_path}: {e}")
        
        # Clean up directories
        for dir_path in self.directories:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
            except Exception as e:
                logging.warning(f"Failed to delete directory {dir_path}: {e}")
        
        # Clean up databases
        for db_name in self.databases:
            try:
                # Add database-specific cleanup logic here
                pass
            except Exception as e:
                logging.warning(f"Failed to clean up database {db_name}: {e}")
        
        # Clean up other resources
        for resource in self.other_resources:
            try:
                if resource['cleanup']:
                    resource['cleanup']()
            except Exception as e:
                logging.warning(
                    f"Failed to clean up {resource['type']} {resource['id']}: {e}"
                )
        
        # Clear all tracked resources
        self.files.clear()
        self.directories.clear()
        self.databases.clear()
        self.other_resources.clear()

# Global resource tracker
resource_tracker = ResourceTracker()

@contextmanager
def tracked_file(content='', suffix='.txt'):
    """Context manager for temporary test file."""
    import tempfile
    
    fd, path = tempfile.mkstemp(suffix=suffix, dir=TEST_TEMP_DIR)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        resource_tracker.add_file(path)
        yield Path(path)
    finally:
        if os.path.exists(path):
            os.unlink(path)

@contextmanager
def tracked_directory():
    """Context manager for temporary test directory."""
    import tempfile
    
    path = tempfile.mkdtemp(dir=TEST_TEMP_DIR)
    try:
        resource_tracker.add_directory(path)
        yield Path(path)
    finally:
        if os.path.exists(path):
            shutil.rmtree(path)

@contextmanager
def tracked_database(name: str):
    """Context manager for test database."""
    try:
        resource_tracker.add_database(name)
        yield name
    finally:
        # Add database cleanup logic here
        pass

def cleanup_test_files():
    """Clean up test-generated files."""
    paths = get_test_paths()
    
    # Clean temp directory
    if TEST_TEMP_DIR.exists():
        shutil.rmtree(TEST_TEMP_DIR)
        TEST_TEMP_DIR.mkdir()
    
    # Clean test data
    for item in TEST_DATA_DIR.glob('**/test_*'):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    
    # Clean test reports
    for item in TEST_REPORTS_DIR.glob('*'):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

def cleanup_test_database(app):
    """Clean up test database."""
    with app.app_context():
        from webbly.models import db
        db.drop_all()
        db.create_all()

def cleanup_test_cache(app):
    """Clean up test cache."""
    with app.app_context():
        from webbly.cache import cache
        cache.clear()

def cleanup_test_uploads(app):
    """Clean up test uploads."""
    upload_dir = Path(app.config['UPLOAD_FOLDER'])
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
        upload_dir.mkdir(parents=True)

def cleanup_test_media(app):
    """Clean up test media files."""
    media_dir = Path(app.config['MEDIA_FOLDER'])
    if media_dir.exists():
        shutil.rmtree(media_dir)
        media_dir.mkdir(parents=True)

def cleanup_test_themes(app):
    """Clean up test themes."""
    theme_dir = Path(app.config['THEME_FOLDER'])
    if theme_dir.exists():
        shutil.rmtree(theme_dir)
        theme_dir.mkdir(parents=True)

def cleanup_test_plugins(app):
    """Clean up test plugins."""
    plugin_dir = Path(app.config['PLUGIN_FOLDER'])
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
        plugin_dir.mkdir(parents=True)

def cleanup_all(app):
    """Clean up all test resources."""
    cleanup_test_files()
    cleanup_test_database(app)
    cleanup_test_cache(app)
    cleanup_test_uploads(app)
    cleanup_test_media(app)
    cleanup_test_themes(app)
    cleanup_test_plugins(app)
    resource_tracker.cleanup()

def pytest_sessionfinish(session):
    """Clean up after test session."""
    cleanup_all(session.app)

class CleanupManager:
    """Manager for test cleanup operations."""
    
    def __init__(self, app):
        self.app = app
        self.cleanups = []
    
    def add_cleanup(self, func, *args, **kwargs):
        """Add cleanup function to be called later."""
        self.cleanups.append((func, args, kwargs))
    
    def cleanup(self):
        """Execute all cleanup functions."""
        while self.cleanups:
            func, args, kwargs = self.cleanups.pop()
            try:
                func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Cleanup failed: {e}")

@contextmanager
def cleanup_manager(app):
    """Context manager for cleanup operations."""
    manager = CleanupManager(app)
    try:
        yield manager
    finally:
        manager.cleanup()
