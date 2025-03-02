"""Mock objects and responses for testing."""

import json
from unittest.mock import MagicMock, PropertyMock
from datetime import datetime, timedelta

# Mock HTTP responses
class MockResponse:
    """Mock requests.Response object."""
    
    def __init__(self, status_code=200, json_data=None, content=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self._content = content
        self.headers = headers or {}
    
    def json(self):
        return self._json_data
    
    @property
    def content(self):
        return self._content
    
    @property
    def text(self):
        if isinstance(self._content, bytes):
            return self._content.decode('utf-8')
        return self._content

# Mock email
class MockMailMessage:
    """Mock Flask-Mail Message object."""
    
    def __init__(self, subject='', recipients=None, body='', html='', sender=None):
        self.subject = subject
        self.recipients = recipients or []
        self.body = body
        self.html = html
        self.sender = sender

class MockMailer:
    """Mock Flask-Mail mailer."""
    
    def __init__(self):
        self.messages = []
    
    def send(self, message):
        self.messages.append(message)

# Mock file storage
class MockFileStorage:
    """Mock Werkzeug FileStorage object."""
    
    def __init__(self, filename='test.txt', content=b'test content', content_type='text/plain'):
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self._file = MagicMock()
        self._file.read.return_value = content
    
    def save(self, dst):
        with open(dst, 'wb') as f:
            f.write(self.content)
    
    @property
    def stream(self):
        return self._file

# Mock cache
class MockCache:
    """Mock cache object."""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value, timeout=None):
        self._cache[key] = value
    
    def delete(self, key):
        self._cache.pop(key, None)
    
    def clear(self):
        self._cache.clear()

# Mock search
class MockSearchResult:
    """Mock search result."""
    
    def __init__(self, title, content, score=1.0):
        self.title = title
        self.content = content
        self.score = score

class MockSearch:
    """Mock search engine."""
    
    def __init__(self):
        self.indexed = []
        self.results = []
    
    def index(self, document):
        self.indexed.append(document)
    
    def search(self, query):
        return self.results

# Mock theme
class MockTheme:
    """Mock theme object."""
    
    def __init__(self, name='Test Theme', directory='test_theme'):
        self.name = name
        self.directory = directory
        self.options = {}
    
    def get_option(self, key, default=None):
        return self.options.get(key, default)
    
    def set_option(self, key, value):
        self.options[key] = value

# Mock plugin
class MockPlugin:
    """Mock plugin object."""
    
    def __init__(self, name='Test Plugin', directory='test_plugin'):
        self.name = name
        self.directory = directory
        self.settings = {}
        self.active = False
    
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        self.settings[key] = value

# Mock user
class MockUser:
    """Mock user object."""
    
    def __init__(self, id=1, username='testuser', email='test@example.com', is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)

# Mock request context
class MockRequestContext:
    """Mock Flask request context."""
    
    def __init__(self, path='/', method='GET', data=None, headers=None):
        self.path = path
        self.method = method
        self.data = data or {}
        self.headers = headers or {}
        self.files = {}
        self.args = {}
        self.form = {}
        self.is_json = False
        self.cookies = {}
    
    def get_json(self):
        return self.data if self.is_json else None

# Mock response
def mock_success_response(data=None, message='Success'):
    """Create a mock success response."""
    return {
        'status': 'success',
        'message': message,
        'data': data
    }

def mock_error_response(message='Error', code='ERROR', status_code=400):
    """Create a mock error response."""
    return {
        'status': 'error',
        'message': message,
        'code': code,
        'status_code': status_code
    }

# Mock tasks
class MockTask:
    """Mock background task."""
    
    def __init__(self, success=True, result=None):
        self.success = success
        self.result = result
        self.started = False
        self.completed = False
        self.failed = False
    
    def start(self):
        self.started = True
    
    def complete(self):
        self.completed = True
    
    def fail(self):
        self.failed = True

class MockTaskQueue:
    """Mock task queue."""
    
    def __init__(self):
        self.tasks = []
    
    def enqueue(self, task):
        self.tasks.append(task)
    
    def process(self):
        for task in self.tasks:
            if task.success:
                task.complete()
            else:
                task.fail()

# Mock logger
class MockLogger:
    """Mock logger object."""
    
    def __init__(self):
        self.logs = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': []
        }
    
    def debug(self, message):
        self.logs['debug'].append(message)
    
    def info(self, message):
        self.logs['info'].append(message)
    
    def warning(self, message):
        self.logs['warning'].append(message)
    
    def error(self, message):
        self.logs['error'].append(message)
    
    def critical(self, message):
        self.logs['critical'].append(message)
