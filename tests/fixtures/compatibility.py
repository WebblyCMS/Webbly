"""Cross-browser and cross-platform testing utilities."""

import os
import sys
import platform
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class BrowserConfig:
    """Browser configuration data."""
    name: str
    version: str
    platform: str
    driver_options: Dict[str, Any] = None

@dataclass
class CompatibilityResult:
    """Compatibility test result data."""
    browser: str
    platform: str
    status: str
    error: Optional[str] = None
    screenshot: Optional[str] = None

class BrowserTestManager:
    """Cross-browser test manager."""
    
    def __init__(self):
        self.browsers: Dict[str, webdriver.Remote] = {}
        self.results: List[CompatibilityResult] = []
    
    def setup_browser(self, config: BrowserConfig) -> webdriver.Remote:
        """Set up browser for testing."""
        try:
            if config.name.lower() == 'chrome':
                options = webdriver.ChromeOptions()
            elif config.name.lower() == 'firefox':
                options = webdriver.FirefoxOptions()
            elif config.name.lower() == 'safari':
                options = webdriver.SafariOptions()
            elif config.name.lower() == 'edge':
                options = webdriver.EdgeOptions()
            else:
                raise ValueError(f"Unsupported browser: {config.name}")
            
            # Apply custom options
            if config.driver_options:
                for key, value in config.driver_options.items():
                    options.set_capability(key, value)
            
            driver = webdriver.Remote(
                command_executor='http://localhost:4444/wd/hub',
                options=options
            )
            
            self.browsers[config.name] = driver
            return driver
        
        except Exception as e:
            logger.error(f"Failed to set up browser {config.name}: {e}")
            raise
    
    def teardown_browser(self, browser_name: str):
        """Clean up browser after testing."""
        if browser_name in self.browsers:
            try:
                self.browsers[browser_name].quit()
                del self.browsers[browser_name]
            except Exception as e:
                logger.error(f"Failed to tear down browser {browser_name}: {e}")
    
    def run_test(self, url: str, test_func, configs: List[BrowserConfig]):
        """Run test across multiple browsers."""
        for config in configs:
            try:
                driver = self.setup_browser(config)
                driver.get(url)
                
                result = test_func(driver)
                screenshot = self._take_screenshot(driver, config)
                
                self.results.append(CompatibilityResult(
                    browser=config.name,
                    platform=config.platform,
                    status='passed',
                    screenshot=screenshot
                ))
            
            except Exception as e:
                self.results.append(CompatibilityResult(
                    browser=config.name,
                    platform=config.platform,
                    status='failed',
                    error=str(e)
                ))
            
            finally:
                self.teardown_browser(config.name)
    
    def _take_screenshot(self, driver: webdriver.Remote, config: BrowserConfig) -> str:
        """Take browser screenshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{config.name}_{timestamp}.png"
        filepath = TEST_REPORTS_DIR / 'screenshots' / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        driver.save_screenshot(str(filepath))
        return str(filepath)
    
    def generate_report(self, output_file: Optional[str] = None):
        """Generate compatibility test report."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = TEST_REPORTS_DIR / f'compatibility_{timestamp}.html'
        
        self._generate_html_report(output_file)
        logger.info(f"Compatibility report generated: {output_file}")
    
    def _generate_html_report(self, output_file: str):
        """Generate HTML compatibility report."""
        results_by_status = {
            'passed': [],
            'failed': []
        }
        
        for result in self.results:
            results_by_status[result.status].append(result)
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cross-Browser Compatibility Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ margin-bottom: 20px; }}
                .result {{ margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; }}
                .passed {{ border-left: 5px solid #28a745; }}
                .failed {{ border-left: 5px solid #dc3545; }}
                .screenshot {{ max-width: 800px; margin: 10px 0; }}
                .error {{ background-color: #f8d7da; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Cross-Browser Compatibility Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {len(self.results)}</p>
                <p>Passed: {len(results_by_status['passed'])}</p>
                <p>Failed: {len(results_by_status['failed'])}</p>
            </div>
            
            <div class="results">
                <h2>Test Results</h2>
                {self._generate_result_sections(results_by_status)}
            </div>
        </body>
        </html>
        '''
        
        with open(output_file, 'w') as f:
            f.write(html_content)
    
    def _generate_result_sections(self, results_by_status: Dict[str, List[CompatibilityResult]]) -> str:
        sections = []
        
        for status in ['passed', 'failed']:
            results = results_by_status[status]
            if results:
                sections.append(f'''
                <h3>{status.title()} Tests</h3>
                {''.join(self._generate_result_html(r) for r in results)}
                ''')
        
        return '\n'.join(sections)
    
    def _generate_result_html(self, result: CompatibilityResult) -> str:
        return f'''
        <div class="result {result.status}">
            <h4>{result.browser} ({result.platform})</h4>
            <p>Status: {result.status}</p>
            {f'<div class="error">Error: {result.error}</div>' if result.error else ''}
            {f'<img class="screenshot" src="{result.screenshot}" alt="Screenshot">' if result.screenshot else ''}
        </div>
        '''

class PlatformTestManager:
    """Cross-platform test manager."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.python_version = sys.version_info
    
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self.platform == 'windows'
    
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self.platform == 'linux'
    
    def is_mac(self) -> bool:
        """Check if running on macOS."""
        return self.platform == 'darwin'
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get detailed platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': '.'.join(map(str, self.python_version[:3]))
        }
    
    def skip_if_platform(self, platforms: List[str]):
        """Decorator to skip test on specific platforms."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.platform in platforms:
                    pytest.skip(f"Test not supported on {self.platform}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def run_if_platform(self, platforms: List[str]):
        """Decorator to run test only on specific platforms."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.platform not in platforms:
                    pytest.skip(f"Test only runs on {', '.join(platforms)}")
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Default browser configurations
BROWSER_CONFIGS = [
    BrowserConfig(
        name='Chrome',
        version='latest',
        platform='Windows 10',
        driver_options={'headless': True}
    ),
    BrowserConfig(
        name='Firefox',
        version='latest',
        platform='Windows 10',
        driver_options={'headless': True}
    ),
    BrowserConfig(
        name='Edge',
        version='latest',
        platform='Windows 10',
        driver_options={'headless': True}
    )
]

# Global instances
browser_manager = BrowserTestManager()
platform_manager = PlatformTestManager()
