"""Test profiling and performance analysis utilities."""

import os
import time
import cProfile
import pstats
import io
import psutil
import tracemalloc
from functools import wraps
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class ProfileResult:
    """Profile result data."""
    name: str
    start_time: datetime
    end_time: datetime
    duration: float
    memory_start: int
    memory_end: int
    memory_diff: int
    cpu_percent: float
    calls: int
    function_stats: Dict[str, Any]

class Profiler:
    """Performance profiler."""
    
    def __init__(self, name: str):
        self.name = name
        self.process = psutil.Process()
        self.profile = cProfile.Profile()
        self.start_time = None
        self.end_time = None
        self.memory_start = None
        self.memory_end = None
        self.cpu_start = None
        self.cpu_end = None
    
    def start(self):
        """Start profiling."""
        self.start_time = datetime.now()
        self.memory_start = self.process.memory_info().rss
        self.cpu_start = self.process.cpu_percent()
        self.profile.enable()
        tracemalloc.start()
    
    def stop(self) -> ProfileResult:
        """Stop profiling and return results."""
        self.profile.disable()
        snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        self.end_time = datetime.now()
        self.memory_end = self.process.memory_info().rss
        self.cpu_end = self.process.cpu_percent()
        
        # Get function statistics
        s = io.StringIO()
        ps = pstats.Stats(self.profile, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        return ProfileResult(
            name=self.name,
            start_time=self.start_time,
            end_time=self.end_time,
            duration=(self.end_time - self.start_time).total_seconds(),
            memory_start=self.memory_start,
            memory_end=self.memory_end,
            memory_diff=self.memory_end - self.memory_start,
            cpu_percent=self.cpu_end - self.cpu_start,
            calls=len(self.profile.getstats()),
            function_stats=self._parse_stats(s.getvalue())
        )
    
    def _parse_stats(self, stats_str: str) -> Dict[str, Any]:
        """Parse profiler statistics."""
        lines = stats_str.split('\n')
        stats = {}
        
        for line in lines[3:]:  # Skip header lines
            if line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    stats[parts[5]] = {
                        'calls': int(parts[0]),
                        'time_per_call': float(parts[1]),
                        'total_time': float(parts[2]),
                        'cumulative_time': float(parts[3])
                    }
        
        return stats

def profile(name: str = None):
    """Decorator to profile a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = Profiler(name or func.__name__)
            profiler.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profile_result = profiler.stop()
                save_profile_result(profile_result)
        return wrapper
    return decorator

class PerformanceAnalyzer:
    """Analyze performance results."""
    
    def __init__(self):
        self.results: List[ProfileResult] = []
    
    def add_result(self, result: ProfileResult):
        """Add a profile result."""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.results:
            return {}
        
        return {
            'total_tests': len(self.results),
            'total_duration': sum(r.duration for r in self.results),
            'avg_duration': sum(r.duration for r in self.results) / len(self.results),
            'total_memory': sum(r.memory_diff for r in self.results),
            'avg_memory': sum(r.memory_diff for r in self.results) / len(self.results),
            'avg_cpu': sum(r.cpu_percent for r in self.results) / len(self.results),
            'slowest_test': max(self.results, key=lambda r: r.duration).name,
            'highest_memory': max(self.results, key=lambda r: r.memory_diff).name
        }
    
    def generate_report(self, output_file: str = None):
        """Generate performance report."""
        if not output_file:
            output_file = TEST_REPORTS_DIR / f'performance_{datetime.now():%Y%m%d_%H%M%S}.html'
        
        summary = self.get_summary()
        
        with open(output_file, 'w') as f:
            f.write(self._generate_html_report(summary))
        
        logger.info(f"Performance report generated: {output_file}")
    
    def _generate_html_report(self, summary: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ margin-bottom: 20px; }}
                .test-result {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Performance Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {summary['total_tests']}</p>
                <p>Total Duration: {summary['total_duration']:.2f}s</p>
                <p>Average Duration: {summary['avg_duration']:.2f}s</p>
                <p>Total Memory: {summary['total_memory'] / 1024 / 1024:.2f}MB</p>
                <p>Average Memory: {summary['avg_memory'] / 1024 / 1024:.2f}MB</p>
                <p>Average CPU: {summary['avg_cpu']:.2f}%</p>
                <p>Slowest Test: {summary['slowest_test']}</p>
                <p>Highest Memory Usage: {summary['highest_memory']}</p>
            </div>
            
            <div class="results">
                <h2>Test Results</h2>
                {self._generate_test_results_html()}
            </div>
        </body>
        </html>
        """
    
    def _generate_test_results_html(self) -> str:
        """Generate HTML for test results."""
        html = []
        for result in sorted(self.results, key=lambda r: r.duration, reverse=True):
            html.append(f"""
            <div class="test-result">
                <h3>{result.name}</h3>
                <p>Duration: {result.duration:.2f}s</p>
                <p>Memory Usage: {result.memory_diff / 1024 / 1024:.2f}MB</p>
                <p>CPU Usage: {result.cpu_percent:.2f}%</p>
                <p>Function Calls: {result.calls}</p>
            </div>
            """)
        return '\n'.join(html)

def save_profile_result(result: ProfileResult):
    """Save profile result to analyzer."""
    analyzer = PerformanceAnalyzer()
    analyzer.add_result(result)
    return analyzer

# Global analyzer instance
analyzer = PerformanceAnalyzer()
