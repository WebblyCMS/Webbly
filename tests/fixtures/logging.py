"""Test logging and output formatting utilities."""

import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager

from .config import TEST_LOGGING, get_test_paths

@dataclass
class TestLogRecord:
    """Test log record data."""
    timestamp: datetime
    level: str
    message: str
    test_name: Optional[str] = None
    test_phase: Optional[str] = None
    error: Optional[Exception] = None
    context: Optional[Dict[str, Any]] = None

class TestLogger:
    """Custom test logger."""
    
    def __init__(self, log_file: str = None, level: str = 'INFO'):
        self.log_file = log_file or TEST_LOGGING['LOG_FILE']
        self.level = getattr(logging, level.upper())
        self.logger = self._setup_logger()
        self.current_test = None
        self.current_phase = None
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        # Create logger
        logger = logging.getLogger('test_logger')
        logger.setLevel(self.level)
        
        # Create directory if needed
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(logging.Formatter(TEST_LOGGING['LOG_FORMAT']))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(logging.Formatter(TEST_LOGGING['LOG_FORMAT']))
        logger.addHandler(console_handler)
        
        return logger
    
    def set_test(self, test_name: str):
        """Set current test name."""
        self.current_test = test_name
        self.log('info', f"Starting test: {test_name}")
    
    def set_phase(self, phase: str):
        """Set current test phase."""
        self.current_phase = phase
        self.log('info', f"Test phase: {phase}")
    
    def log(self, level: str, message: str, error: Exception = None, context: Dict[str, Any] = None):
        """Log a message with context."""
        record = TestLogRecord(
            timestamp=datetime.now(),
            level=level.upper(),
            message=message,
            test_name=self.current_test,
            test_phase=self.current_phase,
            error=error,
            context=context
        )
        
        log_message = self._format_record(record)
        getattr(self.logger, level.lower())(log_message)
        
        if error:
            self.logger.error(traceback.format_exc())
    
    def _format_record(self, record: TestLogRecord) -> str:
        """Format log record."""
        parts = []
        
        # Add test name and phase if available
        if record.test_name:
            parts.append(f"[{record.test_name}]")
        if record.test_phase:
            parts.append(f"({record.test_phase})")
        
        # Add message
        parts.append(record.message)
        
        # Add error if available
        if record.error:
            parts.append(f"Error: {str(record.error)}")
        
        # Add context if available
        if record.context:
            parts.append(f"Context: {record.context}")
        
        return " ".join(parts)
    
    def clear(self):
        """Clear log file."""
        with open(self.log_file, 'w'):
            pass

class TestOutput:
    """Test output formatter."""
    
    def __init__(self, show_timestamps: bool = True, show_colors: bool = True):
        self.show_timestamps = show_timestamps
        self.show_colors = show_colors and sys.stdout.isatty()
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'reset': '\033[0m'
        }
    
    def format(self, message: str, color: str = None, timestamp: bool = None) -> str:
        """Format output message."""
        parts = []
        
        # Add timestamp if enabled
        if (timestamp or self.show_timestamps) and timestamp is not False:
            parts.append(f"[{datetime.now().strftime('%H:%M:%S')}]")
        
        # Add color if enabled
        if self.show_colors and color and color in self.colors:
            message = f"{self.colors[color]}{message}{self.colors['reset']}"
        
        parts.append(message)
        return " ".join(parts)
    
    def success(self, message: str, **kwargs):
        """Print success message."""
        print(self.format(message, color='green', **kwargs))
    
    def error(self, message: str, **kwargs):
        """Print error message."""
        print(self.format(message, color='red', **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Print warning message."""
        print(self.format(message, color='yellow', **kwargs))
    
    def info(self, message: str, **kwargs):
        """Print info message."""
        print(self.format(message, color='blue', **kwargs))
    
    def debug(self, message: str, **kwargs):
        """Print debug message."""
        print(self.format(message, color='magenta', **kwargs))

@contextmanager
def log_test(name: str):
    """Context manager for test logging."""
    logger = TestLogger()
    logger.set_test(name)
    try:
        yield logger
    finally:
        logger.set_test(None)
        logger.set_phase(None)

@contextmanager
def log_phase(phase: str):
    """Context manager for test phase logging."""
    logger = TestLogger()
    logger.set_phase(phase)
    try:
        yield logger
    finally:
        logger.set_phase(None)

def setup_test_logging():
    """Set up test logging."""
    return TestLogger()

def setup_test_output():
    """Set up test output."""
    return TestOutput()

# Global instances
logger = setup_test_logging()
output = setup_test_output()
