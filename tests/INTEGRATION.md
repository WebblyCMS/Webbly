# Test Suite Integration Guide

## Overview

This guide explains how to integrate the Webbly CMS test suite with various tools, services, and platforms.

## CI/CD Integration

### GitHub Actions

#### Basic Workflow
```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10"]

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r tests/requirements-test.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://test:test@localhost:5432/test_db
      run: |
        pytest --cov=webbly --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### GitLab CI

#### Pipeline Configuration
```yaml
# .gitlab-ci.yml
image: python:3.9

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: test
  POSTGRES_PASSWORD: test
  DATABASE_URL: postgresql://test:test@postgres:5432/test_db

services:
  - postgres:13

stages:
  - test
  - report

test:
  stage: test
  script:
    - pip install -r tests/requirements-test.txt
    - pytest --cov=webbly --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Code Coverage Integration

### Codecov

#### Configuration
```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 90%
    patch:
      default:
        target: 95%

ignore:
  - "tests/**/*"
  - "setup.py"
```

### SonarQube

#### Configuration
```yaml
# sonar-project.properties
sonar.projectKey=webbly-cms
sonar.sources=webbly
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml
```

## Database Integration

### PostgreSQL

#### Connection Setup
```python
# tests/fixtures/database.py
import pytest
from sqlalchemy import create_engine

@pytest.fixture(scope='session')
def database():
    """Set up test database."""
    engine = create_engine(
        os.getenv('DATABASE_URL'),
        pool_size=5,
        max_overflow=10
    )
    
    # Create tables
    from webbly.models import Base
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(engine)
```

### Redis

#### Cache Integration
```python
# tests/fixtures/cache.py
import pytest
import redis

@pytest.fixture(scope='session')
def redis_client():
    """Set up Redis client."""
    client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0))
    )
    
    yield client
    
    # Clean up
    client.flushdb()
```

## Email Integration

### SMTP

#### Email Testing
```python
# tests/fixtures/mail.py
import smtplib
from email.message import EmailMessage

class TestMailer:
    """Test email functionality."""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def send_test_email(self, to_addr, subject, content):
        """Send test email."""
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = 'test@example.com'
        msg['To'] = to_addr
        
        with smtplib.SMTP(self.host, self.port) as server:
            server.send_message(msg)
```

### MailHog

#### Configuration
```yaml
# docker-compose.test.yml
services:
  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI
```

## Browser Integration

### Selenium

#### WebDriver Setup
```python
# tests/fixtures/browser.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope='function')
def browser():
    """Set up browser for testing."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()
```

### Playwright

#### Browser Testing
```python
# tests/fixtures/playwright.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope='function')
def page():
    """Set up Playwright page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        yield page
        
        browser.close()
```

## Monitoring Integration

### Prometheus

#### Metrics Export
```python
# tests/monitoring/metrics.py
from prometheus_client import Counter, Histogram

TEST_RUNS = Counter(
    'test_runs_total',
    'Total number of test runs'
)

TEST_DURATION = Histogram(
    'test_duration_seconds',
    'Test execution duration'
)
```

### Grafana

#### Dashboard Configuration
```json
{
  "dashboard": {
    "title": "Test Metrics",
    "panels": [
      {
        "title": "Test Execution Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(test_duration_seconds_sum[5m])"
          }
        ]
      }
    ]
  }
}
```

## Logging Integration

### ELK Stack

#### Logstash Configuration
```yaml
# logstash.conf
input {
  file {
    path => "/path/to/test.log"
    type => "test_logs"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "test-logs-%{+YYYY.MM.dd}"
  }
}
```

## Best Practices

### Integration Guidelines
1. Use configuration files
2. Handle credentials securely
3. Clean up resources
4. Document dependencies
5. Test integrations

### Security Considerations
1. Secure credentials
2. Use test environments
3. Limit permissions
4. Monitor access
5. Regular audits

Remember:
- Test integrations
- Document setup
- Handle errors
- Clean up resources
- Monitor usage
