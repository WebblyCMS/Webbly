"""Test statistics and metrics collection utilities."""

import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class TestMetric:
    """Test metric data."""
    name: str
    duration: float
    outcome: str
    timestamp: datetime
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    error: Optional[str] = None

class TestStatistics:
    """Test statistics collector and analyzer."""
    
    def __init__(self):
        self.metrics: List[TestMetric] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def start_session(self):
        """Start test session."""
        self.start_time = datetime.now()
    
    def end_session(self):
        """End test session."""
        self.end_time = datetime.now()
    
    def add_metric(self, metric: TestMetric):
        """Add test metric."""
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test statistics summary."""
        if not self.metrics:
            return {}
        
        total_tests = len(self.metrics)
        passed = sum(1 for m in self.metrics if m.outcome == 'passed')
        failed = sum(1 for m in self.metrics if m.outcome == 'failed')
        skipped = sum(1 for m in self.metrics if m.outcome == 'skipped')
        
        total_duration = sum(m.duration for m in self.metrics)
        avg_duration = total_duration / total_tests
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'avg_duration': avg_duration,
            'session_duration': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'slowest_tests': sorted(self.metrics, key=lambda m: m.duration, reverse=True)[:5],
            'most_memory': sorted(
                [m for m in self.metrics if m.memory_usage is not None],
                key=lambda m: m.memory_usage,
                reverse=True
            )[:5]
        }
    
    def generate_report(self, output_dir: Optional[str] = None):
        """Generate statistics report with visualizations."""
        if not output_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = TEST_REPORTS_DIR / f'statistics_{timestamp}'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        summary = self.get_summary()
        
        # Generate plots
        self._generate_outcome_pie_chart(output_dir / 'outcomes.png')
        self._generate_duration_histogram(output_dir / 'durations.png')
        self._generate_timeline(output_dir / 'timeline.png')
        if any(m.memory_usage for m in self.metrics):
            self._generate_memory_usage_plot(output_dir / 'memory.png')
        
        # Generate HTML report
        self._generate_html_report(output_dir / 'report.html', summary)
        
        logger.info(f"Statistics report generated in {output_dir}")
    
    def _generate_outcome_pie_chart(self, output_file: str):
        """Generate pie chart of test outcomes."""
        outcomes = defaultdict(int)
        for metric in self.metrics:
            outcomes[metric.outcome] += 1
        
        plt.figure(figsize=(8, 8))
        plt.pie(
            outcomes.values(),
            labels=outcomes.keys(),
            autopct='%1.1f%%',
            colors=['green', 'red', 'gray']
        )
        plt.title('Test Outcomes')
        plt.savefig(output_file)
        plt.close()
    
    def _generate_duration_histogram(self, output_file: str):
        """Generate histogram of test durations."""
        durations = [m.duration for m in self.metrics]
        
        plt.figure(figsize=(10, 6))
        plt.hist(durations, bins=30)
        plt.xlabel('Duration (seconds)')
        plt.ylabel('Number of Tests')
        plt.title('Test Duration Distribution')
        plt.savefig(output_file)
        plt.close()
    
    def _generate_timeline(self, output_file: str):
        """Generate timeline of test execution."""
        plt.figure(figsize=(12, 6))
        
        y_pos = np.arange(len(self.metrics))
        durations = [m.duration for m in self.metrics]
        colors = ['green' if m.outcome == 'passed' else 'red' if m.outcome == 'failed' else 'gray'
                 for m in self.metrics]
        
        plt.barh(y_pos, durations, color=colors)
        plt.yticks(y_pos, [m.name for m in self.metrics])
        plt.xlabel('Duration (seconds)')
        plt.title('Test Execution Timeline')
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
    
    def _generate_memory_usage_plot(self, output_file: str):
        """Generate memory usage plot."""
        memory_metrics = [m for m in self.metrics if m.memory_usage is not None]
        if not memory_metrics:
            return
        
        plt.figure(figsize=(10, 6))
        plt.plot(
            range(len(memory_metrics)),
            [m.memory_usage / (1024 * 1024) for m in memory_metrics]  # Convert to MB
        )
        plt.xlabel('Test Number')
        plt.ylabel('Memory Usage (MB)')
        plt.title('Memory Usage Over Time')
        plt.savefig(output_file)
        plt.close()
    
    def _generate_html_report(self, output_file: str, summary: Dict[str, Any]):
        """Generate HTML report."""
        memory_chart = '''
            <div class="chart">
                <h3>Memory Usage</h3>
                <img src="memory.png" alt="Memory Usage">
            </div>
        ''' if any(m.memory_usage for m in self.metrics) else ''
        
        metrics_rows = []
        for m in self.metrics:
            memory = f"{m.memory_usage / (1024 * 1024):.1f}MB" if m.memory_usage else 'N/A'
            cpu = f"{m.cpu_usage:.1f}%" if m.cpu_usage else 'N/A'
            metrics_rows.append(f'''
                <tr>
                    <td>{m.name}</td>
                    <td class="{m.outcome}">{m.outcome}</td>
                    <td>{m.duration:.2f}s</td>
                    <td>{memory}</td>
                    <td>{cpu}</td>
                </tr>
            ''')
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Statistics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ margin-bottom: 20px; }}
                .charts {{ display: flex; flex-wrap: wrap; gap: 20px; }}
                .chart {{ margin-bottom: 20px; }}
                .metrics {{ margin-top: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .skipped {{ color: gray; }}
            </style>
        </head>
        <body>
            <h1>Test Statistics Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {summary['total_tests']}</p>
                <p>Passed: <span class="passed">{summary['passed']}</span></p>
                <p>Failed: <span class="failed">{summary['failed']}</span></p>
                <p>Skipped: <span class="skipped">{summary['skipped']}</span></p>
                <p>Pass Rate: {summary['pass_rate']:.1f}%</p>
                <p>Total Duration: {summary['total_duration']:.2f}s</p>
                <p>Average Duration: {summary['avg_duration']:.2f}s</p>
                <p>Session Duration: {summary['session_duration']:.2f}s</p>
            </div>
            
            <div class="charts">
                <div class="chart">
                    <h3>Test Outcomes</h3>
                    <img src="outcomes.png" alt="Test Outcomes">
                </div>
                <div class="chart">
                    <h3>Duration Distribution</h3>
                    <img src="durations.png" alt="Duration Distribution">
                </div>
                <div class="chart">
                    <h3>Execution Timeline</h3>
                    <img src="timeline.png" alt="Execution Timeline">
                </div>
                {memory_chart}
            </div>
            
            <div class="metrics">
                <h2>Test Metrics</h2>
                <table>
                    <tr>
                        <th>Test</th>
                        <th>Outcome</th>
                        <th>Duration</th>
                        <th>Memory Usage</th>
                        <th>CPU Usage</th>
                    </tr>
                    {''.join(metrics_rows)}
                </table>
            </div>
        </body>
        </html>
        '''
        
        with open(output_file, 'w') as f:
            f.write(html_content)

# Global statistics instance
statistics = TestStatistics()

def track_test(func):
    """Decorator to track test metrics."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        start_cpu = psutil.Process().cpu_percent()
        
        try:
            result = func(*args, **kwargs)
            outcome = 'passed'
            error = None
        except Exception as e:
            outcome = 'failed'
            error = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            end_cpu = psutil.Process().cpu_percent()
            
            metric = TestMetric(
                name=func.__name__,
                duration=end_time - start_time,
                outcome=outcome,
                timestamp=datetime.now(),
                memory_usage=end_memory - start_memory,
                cpu_usage=end_cpu - start_cpu,
                error=error
            )
            statistics.add_metric(metric)
        
        return result
    
    return wrapper
