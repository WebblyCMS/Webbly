"""Performance testing utilities and benchmarks."""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from statistics import mean, median, stdev
import matplotlib.pyplot as plt
import numpy as np

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    duration: float
    memory_usage: int
    cpu_usage: float
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None

class LoadGenerator:
    """Load generator for performance testing."""
    
    def __init__(self, target: Callable, users: int = 1, 
                 ramp_up: int = 0, duration: int = 60):
        self.target = target
        self.users = users
        self.ramp_up = ramp_up
        self.duration = duration
        self.metrics: List[PerformanceMetric] = []
        self.running = False
        self.threads: List[threading.Thread] = []
    
    def start(self):
        """Start load generation."""
        self.running = True
        delay = self.ramp_up / self.users if self.ramp_up > 0 else 0
        
        for i in range(self.users):
            thread = threading.Thread(
                target=self._user_session,
                args=(i,),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()
            if delay > 0:
                time.sleep(delay)
    
    def stop(self):
        """Stop load generation."""
        self.running = False
        for thread in self.threads:
            thread.join()
    
    def _user_session(self, user_id: int):
        """Simulate user session."""
        start_time = time.time()
        
        while self.running and time.time() - start_time < self.duration:
            try:
                metric = self._execute_with_metrics(
                    self.target,
                    context={'user_id': user_id}
                )
                self.metrics.append(metric)
            except Exception as e:
                logger.error(f"Error in user session {user_id}: {e}")
    
    def _execute_with_metrics(self, func: Callable, context: Dict[str, Any] = None) -> PerformanceMetric:
        """Execute function and collect metrics."""
        process = psutil.Process()
        
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        
        try:
            func()
        finally:
            end_time = time.time()
            end_memory = process.memory_info().rss
            end_cpu = process.cpu_percent()
            
            return PerformanceMetric(
                name=func.__name__,
                duration=end_time - start_time,
                memory_usage=end_memory - start_memory,
                cpu_usage=end_cpu - start_cpu,
                timestamp=datetime.now(),
                context=context
            )

class PerformanceTest:
    """Base class for performance tests."""
    
    def __init__(self, name: str):
        self.name = name
        self.metrics: List[PerformanceMetric] = []
    
    def setup(self):
        """Set up performance test."""
        pass
    
    def teardown(self):
        """Clean up performance test."""
        pass
    
    def execute(self, func: Callable, iterations: int = 1):
        """Execute test function with metrics collection."""
        self.setup()
        
        try:
            for _ in range(iterations):
                metric = self._execute_with_metrics(func)
                self.metrics.append(metric)
        finally:
            self.teardown()
    
    def _execute_with_metrics(self, func: Callable) -> PerformanceMetric:
        """Execute function and collect metrics."""
        process = psutil.Process()
        
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        
        try:
            func()
        finally:
            end_time = time.time()
            end_memory = process.memory_info().rss
            end_cpu = process.cpu_percent()
            
            return PerformanceMetric(
                name=self.name,
                duration=end_time - start_time,
                memory_usage=end_memory - start_memory,
                cpu_usage=end_cpu - start_cpu,
                timestamp=datetime.now()
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance test summary."""
        if not self.metrics:
            return {}
        
        durations = [m.duration for m in self.metrics]
        memory_usages = [m.memory_usage for m in self.metrics]
        cpu_usages = [m.cpu_usage for m in self.metrics]
        
        return {
            'name': self.name,
            'iterations': len(self.metrics),
            'duration': {
                'total': sum(durations),
                'mean': mean(durations),
                'median': median(durations),
                'std_dev': stdev(durations) if len(durations) > 1 else 0,
                'min': min(durations),
                'max': max(durations)
            },
            'memory': {
                'total': sum(memory_usages),
                'mean': mean(memory_usages),
                'median': median(memory_usages),
                'std_dev': stdev(memory_usages) if len(memory_usages) > 1 else 0,
                'min': min(memory_usages),
                'max': max(memory_usages)
            },
            'cpu': {
                'mean': mean(cpu_usages),
                'median': median(cpu_usages),
                'std_dev': stdev(cpu_usages) if len(cpu_usages) > 1 else 0,
                'min': min(cpu_usages),
                'max': max(cpu_usages)
            }
        }
    
    def generate_report(self, output_dir: Optional[str] = None):
        """Generate performance report."""
        if not output_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = TEST_REPORTS_DIR / f'performance_{timestamp}'
        
        summary = self.get_summary()
        
        # Generate plots
        self._generate_duration_plot(output_dir / 'duration.png')
        self._generate_memory_plot(output_dir / 'memory.png')
        self._generate_cpu_plot(output_dir / 'cpu.png')
        
        # Generate HTML report
        self._generate_html_report(output_dir / 'report.html', summary)
    
    def _generate_duration_plot(self, output_file: str):
        """Generate duration plot."""
        durations = [m.duration for m in self.metrics]
        timestamps = range(len(durations))
        
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, durations)
        plt.xlabel('Test Number')
        plt.ylabel('Duration (seconds)')
        plt.title('Test Duration Over Time')
        plt.savefig(output_file)
        plt.close()
    
    def _generate_memory_plot(self, output_file: str):
        """Generate memory usage plot."""
        memory_usages = [m.memory_usage / (1024 * 1024) for m in self.metrics]  # Convert to MB
        timestamps = range(len(memory_usages))
        
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, memory_usages)
        plt.xlabel('Test Number')
        plt.ylabel('Memory Usage (MB)')
        plt.title('Memory Usage Over Time')
        plt.savefig(output_file)
        plt.close()
    
    def _generate_cpu_plot(self, output_file: str):
        """Generate CPU usage plot."""
        cpu_usages = [m.cpu_usage for m in self.metrics]
        timestamps = range(len(cpu_usages))
        
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, cpu_usages)
        plt.xlabel('Test Number')
        plt.ylabel('CPU Usage (%)')
        plt.title('CPU Usage Over Time')
        plt.savefig(output_file)
        plt.close()
    
    def _generate_html_report(self, output_file: str, summary: Dict[str, Any]):
        """Generate HTML report."""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Test Report - {self.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ margin-bottom: 20px; }}
                .charts {{ display: flex; flex-wrap: wrap; gap: 20px; }}
                .chart {{ margin-bottom: 20px; }}
                .metrics {{ margin-top: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>Performance Test Report - {self.name}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Iterations: {summary['iterations']}</p>
                <h3>Duration</h3>
                <ul>
                    <li>Total: {summary['duration']['total']:.2f}s</li>
                    <li>Mean: {summary['duration']['mean']:.2f}s</li>
                    <li>Median: {summary['duration']['median']:.2f}s</li>
                    <li>Std Dev: {summary['duration']['std_dev']:.2f}s</li>
                    <li>Min: {summary['duration']['min']:.2f}s</li>
                    <li>Max: {summary['duration']['max']:.2f}s</li>
                </ul>
                <h3>Memory Usage</h3>
                <ul>
                    <li>Total: {summary['memory']['total'] / (1024 * 1024):.2f}MB</li>
                    <li>Mean: {summary['memory']['mean'] / (1024 * 1024):.2f}MB</li>
                    <li>Median: {summary['memory']['median'] / (1024 * 1024):.2f}MB</li>
                    <li>Std Dev: {summary['memory']['std_dev'] / (1024 * 1024):.2f}MB</li>
                    <li>Min: {summary['memory']['min'] / (1024 * 1024):.2f}MB</li>
                    <li>Max: {summary['memory']['max'] / (1024 * 1024):.2f}MB</li>
                </ul>
                <h3>CPU Usage</h3>
                <ul>
                    <li>Mean: {summary['cpu']['mean']:.2f}%</li>
                    <li>Median: {summary['cpu']['median']:.2f}%</li>
                    <li>Std Dev: {summary['cpu']['std_dev']:.2f}%</li>
                    <li>Min: {summary['cpu']['min']:.2f}%</li>
                    <li>Max: {summary['cpu']['max']:.2f}%</li>
                </ul>
            </div>
            
            <div class="charts">
                <div class="chart">
                    <h3>Duration Over Time</h3>
                    <img src="duration.png" alt="Duration Plot">
                </div>
                <div class="chart">
                    <h3>Memory Usage Over Time</h3>
                    <img src="memory.png" alt="Memory Usage Plot">
                </div>
                <div class="chart">
                    <h3>CPU Usage Over Time</h3>
                    <img src="cpu.png" alt="CPU Usage Plot">
                </div>
            </div>
        </body>
        </html>
        '''
        
        with open(output_file, 'w') as f:
            f.write(html_content)

def performance_test(iterations: int = 1):
    """Decorator for performance tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            test = PerformanceTest(func.__name__)
            test.execute(lambda: func(*args, **kwargs), iterations)
            test.generate_report()
            return func(*args, **kwargs)
        return wrapper
    return decorator
