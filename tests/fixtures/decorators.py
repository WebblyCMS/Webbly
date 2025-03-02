"""Custom test decorators and wrappers."""

import functools
import pytest
from datetime import datetime, timedelta
from flask import url_for
from .mocks import MockResponse, MockMailer
from .constants import TEST_USER, TEST_ADMIN

def requires_login(f):
    """Decorator to mark tests that require user login."""
    @functools.wraps(f)
    def wrapper(client, *args, **kwargs):
        # Login as test user
        client.post(url_for('auth.login'), data={
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        })
        try:
            return f(client, *args, **kwargs)
        finally:
            # Logout after test
            client.get(url_for('auth.logout'))
    return wrapper

def requires_admin(f):
    """Decorator to mark tests that require admin login."""
    @functools.wraps(f)
    def wrapper(client, *args, **kwargs):
        # Login as admin
        client.post(url_for('auth.login'), data={
            'email': TEST_ADMIN['email'],
            'password': TEST_ADMIN['password']
        })
        try:
            return f(client, *args, **kwargs)
        finally:
            # Logout after test
            client.get(url_for('auth.logout'))
    return wrapper

def with_context(app):
    """Decorator to run test with application context."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with app.app_context():
                return f(*args, **kwargs)
        return wrapper
    return decorator

def with_request_context(app):
    """Decorator to run test with request context."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with app.test_request_context():
                return f(*args, **kwargs)
        return wrapper
    return decorator

def mock_datetime(dt=None):
    """Decorator to mock datetime in tests."""
    if dt is None:
        dt = datetime(2023, 1, 1, 12, 0, 0)
    
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with pytest.MonkeyPatch.context() as mp:
                class MockDateTime:
                    @classmethod
                    def now(cls):
                        return dt
                    
                    @classmethod
                    def utcnow(cls):
                        return dt
                
                mp.setattr('webbly.utils.datetime', MockDateTime)
                return f(*args, **kwargs)
        return wrapper
    return decorator

def mock_mail(f):
    """Decorator to mock email sending in tests."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        mailer = MockMailer()
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('webbly.utils.email.mail', mailer)
            return f(*args, **kwargs)
    return wrapper

def mock_requests(responses=None):
    """Decorator to mock HTTP requests in tests."""
    if responses is None:
        responses = {}
    
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            def mock_request(method, url, *args, **kwargs):
                key = (method, url)
                if key in responses:
                    resp = responses[key]
                    return MockResponse(**resp)
                return MockResponse(status_code=404)
            
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr('requests.request', mock_request)
                return f(*args, **kwargs)
        return wrapper
    return decorator

def track_queries(f):
    """Decorator to track database queries in tests."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        from flask_sqlalchemy import get_debug_queries
        
        queries_before = len(get_debug_queries())
        result = f(*args, **kwargs)
        queries_after = len(get_debug_queries())
        
        print(f"\nQueries executed: {queries_after - queries_before}")
        for query in get_debug_queries()[queries_before:]:
            print(f"Query: {query.statement}")
            print(f"Parameters: {query.parameters}")
            print(f"Duration: {query.duration}")
            print()
        
        return result
    return wrapper

def measure_time(f):
    """Decorator to measure test execution time."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = f(*args, **kwargs)
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\nTest duration: {duration}")
        return result
    return wrapper

def retry_on_failure(max_attempts=3, delay=1):
    """Decorator to retry failed tests."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            import time
            attempts = 0
            while attempts < max_attempts:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def skip_in_ci(reason=None):
    """Decorator to skip tests in CI environment."""
    import os
    return pytest.mark.skipif(
        os.environ.get('CI') == 'true',
        reason=reason or 'Test skipped in CI environment'
    )

def only_in_ci(reason=None):
    """Decorator to run tests only in CI environment."""
    import os
    return pytest.mark.skipif(
        os.environ.get('CI') != 'true',
        reason=reason or 'Test only runs in CI environment'
    )

def requires_database(f):
    """Decorator to mark tests that require database."""
    return pytest.mark.requires_db(f)

def requires_cache(f):
    """Decorator to mark tests that require cache."""
    return pytest.mark.requires_cache(f)

def requires_email(f):
    """Decorator to mark tests that require email."""
    return pytest.mark.requires_email(f)

def requires_media(f):
    """Decorator to mark tests that require media storage."""
    return pytest.mark.requires_media(f)

def requires_internet(f):
    """Decorator to mark tests that require internet connection."""
    return pytest.mark.requires_internet(f)
