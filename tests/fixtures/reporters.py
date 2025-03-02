"""Custom test reporters and result formatting."""

import os
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from pytest import Item, TestReport

@dataclass
class TestResult:
    """Test result data class."""
    name: str
    outcome: str
    duration: float
    error: str = None
    stdout: str = None
    stderr: str = None
    markers: List[str] = None

class BaseReporter:
    """Base class for custom test reporters."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time: datetime = None
        self.end_time: datetime = None
    
    def start(self):
        """Called when testing starts."""
        self.start_time = datetime.now()
    
    def finish(self):
        """Called when testing finishes."""
        self.end_time = datetime.now()
    
    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary statistics."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.outcome == 'passed')
        failed = sum(1 for r in self.results if r.outcome == 'failed')
        skipped = sum(1 for r in self.results if r.outcome == 'skipped')
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': duration
        }

class ConsoleReporter(BaseReporter):
    """Reporter that outputs to console."""
    
    def __init__(self, show_output=True):
        super().__init__()
        self.show_output = show_output
    
    def start(self):
        super().start()
        print("\nStarting test run...")
    
    def finish(self):
        super().finish()
        summary = self.get_summary()
        
        print("\nTest Run Summary")
        print("=" * 80)
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Duration: {summary['duration']:.2f}s")
        
        if summary['failed'] > 0:
            print("\nFailed Tests:")
            print("-" * 80)
            for result in self.results:
                if result.outcome == 'failed':
                    print(f"\n{result.name}")
                    print(f"Error: {result.error}")
                    if self.show_output and result.stdout:
                        print("\nStandard Output:")
                        print(result.stdout)
                    if self.show_output and result.stderr:
                        print("\nStandard Error:")
                        print(result.stderr)

class HTMLReporter(BaseReporter):
    """Reporter that generates HTML report."""
    
    def __init__(self, output_dir='test-reports'):
        super().__init__()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def finish(self):
        super().finish()
        self._generate_report()
    
    def _generate_report(self):
        """Generate HTML report."""
        summary = self.get_summary()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(self.output_dir, f'test_report_{timestamp}.html')
        
        with open(filename, 'w') as f:
            f.write(self._get_html_content(summary))
        
        print(f"\nHTML report generated: {filename}")
    
    def _get_html_content(self, summary):
        """Generate HTML content."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ margin-bottom: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        .test-result {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; }}
        .error {{ background-color: #ffebee; padding: 10px; margin-top: 5px; }}
        .output {{ background-color: #f5f5f5; padding: 10px; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {summary['total']}</p>
        <p class="passed">Passed: {summary['passed']}</p>
        <p class="failed">Failed: {summary['failed']}</p>
        <p class="skipped">Skipped: {summary['skipped']}</p>
        <p>Duration: {summary['duration']:.2f}s</p>
    </div>
    
    <h2>Test Results</h2>
    {self._get_test_results_html()}
</body>
</html>
"""
    
    def _get_test_results_html(self):
        """Generate HTML for test results."""
        html = []
        for result in self.results:
            html.append(f"""
            <div class="test-result">
                <h3>{result.name} <span class="{result.outcome}">{result.outcome}</span></h3>
                <p>Duration: {result.duration:.2f}s</p>
                {f'<div class="error">Error: {result.error}</div>' if result.error else ''}
                {f'<div class="output">Output: {result.stdout}</div>' if result.stdout else ''}
            </div>
            """)
        return '\n'.join(html)

class JUnitReporter(BaseReporter):
    """Reporter that generates JUnit XML report."""
    
    def __init__(self, output_dir='test-reports'):
        super().__init__()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def finish(self):
        super().finish()
        self._generate_report()
    
    def _generate_report(self):
        """Generate JUnit XML report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(self.output_dir, f'junit_{timestamp}.xml')
        
        with open(filename, 'w') as f:
            f.write(self._get_junit_content())
        
        print(f"\nJUnit report generated: {filename}")
    
    def _get_junit_content(self):
        """Generate JUnit XML content."""
        summary = self.get_summary()
        
        xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuites time="{summary["duration"]:.2f}" tests="{summary["total"]}" failures="{summary["failed"]}" skipped="{summary["skipped"]}">'
        ]
        
        for result in self.results:
            xml.append(f"""
            <testcase name="{result.name}" time="{result.duration:.2f}">
                {f'<failure message="{result.error}"></failure>' if result.outcome == 'failed' else ''}
                {f'<skipped></skipped>' if result.outcome == 'skipped' else ''}
                {f'<system-out>{result.stdout}</system-out>' if result.stdout else ''}
                {f'<system-err>{result.stderr}</system-err>' if result.stderr else ''}
            </testcase>
            """)
        
        xml.append('</testsuites>')
        return '\n'.join(xml)

def pytest_configure(config):
    """Configure pytest with custom reporters."""
    config.option.htmlpath = os.path.join('test-reports', 'report.html')
    config.option.junitxml = os.path.join('test-reports', 'junit.xml')
    
    # Register reporters
    config._reporters = {
        'console': ConsoleReporter(),
        'html': HTMLReporter(),
        'junit': JUnitReporter()
    }

def pytest_runtest_logreport(report: TestReport):
    """Process test reports."""
    for reporter in pytest.config._reporters.values():
        if report.when == 'call' or (report.when == 'setup' and report.skipped):
            result = TestResult(
                name=report.nodeid,
                outcome=report.outcome,
                duration=report.duration,
                error=str(report.longrepr) if report.failed else None,
                stdout=report.capstdout,
                stderr=report.capstderr,
                markers=[marker.name for marker in report.keywords.get('pytestmark', [])]
            )
            reporter.add_result(result)

def pytest_sessionstart():
    """Called before test session starts."""
    for reporter in pytest.config._reporters.values():
        reporter.start()

def pytest_sessionfinish():
    """Called after test session finishes."""
    for reporter in pytest.config._reporters.values():
        reporter.finish()
