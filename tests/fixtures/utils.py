"""Common test helper functions and utilities."""

import os
import re
import json
import time
import hashlib
import tempfile
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from .config import TEST_TEMP_DIR
from .logging import logger

def wait_for(condition: Callable[[], bool], timeout: int = 30, interval: int = 1,
             message: str = None) -> bool:
    """Wait for a condition to be true."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    
    if message:
        logger.error(f"Timeout waiting for condition: {message}")
    return False

def compare_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any],
                 exclude_keys: List[str] = None) -> bool:
    """Compare two dictionaries, optionally excluding certain keys."""
    if exclude_keys:
        dict1 = {k: v for k, v in dict1.items() if k not in exclude_keys}
        dict2 = {k: v for k, v in dict2.items() if k not in exclude_keys}
    return dict1 == dict2

def compare_lists(list1: List[Any], list2: List[Any],
                 key_func: Callable[[Any], Any] = None) -> bool:
    """Compare two lists, optionally using a key function."""
    if key_func:
        return sorted(list1, key=key_func) == sorted(list2, key=key_func)
    return sorted(list1) == sorted(list2)

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return ' '.join(text.split())

def normalize_html(html: str) -> str:
    """Normalize HTML content."""
    # Remove whitespace between tags
    html = re.sub(r'>\s+<', '><', html.strip())
    # Normalize whitespace in text content
    html = re.sub(r'\s+', ' ', html)
    return html

def extract_csrf_token(html: str) -> Optional[str]:
    """Extract CSRF token from HTML."""
    match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', html)
    return match.group(1) if match else None

def parse_response_data(response) -> Dict[str, Any]:
    """Parse response data based on content type."""
    content_type = response.headers.get('Content-Type', '')
    
    if 'application/json' in content_type:
        return response.json()
    elif 'text/html' in content_type:
        return {'html': response.text}
    else:
        return {'data': response.text}

def get_file_hash(file_path: Union[str, Path]) -> str:
    """Get file hash."""
    file_path = Path(file_path)
    hasher = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()

@contextmanager
def temp_file(content: str = '', suffix: str = '.txt') -> Path:
    """Create a temporary file with content."""
    fd, path = tempfile.mkstemp(suffix=suffix, dir=TEST_TEMP_DIR)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        yield Path(path)
    finally:
        os.unlink(path)

@contextmanager
def temp_directory() -> Path:
    """Create a temporary directory."""
    path = tempfile.mkdtemp(dir=TEST_TEMP_DIR)
    try:
        yield Path(path)
    finally:
        import shutil
        shutil.rmtree(path)

def create_test_file(path: Union[str, Path], content: str = '') -> Path:
    """Create a test file with content."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path

def create_test_image(path: Union[str, Path], size: tuple = (100, 100)) -> Path:
    """Create a test image file."""
    from PIL import Image
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    image = Image.new('RGB', size, color='red')
    image.save(path)
    return path

def load_json_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)

def save_json_file(data: Dict[str, Any], path: Union[str, Path]):
    """Save JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def format_datetime(dt: datetime) -> str:
    """Format datetime for testing."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string."""
    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

def get_relative_url(url: str) -> str:
    """Get relative URL from absolute URL."""
    parsed = urlparse(url)
    return parsed.path + ('?' + parsed.query if parsed.query else '')

def get_query_params(url: str) -> Dict[str, List[str]]:
    """Get query parameters from URL."""
    parsed = urlparse(url)
    return parse_qs(parsed.query)

def generate_random_string(length: int = 10) -> str:
    """Generate random string."""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_email() -> str:
    """Generate random email address."""
    return f"{generate_random_string()}@example.com"

def generate_random_password(length: int = 12) -> str:
    """Generate random password."""
    import random
    import string
    
    # Ensure at least one of each required character type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice('!@#$%^&*')
    ]
    
    # Fill remaining length with random characters
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password.extend(random.choices(chars, k=length - len(password)))
    
    # Shuffle password
    random.shuffle(password)
    return ''.join(password)

def is_valid_uuid(uuid_str: str) -> bool:
    """Check if string is valid UUID."""
    import uuid
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False

def is_valid_email(email: str) -> bool:
    """Check if string is valid email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_url(url: str) -> bool:
    """Check if string is valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def truncate_string(s: str, length: int = 100) -> str:
    """Truncate string to specified length."""
    return s[:length] + '...' if len(s) > length else s

def strip_html(html: str) -> str:
    """Strip HTML tags from string."""
    return re.sub(r'<[^>]+>', '', html)

def escape_html(s: str) -> str:
    """Escape HTML special characters."""
    return (s.replace('&', '&amp;')
            .replace('<', '<')
            .replace('>', '>')
            .replace('"', '"')
            .replace("'", '&#39;'))

def slugify(s: str) -> str:
    """Convert string to URL-friendly slug."""
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[-\s]+', '-', s)
    return s.strip('-')
