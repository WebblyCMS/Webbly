# Test Automation Guide

## Overview

This guide provides instructions for automating the Webbly CMS test suite, including CI/CD integration, scheduled runs, and automated reporting.

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
      run: |
        pytest --cov=webbly --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### GitLab CI

#### Pipeline Configuration
```yaml
# .gitlab-ci.yml
test:
  image: python:3.9
  script:
    - pip install -r tests/requirements-test.txt
    - pytest --cov=webbly
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Automated Test Execution

### Test Runner Script
```python
#!/usr/bin/env python3
"""Automated test runner."""

import argparse
import subprocess
import sys

def run_tests(test_type='all', parallel=False, coverage=False):
    """Run specified tests."""
    cmd = ['pytest']
    
    if parallel:
        cmd.extend(['-n', 'auto'])
    
    if coverage:
        cmd.extend(['--cov=webbly', '--cov-report=html'])
    
    if test_type != 'all':
        cmd.append(f'tests/{test_type}/')
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default='all')
    parser.add_argument('--parallel', action='store_true')
    parser.add_argument('--coverage', action='store_true')
    
    args = parser.parse_args()
    sys.exit(run_tests(args.type, args.parallel, args.coverage))

if __name__ == '__main__':
    main()
```

### Scheduled Execution
```python
# scripts/schedule_tests.py
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=2)  # Run at 2 AM
def nightly_tests():
    """Run nightly test suite."""
    subprocess.run(['pytest', '--cov=webbly'])

@scheduler.scheduled_job('cron', day_of_week='mon')  # Run on Mondays
def weekly_full_suite():
    """Run full test suite weekly."""
    subprocess.run(['pytest', '--cov=webbly', '--runslow'])

scheduler.start()
```

## Automated Reporting

### Report Generator
```python
# scripts/generate_report.py
from datetime import datetime
import json

class TestReporter:
    """Generate test reports."""
    
    def __init__(self):
        self.timestamp = datetime.now()
    
    def generate_report(self, results):
        """Generate HTML report."""
        report = {
            'timestamp': self.timestamp.isoformat(),
            'results': results,
            'summary': self._generate_summary(results)
        }
        
        self._save_report(report)
    
    def _generate_summary(self, results):
        return {
            'total': len(results),
            'passed': sum(1 for r in results if r['status'] == 'passed'),
            'failed': sum(1 for r in results if r['status'] == 'failed')
        }
    
    def _save_report(self, report):
        filename = f'report_{self.timestamp:%Y%m%d_%H%M%S}.html'
        with open(filename, 'w') as f:
            # Generate HTML report
            pass
```

### Notification System
```python
# scripts/notify.py
import smtplib
from email.message import EmailMessage

def send_notification(report_data):
    """Send test report notification."""
    msg = EmailMessage()
    msg.set_content(f"""
    Test Report Summary:
    - Total: {report_data['total']}
    - Passed: {report_data['passed']}
    - Failed: {report_data['failed']}
    
    See attached report for details.
    """)
    
    msg['Subject'] = 'Test Report'
    msg['From'] = 'tests@webblycms.com'
    msg['To'] = 'team@webblycms.com'
    
    # Send email
    with smtplib.SMTP('smtp.example.com') as server:
        server.send_message(msg)
```

## Performance Monitoring

### Resource Monitor
```python
# scripts/monitor.py
import psutil
import time

class ResourceMonitor:
    """Monitor system resources during tests."""
    
    def __init__(self):
        self.start_time = None
        self.measurements = []
    
    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        self._record_measurement()
    
    def stop(self):
        """Stop monitoring."""
        self._record_measurement()
        return self.get_report()
    
    def _record_measurement(self):
        self.measurements.append({
            'timestamp': time.time(),
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        })
    
    def get_report(self):
        """Generate resource usage report."""
        return {
            'duration': time.time() - self.start_time,
            'measurements': self.measurements
        }
```

## Automated Maintenance

### Database Cleanup
```python
# scripts/cleanup.py
def cleanup_test_data():
    """Clean up test databases."""
    from webbly.models import db
    
    # Clean test database
    db.session.execute('DELETE FROM test_data WHERE created_at < NOW() - INTERVAL 7 DAY')
    db.session.commit()
```

### Log Rotation
```python
# scripts/rotate_logs.py
import logging
from logging.handlers import RotatingFileHandler

def setup_log_rotation():
    """Set up log rotation."""
    handler = RotatingFileHandler(
        'test.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    logging.getLogger().addHandler(handler)
```

## Integration Examples

### Jenkins Pipeline
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'python -m pytest'
            }
            post {
                always {
                    junit 'test-results/*.xml'
                }
            }
        }
    }
}
```

### Docker Compose
```yaml
# docker-compose.test.yml
version: '3'
services:
  tests:
    build: .
    command: pytest
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
```

## Best Practices

### Automation Guidelines
1. Keep scripts maintainable
2. Handle errors gracefully
3. Log important information
4. Clean up resources
5. Monitor performance

### Configuration Management
```python
# config/test_automation.py
CONFIG = {
    'schedule': {
        'nightly': '0 2 * * *',
        'weekly': '0 0 * * 1'
    },
    'reporting': {
        'email': ['team@webblycms.com'],
        'slack': '#testing-alerts'
    },
    'cleanup': {
        'data_retention_days': 7,
        'log_rotation_size': 1024*1024
    }
}
```

## Troubleshooting

### Common Issues
1. CI pipeline failures
2. Resource constraints
3. Timing issues
4. Configuration problems

### Solutions
1. Check logs
2. Monitor resources
3. Adjust timeouts
4. Verify configurations

Remember:
- Automate repetitive tasks
- Monitor execution
- Handle failures gracefully
- Maintain documentation
- Review regularly
