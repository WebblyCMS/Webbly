# Test Coverage Guide

## Overview

This guide explains how to measure, analyze, and maintain test coverage in the Webbly CMS test suite.

## Coverage Configuration

### pytest Configuration

#### pytest.ini
```ini
[pytest]
# Coverage settings
addopts = 
    --cov=webbly
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    --cov-branch
    --cov-fail-under=90
```

### Coverage Configuration

#### .coveragerc
```ini
[run]
source = webbly
omit =
    */tests/*
    */migrations/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass

[html]
directory = coverage_html
title = Webbly CMS Test Coverage Report
```

## Coverage Measurement

### Basic Coverage

#### Running Coverage
```bash
# Run tests with coverage
pytest --cov=webbly

# Generate HTML report
pytest --cov=webbly --cov-report=html

# Generate XML report
pytest --cov=webbly --cov-report=xml
```

### Advanced Coverage

#### Coverage Types
```python
# Branch coverage example
def function_with_branches(value):
    """Function with multiple branches."""
    if value > 0:  # pragma: no branch
        return "positive"
    elif value < 0:
        return "negative"
    else:
        return "zero"

# Path coverage example
def function_with_paths(a, b):
    """Function with multiple paths."""
    if a:
        if b:
            return "both"
        return "a only"
    if b:
        return "b only"
    return "none"
```

## Coverage Analysis

### Coverage Reports

#### HTML Report Analysis
```python
class CoverageAnalyzer:
    """Analyze coverage reports."""
    
    def analyze_html_report(self, report_dir):
        """Analyze HTML coverage report."""
        results = {
            'total_coverage': 0,
            'uncovered_lines': [],
            'partially_covered': [],
            'missing_modules': []
        }
        
        # Analysis implementation
        return results
```

### Coverage Metrics

#### Coverage Calculator
```python
class CoverageCalculator:
    """Calculate coverage metrics."""
    
    def calculate_metrics(self, coverage_data):
        """Calculate coverage metrics."""
        return {
            'line_coverage': self._calculate_line_coverage(coverage_data),
            'branch_coverage': self._calculate_branch_coverage(coverage_data),
            'path_coverage': self._calculate_path_coverage(coverage_data)
        }
    
    def _calculate_line_coverage(self, data):
        """Calculate line coverage percentage."""
        covered = data['covered_lines']
        total = data['total_lines']
        return (covered / total * 100) if total > 0 else 0
```

## Coverage Maintenance

### Coverage Tracking

#### Coverage History
```python
class CoverageTracker:
    """Track coverage history."""
    
    def __init__(self, history_file):
        self.history_file = history_file
        self.history = self._load_history()
    
    def add_coverage(self, coverage_data):
        """Add new coverage data."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'coverage': coverage_data,
            'commit': self._get_current_commit()
        }
        self.history.append(entry)
        self._save_history()
```

### Coverage Goals

#### Coverage Requirements
```python
class CoverageRequirements:
    """Define coverage requirements."""
    
    REQUIREMENTS = {
        'total': 90,
        'critical_modules': 95,
        'new_code': 100
    }
    
    def check_requirements(self, coverage_data):
        """Check if coverage meets requirements."""
        results = {
            'passed': True,
            'failures': []
        }
        
        if coverage_data['total'] < self.REQUIREMENTS['total']:
            results['passed'] = False
            results['failures'].append(
                f"Total coverage {coverage_data['total']}% below required {self.REQUIREMENTS['total']}%"
            )
        
        return results
```

## Coverage Tools

### Custom Tools

#### Coverage Diff Tool
```python
class CoverageDiff:
    """Compare coverage between versions."""
    
    def compare_coverage(self, old_data, new_data):
        """Compare coverage data."""
        return {
            'changed': self._find_changed_coverage(old_data, new_data),
            'new': self._find_new_coverage(old_data, new_data),
            'removed': self._find_removed_coverage(old_data, new_data)
        }
    
    def _find_changed_coverage(self, old, new):
        """Find modules with changed coverage."""
        changed = {}
        for module in set(old.keys()) & set(new.keys()):
            if old[module] != new[module]:
                changed[module] = {
                    'old': old[module],
                    'new': new[module],
                    'diff': new[module] - old[module]
                }
        return changed
```

### Integration Tools

#### CI Integration
```yaml
# .github/workflows/coverage.yml
name: Coverage

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Run coverage
        run: |
          pip install -r requirements-test.txt
          pytest --cov=webbly --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Coverage Reporting

### Report Generation

#### Report Generator
```python
class CoverageReporter:
    """Generate coverage reports."""
    
    def generate_report(self, coverage_data, format='html'):
        """Generate coverage report."""
        if format == 'html':
            return self._generate_html_report(coverage_data)
        elif format == 'markdown':
            return self._generate_markdown_report(coverage_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, data):
        """Generate HTML coverage report."""
        template = """
        <html>
            <head>
                <title>Coverage Report</title>
            </head>
            <body>
                <h1>Coverage Report</h1>
                <p>Total Coverage: {total_coverage}%</p>
                <!-- More report content -->
            </body>
        </html>
        """
        return template.format(total_coverage=data['total'])
```

## Best Practices

### Coverage Guidelines
1. Set realistic goals
2. Focus on critical code
3. Update regularly
4. Review changes
5. Document exclusions

### Implementation Tips
1. Use appropriate tools
2. Monitor trends
3. Address gaps
4. Maintain history
5. Regular reviews

Remember:
- Coverage isn't everything
- Focus on quality
- Test critical paths
- Document decisions
- Regular updates
