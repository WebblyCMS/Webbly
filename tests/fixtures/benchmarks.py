"""Performance testing utilities and benchmarks."""

import time
import cProfile
import pstats
import io
from functools import wraps
from contextlib import contextmanager
from typing import List, Dict, Any, Callable
from statistics import mean, median, stdev
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    """Benchmark result data class."""
    name: str
    iterations: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    std_dev: float
    median_time: float
    memory_usage: int = None
    cpu_usage: float = None

class Benchmark:
    """Benchmark utility class."""
    
    def __init__(self, name: str, iterations: int = 1000):
        self.name = name
        self.iterations = iterations
        self.times: List[float] = []
        self.memory_samples: List[int] = []
        self.cpu_samples: List[float] = []
    
    def run(self, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Run benchmark on a function."""
        import psutil
        process = psutil.Process()
        
        for _ in range(self.iterations):
            # Memory usage before
            mem_before = process.memory_info().rss
            cpu_before = process.cpu_percent()
            
            # Time the function
            start_time = time.perf_counter()
            func(*args, **kwargs)
            end_time = time.perf_counter()
            
            # Memory and CPU usage after
            mem_after = process.memory_info().rss
            cpu_after = process.cpu_percent()
            
            self.times.append(end_time - start_time)
            self.memory_samples.append(mem_after - mem_before)
            self.cpu_samples.append(cpu_after - cpu_before)
        
        return BenchmarkResult(
            name=self.name,
            iterations=self.iterations,
            total_time=sum(self.times),
            average_time=mean(self.times),
            min_time=min(self.times),
            max_time=max(self.times),
            std_dev=stdev(self.times) if len(self.times) > 1 else 0,
            median_time=median(self.times),
            memory_usage=mean(self.memory_samples),
            cpu_usage=mean(self.cpu_samples)
        )

def benchmark(name: str = None, iterations: int = 1000):
    """Decorator to benchmark a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            benchmark_name = name or func.__name__
            benchmark = Benchmark(benchmark_name, iterations)
            result = benchmark.run(func, *args, **kwargs)
            print(f"\nBenchmark: {result.name}")
            print(f"Iterations: {result.iterations}")
            print(f"Total time: {result.total_time:.6f}s")
            print(f"Average time: {result.average_time:.6f}s")
            print(f"Min time: {result.min_time:.6f}s")
            print(f"Max time: {result.max_time:.6f}s")
            print(f"Std dev: {result.std_dev:.6f}s")
            print(f"Median time: {result.median_time:.6f}s")
            if result.memory_usage:
                print(f"Average memory usage: {result.memory_usage / 1024:.2f}KB")
            if result.cpu_usage:
                print(f"Average CPU usage: {result.cpu_usage:.2f}%")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@contextmanager
def profile():
    """Context manager for profiling code."""
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())

class PerformanceTest:
    """Base class for performance tests."""
    
    def setup(self):
        """Set up test fixtures."""
        pass
    
    def teardown(self):
        """Clean up test fixtures."""
        pass
    
    def run_benchmark(self, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Run benchmark on a function."""
        self.setup()
        try:
            benchmark = Benchmark(func.__name__)
            return benchmark.run(func, *args, **kwargs)
        finally:
            self.teardown()

def assert_performance(result: BenchmarkResult, max_time: float = None, max_memory: int = None, max_cpu: float = None):
    """Assert performance constraints."""
    if max_time and result.average_time > max_time:
        raise AssertionError(
            f"Performance constraint violated: average time {result.average_time:.6f}s exceeds maximum {max_time:.6f}s"
        )
    if max_memory and result.memory_usage > max_memory:
        raise AssertionError(
            f"Performance constraint violated: memory usage {result.memory_usage}B exceeds maximum {max_memory}B"
        )
    if max_cpu and result.cpu_usage > max_cpu:
        raise AssertionError(
            f"Performance constraint violated: CPU usage {result.cpu_usage:.2f}% exceeds maximum {max_cpu:.2f}%"
        )

class MemoryProfiler:
    """Memory profiler utility."""
    
    def __init__(self):
        import tracemalloc
        self.tracemalloc = tracemalloc
    
    def start(self):
        """Start memory profiling."""
        self.tracemalloc.start()
    
    def stop(self):
        """Stop memory profiling."""
        self.tracemalloc.stop()
    
    def get_snapshot(self):
        """Get memory snapshot."""
        return self.tracemalloc.take_snapshot()
    
    def print_stats(self, snapshot, limit=10):
        """Print memory statistics."""
        stats = snapshot.statistics('lineno')
        print("\nTop %s memory allocations:" % limit)
        for stat in stats[:limit]:
            print(stat)

def time_function(func: Callable, *args, repeat: int = 3, number: int = 1000, **kwargs) -> Dict[str, Any]:
    """Time a function execution."""
    import timeit
    
    # Create timer
    timer = timeit.Timer(
        lambda: func(*args, **kwargs)
    )
    
    # Run timing
    times = timer.repeat(repeat=repeat, number=number)
    
    return {
        'best': min(times) / number,
        'worst': max(times) / number,
        'average': mean(times) / number,
        'total': sum(times),
        'repeat': repeat,
        'number': number
    }

@contextmanager
def measure_time(name: str = None):
    """Context manager to measure execution time."""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    duration = end - start
    if name:
        print(f"{name}: {duration:.6f}s")
    else:
        print(f"Time: {duration:.6f}s")

def compare_performance(funcs: List[Callable], *args, **kwargs) -> Dict[str, BenchmarkResult]:
    """Compare performance of multiple functions."""
    results = {}
    for func in funcs:
        benchmark = Benchmark(func.__name__)
        results[func.__name__] = benchmark.run(func, *args, **kwargs)
    return results

def print_comparison(results: Dict[str, BenchmarkResult]):
    """Print performance comparison results."""
    print("\nPerformance Comparison:")
    print("-" * 80)
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Average time: {result.average_time:.6f}s")
        print(f"  Memory usage: {result.memory_usage / 1024:.2f}KB")
        print(f"  CPU usage: {result.cpu_usage:.2f}%")
