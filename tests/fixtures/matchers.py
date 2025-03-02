"""Custom test matchers and comparison helpers."""

import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class Matcher:
    """Base class for custom matchers."""
    
    def __init__(self, expected):
        self.expected = expected
    
    def matches(self, actual):
        """Check if actual value matches expected value."""
        raise NotImplementedError
    
    def describe_to(self, description):
        """Describe the expected value."""
        raise NotImplementedError
    
    def describe_mismatch(self, actual, mismatch_description):
        """Describe why the actual value didn't match."""
        raise NotImplementedError

class IsHTML(Matcher):
    """Matcher for HTML content."""
    
    def matches(self, actual):
        try:
            soup = BeautifulSoup(actual, 'html.parser')
            return bool(soup.find())
        except:
            return False
    
    def describe_to(self, description):
        description.append('valid HTML content')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append('was invalid HTML')

class HasElement(Matcher):
    """Matcher for HTML elements."""
    
    def __init__(self, selector, text=None):
        self.selector = selector
        self.text = text
    
    def matches(self, actual):
        soup = BeautifulSoup(actual, 'html.parser')
        elements = soup.select(self.selector)
        if not elements:
            return False
        if self.text:
            return any(self.text in elem.text for elem in elements)
        return True
    
    def describe_to(self, description):
        desc = f'HTML containing element matching "{self.selector}"'
        if self.text:
            desc += f' with text "{self.text}"'
        description.append(desc)
    
    def describe_mismatch(self, actual, mismatch_description):
        soup = BeautifulSoup(actual, 'html.parser')
        elements = soup.select(self.selector)
        if not elements:
            mismatch_description.append(f'no elements matched selector "{self.selector}"')
        elif self.text:
            texts = [elem.text for elem in elements]
            mismatch_description.append(f'found elements but none contained text "{self.text}" (found: {texts})')

class IsJSON(Matcher):
    """Matcher for JSON content."""
    
    def matches(self, actual):
        import json
        try:
            if isinstance(actual, str):
                json.loads(actual)
            else:
                json.dumps(actual)
            return True
        except:
            return False
    
    def describe_to(self, description):
        description.append('valid JSON content')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append('was invalid JSON')

class HasKeys(Matcher):
    """Matcher for dictionary keys."""
    
    def matches(self, actual):
        return all(key in actual for key in self.expected)
    
    def describe_to(self, description):
        description.append(f'dictionary containing keys {self.expected}')
    
    def describe_mismatch(self, actual, mismatch_description):
        missing = [key for key in self.expected if key not in actual]
        mismatch_description.append(f'missing keys {missing}')

class MatchesRegex(Matcher):
    """Matcher for regex patterns."""
    
    def matches(self, actual):
        return bool(re.match(self.expected, actual))
    
    def describe_to(self, description):
        description.append(f'string matching pattern "{self.expected}"')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append(f'"{actual}" did not match pattern')

class IsWithinDelta(Matcher):
    """Matcher for numeric values within a delta."""
    
    def __init__(self, expected, delta):
        super().__init__(expected)
        self.delta = delta
    
    def matches(self, actual):
        return abs(actual - self.expected) <= self.delta
    
    def describe_to(self, description):
        description.append(f'number within {self.delta} of {self.expected}')
    
    def describe_mismatch(self, actual, mismatch_description):
        diff = abs(actual - self.expected)
        mismatch_description.append(f'was {actual} (diff: {diff})')

class IsWithinTimeDelta(Matcher):
    """Matcher for datetime values within a time delta."""
    
    def __init__(self, expected, delta):
        super().__init__(expected)
        self.delta = delta
    
    def matches(self, actual):
        return abs(actual - self.expected) <= self.delta
    
    def describe_to(self, description):
        description.append(f'datetime within {self.delta} of {self.expected}')
    
    def describe_mismatch(self, actual, mismatch_description):
        diff = abs(actual - self.expected)
        mismatch_description.append(f'was {actual} (diff: {diff})')

class HasLength(Matcher):
    """Matcher for sequence length."""
    
    def matches(self, actual):
        return len(actual) == self.expected
    
    def describe_to(self, description):
        description.append(f'sequence of length {self.expected}')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append(f'had length {len(actual)}')

class IsEmpty(Matcher):
    """Matcher for empty sequences."""
    
    def matches(self, actual):
        return len(actual) == 0
    
    def describe_to(self, description):
        description.append('empty sequence')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append(f'had length {len(actual)}')

class Contains(Matcher):
    """Matcher for sequence containment."""
    
    def matches(self, actual):
        return self.expected in actual
    
    def describe_to(self, description):
        description.append(f'sequence containing {self.expected}')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append(f'did not contain {self.expected}')

class IsInstance(Matcher):
    """Matcher for type checking."""
    
    def matches(self, actual):
        return isinstance(actual, self.expected)
    
    def describe_to(self, description):
        description.append(f'instance of {self.expected.__name__}')
    
    def describe_mismatch(self, actual, mismatch_description):
        mismatch_description.append(f'was instance of {type(actual).__name__}')

# Helper functions to create matchers
def is_html():
    return IsHTML(None)

def has_element(selector, text=None):
    return HasElement(selector, text)

def is_json():
    return IsJSON(None)

def has_keys(*keys):
    return HasKeys(keys)

def matches_regex(pattern):
    return MatchesRegex(pattern)

def is_within_delta(expected, delta):
    return IsWithinDelta(expected, delta)

def is_within_time_delta(expected, delta):
    return IsWithinTimeDelta(expected, delta)

def has_length(length):
    return HasLength(length)

def is_empty():
    return IsEmpty(None)

def contains(item):
    return Contains(item)

def is_instance_of(cls):
    return IsInstance(cls)
