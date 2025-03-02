import os
import json
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from flask import current_app, request
from werkzeug.contrib.cache import FileSystemCache, RedisCache

class Cache:
    """Cache manager for Webbly CMS."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize cache with Flask application."""
        self.app = app
        
        # Configure cache
        cache_type = app.config.get('CACHE_TYPE', 'filesystem')
        if cache_type == 'redis':
            self.cache = RedisCache(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                password=app.config.get('REDIS_PASSWORD'),
                db=app.config.get('REDIS_DB', 0),
                key_prefix=app.config.get('CACHE_KEY_PREFIX', 'webbly_')
            )
        else:
            cache_dir = os.path.join(app.root_path, 'cache')
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            self.cache = FileSystemCache(
                cache_dir,
                threshold=app.config.get('CACHE_THRESHOLD', 500),
                default_timeout=app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            )

        # Register context processor
        @app.context_processor
        def inject_cache_buster():
            def cache_bust(filename):
                """Add cache busting query parameter to static files."""
                if not app.debug:
                    filepath = os.path.join(app.root_path, 'static', filename)
                    if os.path.exists(filepath):
                        timestamp = int(os.path.getmtime(filepath))
                        return f"{filename}?v={timestamp}"
                return filename
            return dict(cache_bust=cache_bust)

    def get(self, key):
        """Get value from cache."""
        return self.cache.get(key)

    def set(self, key, value, timeout=None):
        """Set value in cache."""
        return self.cache.set(key, value, timeout)

    def delete(self, key):
        """Delete value from cache."""
        return self.cache.delete(key)

    def clear(self):
        """Clear entire cache."""
        return self.cache.clear()

    def cached(self, timeout=5 * 60, key_prefix='view'):
        """Decorator to cache view functions."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Create cache key from function name, args, and query params
                cache_key = self._make_cache_key(f, key_prefix, *args, **kwargs)
                
                # Try to get response from cache
                rv = self.get(cache_key)
                if rv is not None:
                    return rv
                
                # Generate response and cache it
                rv = f(*args, **kwargs)
                self.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

    def memoize(self, timeout=5 * 60):
        """Decorator to memoize function results."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = self._make_cache_key(f, 'memo', *args, **kwargs)
                rv = self.get(cache_key)
                if rv is not None:
                    return rv
                rv = f(*args, **kwargs)
                self.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

    def _make_cache_key(self, f, key_prefix, *args, **kwargs):
        """Generate a unique cache key."""
        # Start with function name
        key_parts = [key_prefix, f.__name__]
        
        # Add arguments
        for arg in args:
            key_parts.append(str(arg))
        
        # Add sorted keyword arguments
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Add query parameters if in request context
        if request:
            for key, value in sorted(request.args.items()):
                key_parts.append(f"{key}:{value}")
        
        # Join parts and hash
        key = '_'.join(key_parts)
        return hashlib.md5(key.encode()).hexdigest()

    def cached_property(self, timeout=5 * 60):
        """Decorator to cache class property values."""
        def decorator(f):
            @property
            @wraps(f)
            def decorated_function(self, *args, **kwargs):
                # Create cache key from class name, method name, and instance id
                key_parts = ['prop', self.__class__.__name__, f.__name__]
                if hasattr(self, 'id'):
                    key_parts.append(str(self.id))
                cache_key = '_'.join(key_parts)
                
                rv = self.get(cache_key)
                if rv is not None:
                    return rv
                    
                rv = f(self, *args, **kwargs)
                self.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

    def invalidate(self, pattern):
        """Invalidate all cache keys matching pattern."""
        if isinstance(self.cache, RedisCache):
            # Redis supports pattern matching
            keys = self.cache.cache._client.keys(pattern)
            if keys:
                self.cache.cache._client.delete(*keys)
        else:
            # FileSystemCache requires manual pattern matching
            cache_dir = self.cache._path
            for filename in os.listdir(cache_dir):
                if pattern in filename:
                    os.remove(os.path.join(cache_dir, filename))

    def remember(self, key, timeout=None):
        """Decorator to cache function result with explicit key."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                rv = self.get(key)
                if rv is not None:
                    return rv
                rv = f(*args, **kwargs)
                self.set(key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

# Initialize cache
cache = Cache()
