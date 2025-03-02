"""Security testing utilities and vulnerability scanners."""

import re
import json
import hashlib
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class SecurityVulnerability:
    """Security vulnerability data."""
    type: str
    severity: str
    description: str
    location: str
    evidence: str
    recommendation: Optional[str] = None

class SecurityScanner:
    """Base security scanner."""
    
    def __init__(self):
        self.vulnerabilities: List[SecurityVulnerability] = []
    
    def scan(self, target: str):
        """Perform security scan."""
        raise NotImplementedError
    
    def report(self, output_file: Optional[str] = None):
        """Generate security report."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = TEST_REPORTS_DIR / f'security_{timestamp}.html'
        
        self._generate_html_report(output_file)
        logger.info(f"Security report generated: {output_file}")
    
    def _generate_html_report(self, output_file: str):
        """Generate HTML security report."""
        vulnerabilities_by_severity = {
            'Critical': [],
            'High': [],
            'Medium': [],
            'Low': [],
            'Info': []
        }
        
        for vuln in self.vulnerabilities:
            vulnerabilities_by_severity[vuln.severity].append(vuln)
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ margin-bottom: 20px; }}
                .vulnerability {{ margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; }}
                .Critical {{ border-left: 5px solid #dc3545; }}
                .High {{ border-left: 5px solid #fd7e14; }}
                .Medium {{ border-left: 5px solid #ffc107; }}
                .Low {{ border-left: 5px solid #28a745; }}
                .Info {{ border-left: 5px solid #17a2b8; }}
                .evidence {{ background-color: #f8f9fa; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Security Test Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Vulnerabilities: {len(self.vulnerabilities)}</p>
                <ul>
                    <li>Critical: {len(vulnerabilities_by_severity['Critical'])}</li>
                    <li>High: {len(vulnerabilities_by_severity['High'])}</li>
                    <li>Medium: {len(vulnerabilities_by_severity['Medium'])}</li>
                    <li>Low: {len(vulnerabilities_by_severity['Low'])}</li>
                    <li>Info: {len(vulnerabilities_by_severity['Info'])}</li>
                </ul>
            </div>
            
            <div class="vulnerabilities">
                {self._generate_vulnerability_sections(vulnerabilities_by_severity)}
            </div>
        </body>
        </html>
        '''
        
        with open(output_file, 'w') as f:
            f.write(html_content)
    
    def _generate_vulnerability_sections(self, vulns_by_severity: Dict[str, List[SecurityVulnerability]]) -> str:
        sections = []
        
        for severity in ['Critical', 'High', 'Medium', 'Low', 'Info']:
            vulns = vulns_by_severity[severity]
            if vulns:
                sections.append(f'''
                <h2>{severity} Vulnerabilities</h2>
                {''.join(self._generate_vulnerability_html(v) for v in vulns)}
                ''')
        
        return '\n'.join(sections)
    
    def _generate_vulnerability_html(self, vuln: SecurityVulnerability) -> str:
        return f'''
        <div class="vulnerability {vuln.severity}">
            <h3>{vuln.type}</h3>
            <p><strong>Location:</strong> {vuln.location}</p>
            <p>{vuln.description}</p>
            <div class="evidence">
                <strong>Evidence:</strong>
                <pre>{vuln.evidence}</pre>
            </div>
            {f'<p><strong>Recommendation:</strong> {vuln.recommendation}</p>' if vuln.recommendation else ''}
        </div>
        '''

class XSSScanner(SecurityScanner):
    """Cross-Site Scripting (XSS) vulnerability scanner."""
    
    def __init__(self):
        super().__init__()
        self.payloads = [
            '<script>alert("xss")</script>',
            '"><script>alert("xss")</script>',
            '<img src=x onerror=alert("xss")>',
            '<svg onload=alert("xss")>',
            'javascript:alert("xss")'
        ]
    
    def scan(self, target: str):
        """Scan for XSS vulnerabilities."""
        # Test form inputs
        soup = BeautifulSoup(requests.get(target).text, 'html.parser')
        for form in soup.find_all('form'):
            self._test_form(target, form)
        
        # Test URL parameters
        self._test_url_parameters(target)
    
    def _test_form(self, base_url: str, form):
        """Test form inputs for XSS."""
        action = urljoin(base_url, form.get('action', ''))
        method = form.get('method', 'get').lower()
        
        for input_field in form.find_all(['input', 'textarea']):
            field_name = input_field.get('name')
            if field_name:
                for payload in self.payloads:
                    data = {field_name: payload}
                    try:
                        if method == 'post':
                            response = requests.post(action, data=data)
                        else:
                            response = requests.get(action, params=data)
                        
                        if payload in response.text:
                            self.vulnerabilities.append(SecurityVulnerability(
                                type='Reflected XSS',
                                severity='High',
                                description=f'XSS vulnerability found in {method.upper()} parameter',
                                location=f'{action} - {field_name}',
                                evidence=payload,
                                recommendation='Implement proper input validation and output encoding'
                            ))
                    except:
                        continue
    
    def _test_url_parameters(self, url: str):
        """Test URL parameters for XSS."""
        parsed = urlparse(url)
        if parsed.query:
            params = dict(param.split('=') for param in parsed.query.split('&'))
            for param_name in params:
                for payload in self.payloads:
                    test_params = params.copy()
                    test_params[param_name] = payload
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?"
                    test_url += '&'.join(f"{k}={v}" for k, v in test_params.items())
                    
                    try:
                        response = requests.get(test_url)
                        if payload in response.text:
                            self.vulnerabilities.append(SecurityVulnerability(
                                type='Reflected XSS',
                                severity='High',
                                description='XSS vulnerability found in URL parameter',
                                location=f'{url} - {param_name}',
                                evidence=payload,
                                recommendation='Implement proper input validation and output encoding'
                            ))
                    except:
                        continue

class SQLInjectionScanner(SecurityScanner):
    """SQL Injection vulnerability scanner."""
    
    def __init__(self):
        super().__init__()
        self.payloads = [
            "' OR '1'='1",
            '" OR "1"="1',
            "1' OR '1'='1' --",
            "1\" OR \"1\"=\"1\" --",
            "' UNION SELECT NULL--",
            "admin' --"
        ]
    
    def scan(self, target: str):
        """Scan for SQL injection vulnerabilities."""
        # Test form inputs
        soup = BeautifulSoup(requests.get(target).text, 'html.parser')
        for form in soup.find_all('form'):
            self._test_form(target, form)
    
    def _test_form(self, base_url: str, form):
        """Test form inputs for SQL injection."""
        action = urljoin(base_url, form.get('action', ''))
        method = form.get('method', 'get').lower()
        
        for input_field in form.find_all(['input', 'textarea']):
            field_name = input_field.get('name')
            if field_name:
                for payload in self.payloads:
                    data = {field_name: payload}
                    try:
                        if method == 'post':
                            response = requests.post(action, data=data)
                        else:
                            response = requests.get(action, params=data)
                        
                        # Look for SQL error messages
                        if any(error in response.text.lower() for error in [
                            'sql syntax',
                            'mysql error',
                            'ora-',
                            'postgresql error'
                        ]):
                            self.vulnerabilities.append(SecurityVulnerability(
                                type='SQL Injection',
                                severity='Critical',
                                description=f'SQL injection vulnerability found in {method.upper()} parameter',
                                location=f'{action} - {field_name}',
                                evidence=payload,
                                recommendation='Use parameterized queries or prepared statements'
                            ))
                    except:
                        continue

class CSRFScanner(SecurityScanner):
    """Cross-Site Request Forgery (CSRF) vulnerability scanner."""
    
    def scan(self, target: str):
        """Scan for CSRF vulnerabilities."""
        try:
            # Check forms for CSRF tokens
            response = requests.get(target)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for form in soup.find_all('form'):
                if not self._has_csrf_protection(form):
                    self.vulnerabilities.append(SecurityVulnerability(
                        type='CSRF',
                        severity='High',
                        description='Form lacks CSRF protection',
                        location=f"{target} - {form.get('action', 'Unknown form')}",
                        evidence=str(form),
                        recommendation='Implement CSRF tokens in all forms'
                    ))
        except Exception as e:
            logger.error(f"Error scanning for CSRF vulnerabilities: {e}")
    
    def _has_csrf_protection(self, form) -> bool:
        """Check if form has CSRF protection."""
        # Look for common CSRF token field names
        csrf_fields = [
            'csrf_token',
            '_csrf_token',
            '_token',
            'csrfmiddlewaretoken'
        ]
        
        return any(
            form.find('input', {'name': field_name})
            for field_name in csrf_fields
        )

def security_test(target: str):
    """Run all security tests on target."""
    scanners = [
        XSSScanner(),
        SQLInjectionScanner(),
        CSRFScanner()
    ]
    
    for scanner in scanners:
        try:
            scanner.scan(target)
            scanner.report()
        except Exception as e:
            logger.error(f"Error running {scanner.__class__.__name__}: {e}")
    
    return [v for s in scanners for v in s.vulnerabilities]
