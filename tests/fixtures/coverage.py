"""Test coverage utilities and reporting."""

import os
import sys
import json
from typing import Dict, List, Set, Any
from pathlib import Path
from dataclasses import dataclass
from coverage import Coverage
from coverage.files import FnmatchMatcher
from coverage.report import get_analysis

@dataclass
class CoverageStats:
    """Coverage statistics for a module."""
    module: str
    statements: int
    missing: List[int]
    excluded: List[int]
    covered: int
    coverage: float

class CoverageReporter:
    """Custom coverage reporter."""
    
    def __init__(self, config_file='.coveragerc'):
        self.cov = Coverage(config_file=config_file)
        self.stats: Dict[str, CoverageStats] = {}
    
    def start(self):
        """Start coverage measurement."""
        self.cov.start()
    
    def stop(self):
        """Stop coverage measurement."""
        self.cov.stop()
    
    def save(self):
        """Save coverage data."""
        self.cov.save()
    
    def load(self):
        """Load coverage data."""
        self.cov.load()
    
    def analyze(self):
        """Analyze coverage data."""
        for filename in self.cov.get_data().measured_files():
            analysis = get_analysis(filename)
            module = os.path.relpath(filename)
            
            statements = len(analysis.statements)
            missing = sorted(analysis.missing)
            excluded = sorted(analysis.excluded)
            covered = statements - len(missing)
            coverage = (covered / statements * 100) if statements else 0
            
            self.stats[module] = CoverageStats(
                module=module,
                statements=statements,
                missing=missing,
                excluded=excluded,
                covered=covered,
                coverage=coverage
            )
    
    def report(self, show_missing=True):
        """Generate coverage report."""
        total_statements = sum(s.statements for s in self.stats.values())
        total_covered = sum(s.covered for s in self.stats.values())
        total_coverage = (total_covered / total_statements * 100) if total_statements else 0
        
        print("\nCoverage Report")
        print("=" * 80)
        print(f"Total Coverage: {total_coverage:.2f}%")
        print(f"Statements: {total_statements}")
        print(f"Covered: {total_covered}")
        print(f"Missing: {total_statements - total_covered}")
        print("-" * 80)
        
        for module, stats in sorted(self.stats.items()):
            print(f"\n{module}")
            print(f"Coverage: {stats.coverage:.2f}%")
            print(f"Statements: {stats.statements}")
            print(f"Covered: {stats.covered}")
            if show_missing and stats.missing:
                print(f"Missing lines: {stats.missing}")
    
    def html_report(self, directory='htmlcov'):
        """Generate HTML coverage report."""
        self.cov.html_report(directory=directory)
        print(f"\nHTML coverage report generated in {directory}")
    
    def xml_report(self, outfile='coverage.xml'):
        """Generate XML coverage report."""
        self.cov.xml_report(outfile=outfile)
        print(f"\nXML coverage report generated: {outfile}")
    
    def json_report(self, outfile='coverage.json'):
        """Generate JSON coverage report."""
        data = {
            'summary': {
                'total_statements': sum(s.statements for s in self.stats.values()),
                'total_covered': sum(s.covered for s in self.stats.values()),
                'total_coverage': (sum(s.covered for s in self.stats.values()) / 
                                 sum(s.statements for s in self.stats.values()) * 100)
                if sum(s.statements for s in self.stats.values()) else 0
            },
            'modules': {
                module: {
                    'statements': stats.statements,
                    'covered': stats.covered,
                    'coverage': stats.coverage,
                    'missing': stats.missing
                }
                for module, stats in self.stats.items()
            }
        }
        
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nJSON coverage report generated: {outfile}")

class CoverageConfig:
    """Coverage configuration helper."""
    
    def __init__(self, config_file='.coveragerc'):
        self.config_file = config_file
        self.config = {
            'run': {
                'branch': True,
                'source': ['webbly'],
                'omit': [
                    '*/tests/*',
                    '*/migrations/*',
                    '*/venv/*'
                ]
            },
            'report': {
                'exclude_lines': [
                    'pragma: no cover',
                    'def __repr__',
                    'raise NotImplementedError',
                    'if __name__ == .__main__.:',
                    'pass'
                ],
                'ignore_errors': True,
                'skip_covered': False
            },
            'html': {
                'directory': 'htmlcov',
                'title': 'Webbly CMS Coverage Report'
            }
        }
    
    def save(self):
        """Save coverage configuration."""
        import configparser
        config = configparser.ConfigParser()
        
        for section, options in self.config.items():
            config[section] = {
                key: str(value) if not isinstance(value, (list, set))
                else '\n'.join(value)
                for key, value in options.items()
            }
        
        with open(self.config_file, 'w') as f:
            config.write(f)

def setup_coverage():
    """Set up coverage measurement."""
    config = CoverageConfig()
    config.save()
    return CoverageReporter(config.config_file)

def pytest_configure(config):
    """Configure pytest with coverage."""
    if config.option.cov:
        config.coverage = setup_coverage()
        config.coverage.start()

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add coverage report to test summary."""
    if hasattr(config, 'coverage'):
        config.coverage.stop()
        config.coverage.save()
        config.coverage.load()
        config.coverage.analyze()
        config.coverage.report()
        
        if config.option.cov_html:
            config.coverage.html_report()
        if config.option.cov_xml:
            config.coverage.xml_report()
        if config.option.cov_json:
            config.coverage.json_report()

def get_uncovered_lines(module: str) -> Set[int]:
    """Get uncovered lines for a module."""
    cov = Coverage()
    cov.load()
    analysis = get_analysis(module)
    return set(analysis.missing)

def is_line_covered(module: str, line: int) -> bool:
    """Check if a specific line is covered."""
    return line not in get_uncovered_lines(module)
