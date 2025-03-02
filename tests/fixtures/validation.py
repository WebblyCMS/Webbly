"""Test data validation utilities."""

import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationError:
    """Validation error details."""
    field: str
    message: str
    code: str

class Validator:
    """Base validator class."""
    
    def __init__(self, field: str, message: str = None):
        self.field = field
        self.message = message
    
    def validate(self, value: Any) -> Optional[ValidationError]:
        """Validate a value."""
        raise NotImplementedError

class RequiredValidator(Validator):
    """Validator for required fields."""
    
    def validate(self, value: Any) -> Optional[ValidationError]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationError(
                field=self.field,
                message=self.message or 'This field is required',
                code='required'
            )
        return None

class EmailValidator(Validator):
    """Validator for email addresses."""
    
    def validate(self, value: str) -> Optional[ValidationError]:
        if not value:
            return None
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return ValidationError(
                field=self.field,
                message=self.message or 'Invalid email address',
                code='invalid_email'
            )
        return None

class LengthValidator(Validator):
    """Validator for string length."""
    
    def __init__(self, field: str, min_length: int = None, max_length: int = None, message: str = None):
        super().__init__(field, message)
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: str) -> Optional[ValidationError]:
        if not value:
            return None
            
        if self.min_length and len(value) < self.min_length:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must be at least {self.min_length} characters',
                code='min_length'
            )
            
        if self.max_length and len(value) > self.max_length:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must be no more than {self.max_length} characters',
                code='max_length'
            )
        
        return None

class RegexValidator(Validator):
    """Validator for regex patterns."""
    
    def __init__(self, field: str, pattern: str, message: str = None):
        super().__init__(field, message)
        self.pattern = pattern
    
    def validate(self, value: str) -> Optional[ValidationError]:
        if not value:
            return None
            
        if not re.match(self.pattern, value):
            return ValidationError(
                field=self.field,
                message=self.message or 'Invalid format',
                code='invalid_format'
            )
        return None

class RangeValidator(Validator):
    """Validator for numeric ranges."""
    
    def __init__(self, field: str, min_value: Union[int, float] = None, 
                 max_value: Union[int, float] = None, message: str = None):
        super().__init__(field, message)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Union[int, float]) -> Optional[ValidationError]:
        if value is None:
            return None
            
        if self.min_value is not None and value < self.min_value:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must be at least {self.min_value}',
                code='min_value'
            )
            
        if self.max_value is not None and value > self.max_value:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must be no more than {self.max_value}',
                code='max_value'
            )
        
        return None

class DateValidator(Validator):
    """Validator for dates."""
    
    def __init__(self, field: str, min_date: datetime = None, 
                 max_date: datetime = None, message: str = None):
        super().__init__(field, message)
        self.min_date = min_date
        self.max_date = max_date
    
    def validate(self, value: datetime) -> Optional[ValidationError]:
        if not value:
            return None
            
        if self.min_date and value < self.min_date:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must be after {self.min_date}',
                code='min_date'
            )
            
        if self.max_date and value > self.max_date:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must be before {self.max_date}',
                code='max_date'
            )
        
        return None

class ListValidator(Validator):
    """Validator for lists."""
    
    def __init__(self, field: str, min_items: int = None, 
                 max_items: int = None, item_validator: Validator = None, 
                 message: str = None):
        super().__init__(field, message)
        self.min_items = min_items
        self.max_items = max_items
        self.item_validator = item_validator
    
    def validate(self, value: List[Any]) -> Optional[ValidationError]:
        if not value:
            return None
            
        if self.min_items and len(value) < self.min_items:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must have at least {self.min_items} items',
                code='min_items'
            )
            
        if self.max_items and len(value) > self.max_items:
            return ValidationError(
                field=self.field,
                message=self.message or f'Must have no more than {self.max_items} items',
                code='max_items'
            )
        
        if self.item_validator:
            for item in value:
                error = self.item_validator.validate(item)
                if error:
                    return error
        
        return None

class SchemaValidator:
    """Validator for data schemas."""
    
    def __init__(self, schema: Dict[str, List[Validator]]):
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate data against schema."""
        errors = []
        
        for field, validators in self.schema.items():
            value = data.get(field)
            
            for validator in validators:
                error = validator.validate(value)
                if error:
                    errors.append(error)
                    break
        
        return errors

def validate_user_data(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate user data."""
    schema = {
        'username': [
            RequiredValidator('username'),
            LengthValidator('username', min_length=3, max_length=30),
            RegexValidator('username', r'^[a-zA-Z0-9_]+$', 'Username can only contain letters, numbers, and underscores')
        ],
        'email': [
            RequiredValidator('email'),
            EmailValidator('email')
        ],
        'password': [
            RequiredValidator('password'),
            LengthValidator('password', min_length=8),
            RegexValidator('password', r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]+$', 
                         'Password must contain at least one letter and one number')
        ]
    }
    
    validator = SchemaValidator(schema)
    return validator.validate(data)

def validate_post_data(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate post data."""
    schema = {
        'title': [
            RequiredValidator('title'),
            LengthValidator('title', max_length=200)
        ],
        'content': [
            RequiredValidator('content')
        ],
        'excerpt': [
            LengthValidator('excerpt', max_length=500)
        ]
    }
    
    validator = SchemaValidator(schema)
    return validator.validate(data)

def validate_comment_data(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate comment data."""
    schema = {
        'content': [
            RequiredValidator('content'),
            LengthValidator('content', max_length=1000)
        ]
    }
    
    validator = SchemaValidator(schema)
    return validator.validate(data)
