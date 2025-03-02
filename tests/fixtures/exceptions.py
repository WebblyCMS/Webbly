"""Custom test exceptions and error handling."""

class TestError(Exception):
    """Base class for test exceptions."""
    pass

class TestSetupError(TestError):
    """Exception raised when test setup fails."""
    
    def __init__(self, message, component=None):
        self.component = component
        super().__init__(f"Test setup failed{f' in {component}' if component else ''}: {message}")

class TestTeardownError(TestError):
    """Exception raised when test teardown fails."""
    
    def __init__(self, message, component=None):
        self.component = component
        super().__init__(f"Test teardown failed{f' in {component}' if component else ''}: {message}")

class TestDataError(TestError):
    """Exception raised when test data is invalid or missing."""
    
    def __init__(self, message, data=None):
        self.data = data
        super().__init__(f"Test data error: {message}")

class TestAssertionError(TestError):
    """Exception raised when a test assertion fails."""
    
    def __init__(self, message, expected=None, actual=None):
        self.expected = expected
        self.actual = actual
        if expected is not None and actual is not None:
            message = f"{message}\nExpected: {expected}\nActual: {actual}"
        super().__init__(message)

class TestTimeoutError(TestError):
    """Exception raised when a test operation times out."""
    
    def __init__(self, message, timeout=None):
        self.timeout = timeout
        super().__init__(f"Operation timed out{f' after {timeout} seconds' if timeout else ''}: {message}")

class TestDependencyError(TestError):
    """Exception raised when a test dependency is missing."""
    
    def __init__(self, message, dependency=None):
        self.dependency = dependency
        super().__init__(f"Missing dependency{f' {dependency}' if dependency else ''}: {message}")

class TestConfigurationError(TestError):
    """Exception raised when test configuration is invalid."""
    
    def __init__(self, message, config_key=None):
        self.config_key = config_key
        super().__init__(f"Configuration error{f' for {config_key}' if config_key else ''}: {message}")

class TestEnvironmentError(TestError):
    """Exception raised when test environment is invalid."""
    
    def __init__(self, message, env_var=None):
        self.env_var = env_var
        super().__init__(f"Environment error{f' for {env_var}' if env_var else ''}: {message}")

class TestResourceError(TestError):
    """Exception raised when a test resource is unavailable."""
    
    def __init__(self, message, resource=None):
        self.resource = resource
        super().__init__(f"Resource error{f' for {resource}' if resource else ''}: {message}")

class TestValidationError(TestError):
    """Exception raised when test validation fails."""
    
    def __init__(self, message, errors=None):
        self.errors = errors or {}
        if errors:
            message = f"{message}\nValidation errors: {errors}"
        super().__init__(message)

class TestCleanupError(TestError):
    """Exception raised when test cleanup fails."""
    
    def __init__(self, message, resources=None):
        self.resources = resources or []
        if resources:
            message = f"{message}\nFailed to clean up: {resources}"
        super().__init__(message)

class TestFixtureError(TestError):
    """Exception raised when a test fixture fails."""
    
    def __init__(self, message, fixture=None):
        self.fixture = fixture
        super().__init__(f"Fixture error{f' in {fixture}' if fixture else ''}: {message}")

class TestParameterError(TestError):
    """Exception raised when test parameters are invalid."""
    
    def __init__(self, message, parameter=None):
        self.parameter = parameter
        super().__init__(f"Parameter error{f' for {parameter}' if parameter else ''}: {message}")

class TestStateError(TestError):
    """Exception raised when test state is invalid."""
    
    def __init__(self, message, state=None):
        self.state = state
        if state:
            message = f"{message}\nCurrent state: {state}"
        super().__init__(message)

def handle_test_error(func):
    """Decorator to handle test errors."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TestError as e:
            print(f"\nTest error occurred: {str(e)}")
            raise
        except Exception as e:
            print(f"\nUnexpected error occurred: {str(e)}")
            raise TestError(f"Unexpected error in {func.__name__}: {str(e)}") from e
    return wrapper

def assert_raises_with_message(exception_class, message):
    """Context manager to assert that an exception is raised with a specific message."""
    from contextlib import contextmanager
    
    @contextmanager
    def context():
        try:
            yield
            raise AssertionError(f"Expected {exception_class.__name__} to be raised")
        except exception_class as e:
            assert str(e) == message, f"Expected message '{message}' but got '{str(e)}'"
    
    return context()

def assert_not_raises(exception_class):
    """Context manager to assert that an exception is not raised."""
    from contextlib import contextmanager
    
    @contextmanager
    def context():
        try:
            yield
        except exception_class as e:
            raise AssertionError(f"Expected no {exception_class.__name__} but got: {str(e)}")
    
    return context()
