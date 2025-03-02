#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import coverage
from datetime import datetime

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Webbly CMS tests')
    
    # Test selection
    parser.add_argument('-m', '--marker', 
                       help='Only run tests with this marker')
    parser.add_argument('-k', '--keyword', 
                       help='Only run tests matching this keyword expression')
    parser.add_argument('-f', '--file', 
                       help='Run tests from a specific file')
    
    # Test execution options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal output')
    parser.add_argument('--failfast', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--parallel', '-n', type=int, metavar='N',
                       help='Run N tests in parallel')
    
    # Coverage options
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run tests with coverage')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML coverage report')
    parser.add_argument('--xml', action='store_true',
                       help='Generate XML coverage report')
    
    # Report options
    parser.add_argument('--report', '-r', action='store_true',
                       help='Generate test report')
    parser.add_argument('--report-dir', default='test-reports',
                       help='Directory for test reports')
    
    # Environment options
    parser.add_argument('--env', '-e', 
                       choices=['dev', 'test', 'prod'],
                       default='test',
                       help='Environment to run tests in')
    
    return parser.parse_args()

def setup_environment(env):
    """Set up test environment."""
    os.environ['FLASK_ENV'] = env
    os.environ['FLASK_TESTING'] = 'true'
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(__file__))
    
    # Create necessary directories
    dirs = ['logs', 'coverage', 'test-reports']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def build_pytest_command(args):
    """Build pytest command from arguments."""
    cmd = ['pytest']
    
    # Test selection
    if args.marker:
        cmd.extend(['-m', args.marker])
    if args.keyword:
        cmd.extend(['-k', args.keyword])
    if args.file:
        cmd.append(args.file)
    
    # Test execution options
    if args.verbose:
        cmd.append('-v')
    if args.quiet:
        cmd.append('-q')
    if args.failfast:
        cmd.append('--exitfirst')
    if args.parallel:
        cmd.extend(['-n', str(args.parallel)])
    
    # Coverage options
    if args.coverage:
        cmd.extend(['--cov=webbly', '--cov-report=term-missing'])
        if args.html:
            cmd.append('--cov-report=html:coverage/html')
        if args.xml:
            cmd.append('--cov-report=xml:coverage/coverage.xml')
    
    # Report options
    if args.report:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(args.report_dir, f'report_{timestamp}.html')
        cmd.extend(['--html', report_path])
    
    return cmd

def run_tests(cmd):
    """Run tests with given command."""
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def run_linting():
    """Run code quality checks."""
    print("\nRunning code quality checks...")
    
    # Run flake8
    print("\nRunning flake8...")
    subprocess.run(['flake8', 'webbly', 'tests'])
    
    # Run black
    print("\nRunning black...")
    subprocess.run(['black', '--check', 'webbly', 'tests'])
    
    # Run isort
    print("\nRunning isort...")
    subprocess.run(['isort', '--check-only', 'webbly', 'tests'])
    
    # Run mypy
    print("\nRunning mypy...")
    subprocess.run(['mypy', 'webbly'])
    
    # Run pylint
    print("\nRunning pylint...")
    subprocess.run(['pylint', 'webbly', 'tests'])

def run_security_checks():
    """Run security checks."""
    print("\nRunning security checks...")
    
    # Run bandit
    print("\nRunning bandit...")
    subprocess.run(['bandit', '-r', 'webbly'])
    
    # Run safety
    print("\nRunning safety...")
    subprocess.run(['safety', 'check'])

def generate_reports(args):
    """Generate test reports."""
    if args.coverage and args.html:
        print("\nGenerating coverage report...")
        cov = coverage.Coverage()
        cov.load()
        cov.html_report(directory='coverage/html')
    
    if args.report:
        print(f"\nTest report generated at {args.report_dir}")

def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup
    setup_environment(args.env)
    
    # Build and run test command
    cmd = build_pytest_command(args)
    print(f"\nRunning tests with command: {' '.join(cmd)}")
    run_tests(cmd)
    
    # Additional checks
    if args.env == 'test':
        run_linting()
        run_security_checks()
    
    # Generate reports
    generate_reports(args)
    
    print("\nAll tests completed successfully!")

if __name__ == '__main__':
    main()
