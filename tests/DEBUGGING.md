# Test Debugging Guide

## Overview

This guide provides strategies and tools for debugging tests in the Webbly CMS test suite.

## Basic Debugging

### Using pdb

#### Interactive Debugging
```python
def test_problematic_feature():
    """Test with interactive debugging."""
    # Add breakpoint
    import pdb; pdb.set_trace()
    
    result = feature_under_test()
    assert result.is_valid

# Common pdb commands:
# n (next line)
# s (step into)
# c (continue)
# p variable (print variable)
# l (list source)
# q (quit)
```

### Using pytest.set_trace()

#### pytest Debugging
```python
def test_with_pytest_debugger():
    """Test with pytest debugger."""
    data = prepare_test_data()
    
    # Add pytest breakpoint
    pytest.set_trace()
    
    result = process_data(data)
    assert result.success
```

## Advanced Debugging

### Custom Debug Tools

#### Debug Helper
```python
class DebugHelper:
    """Helper for debugging tests."""
    
    def __init__(self):
        self.logs = []
    
    def log_state(self, **kwargs):
        """Log current state."""
        state = {
            'timestamp': datetime.now(),
            'data': kwargs
        }
        self.logs.append(state)
    
    def print_logs(self):
        """Print debug logs."""
        for log in self.logs:
            print(f"[{log['timestamp']}]")
            for key, value in log['data'].items():
                print(f"  {key}: {value}")
```

### Context Managers

#### Debug Context
```python
@contextmanager
def debug_context():
    """Context manager for debugging."""
    start_time = time.time()
    debug_info = {'events': []}
    
    try:
        yield debug_info
    finally:
        duration = time.time() - start_time
        print(f"Debug session duration: {duration:.2f}s")
        print("Events:")
        for event in debug_info['events']:
            print(f"- {event}")
```

## Test State Analysis

### State Inspection

#### State Inspector
```python
class StateInspector:
    """Inspect test state."""
    
    def inspect_object(self, obj):
        """Inspect object state."""
        return {
            'type': type(obj).__name__,
            'attributes': self._get_attributes(obj),
            'methods': self._get_methods(obj)
        }
    
    def _get_attributes(self, obj):
        """Get object attributes."""
        return {
            name: getattr(obj, name)
            for name in dir(obj)
            if not name.startswith('_') and not callable(getattr(obj, name))
        }
```

### Variable Tracking

#### Variable Tracker
```python
class VariableTracker:
    """Track variable changes."""
    
    def __init__(self):
        self.history = defaultdict(list)
    
    def track(self, name, value):
        """Track variable value."""
        self.history[name].append({
            'value': value,
            'timestamp': datetime.now()
        })
    
    def get_history(self, name):
        """Get variable history."""
        return self.history.get(name, [])
```

## Error Analysis

### Error Inspection

#### Error Inspector
```python
class ErrorInspector:
    """Inspect test errors."""
    
    def inspect_error(self, error):
        """Analyze error details."""
        return {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': self._format_traceback(error),
            'context': self._get_error_context(error)
        }
    
    def _format_traceback(self, error):
        """Format error traceback."""
        import traceback
        return ''.join(traceback.format_tb(error.__traceback__))
```

### Stack Trace Analysis

#### Stack Analyzer
```python
class StackAnalyzer:
    """Analyze stack traces."""
    
    def analyze_stack(self, stack_trace):
        """Analyze stack trace."""
        frames = []
        for frame in stack_trace.split('\n'):
            if frame.strip():
                frames.append(self._analyze_frame(frame))
        return frames
    
    def _analyze_frame(self, frame):
        """Analyze single stack frame."""
        # Frame analysis implementation
        pass
```

## Logging and Output

### Debug Logging

#### Debug Logger
```python
class DebugLogger:
    """Enhanced debug logging."""
    
    def __init__(self):
        self.logger = logging.getLogger('debug')
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up debug logger."""
        handler = logging.FileHandler('debug.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
```

### Output Capture

#### Output Capturer
```python
@contextmanager
def capture_output():
    """Capture stdout and stderr."""
    stdout = StringIO()
    stderr = StringIO()
    
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield {
            'stdout': stdout,
            'stderr': stderr
        }
```

## Memory Analysis

### Memory Tracking

#### Memory Tracker
```python
class MemoryTracker:
    """Track memory usage."""
    
    def __init__(self):
        self.snapshots = []
    
    def take_snapshot(self):
        """Take memory snapshot."""
        import tracemalloc
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append({
            'timestamp': datetime.now(),
            'snapshot': snapshot
        })
    
    def compare_snapshots(self, snapshot1, snapshot2):
        """Compare memory snapshots."""
        stats = snapshot2.compare_to(snapshot1, 'lineno')
        return [
            {
                'file': stat.traceback[0].filename,
                'line': stat.traceback[0].lineno,
                'size_diff': stat.size_diff
            }
            for stat in stats
        ]
```

## Best Practices

### Debugging Guidelines
1. Use appropriate tools
2. Log relevant information
3. Isolate issues
4. Document findings
5. Clean up debug code

### Implementation Tips
1. Add debug points strategically
2. Use descriptive logging
3. Track state changes
4. Monitor resources
5. Clean up resources

Remember:
- Debug systematically
- Document findings
- Clean up debug code
- Share knowledge
- Learn from issues
